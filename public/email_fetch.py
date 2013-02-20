import time
import urllib
import json
import os
import logging
import base64
import imaplib
import email
import re
import random
from collections import Counter
#import traceback
#import StringIO
from rq import Queue
import mmstats
from bs4 import BeautifulSoup

from datetime import datetime
from public.static_data import REDIRECT_URI, GOOGLE_ACCOUNTS_BASE_URL
from public.static_data import TEST_GOOGLE_REPLY, OK, FAIL, YIELD
from public.static_data import TEST_EMAIL_TEMPLATE
from public.models import WordUse, Word, WordsToLearn, InterestingEmail

import django.utils.timezone
from pprint import pformat
import string
from worker import conn

logger = logging.getLogger(__name__)
SEP_MATCHER = re.compile('On \S*, .* wrote:')
DISQUALIFIERS = string.digits + '`~!@#$%^&*()_=+{[}]\|";:<,.>/?'
MAX_TO_PROCESS = 10


class EmailStats(mmstats.MmStats):
    imap_timer = mmstats.TimerField()
    fetch_timer = mmstats.TimerField()
    process_timer = mmstats.TimerField()
    analytic_timer1 = mmstats.TimerField()
    analytic_timer1a = mmstats.TimerField()
    analytic_timer2 = mmstats.TimerField()
    analytic_timer2a = mmstats.TimerField()
    analytic_timer3 = mmstats.TimerField()
    word_processing_timer = mmstats.TimerField()
    word_use_save = mmstats.TimerField()
    #cleanup_timer = mmstats.TimerField()
    #save_timer = mmstats.TimerField()
    #wait_for_prompt_timer = mmstats.TimerField(label="wait_for_prompt")
    #line_timeout_counter = mmstats.CounterField(label="line_timeout")
    #test_counter = mmstats.CounterField(label="test_counter")
    #to_router_counter = mmstats.CounterField(label="to_router")


stats = EmailStats(
    label_prefix='email.stats.'
)


def _get_object_or_dict(word_candidate):
    """Get an object or None"""
    word_object = None
    try:
        word_object = Word.objects.get(word__exact=word_candidate)
    except Word.DoesNotExist:
        pass
    return word_object


def _get_word_object(new_word):
    """
    Figure out capitalization and return a word object
    """
    word_object = _get_object_or_dict(new_word)
    if not word_object:
        new_word = new_word.lower()
        word_object = _get_object_or_dict(new_word)
        if not word_object:
            new_word = new_word.capitalize()
            word_object = _get_object_or_dict(new_word)
            if not word_object:
                return None

    if new_word.endswith("'s"):
        new_word = new_word[:-2]
        word_object = _get_object_or_dict(new_word)
        if not word_object:
            msg = "(%s) is NOT a dictionary word but (%s's) is?"
            logger.info(msg % (new_word, new_word))
            return None
    return word_object


def cleanup(new_word):
    """
    We have been given a word with potentially a bunch of punctuation
    and stuff around it. Let's clean it up.
    """
    found = True
    while found and new_word:
        found = False
        if new_word[0] in string.punctuation:
            new_word = new_word[1:]
            found = True
        if len(new_word) == 0:
            break
        if new_word[-1] in string.punctuation:
            new_word = new_word[:-1]
            found = True
    if any([letter in DISQUALIFIERS for letter in new_word]):
        return None

    return _get_word_object(new_word)


def _get_accounts_url(command):
    """Generates the Google Accounts URL."""
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def log_object(object, title=''):
    "Logs an entire object to the log"
    logger.info("===START==========================%s" % title.upper())
    for line in pformat(object).split('\n'):
        logger.info(line)
    logger.info("===FINISH=========================%s" % title.upper())


def _get_auth_token(authorization_code):
    """
    Go ask google for an access token for this user instead of
    just an authorization code.
    """
    if os.environ.get("ENV") == 'dev':
        return TEST_GOOGLE_REPLY

    params = {}
    params['client_id'] = os.environ['GOOGLE_CLIENT_ID']
    params['client_secret'] = os.environ['GOOGLE_CLIENT_SECRET']
    params['code'] = authorization_code
    params['redirect_uri'] = REDIRECT_URI
    params['grant_type'] = 'authorization_code'
    request_url = _get_accounts_url('o/oauth2/token')

    return json.loads(
        urllib.urlopen(request_url, urllib.urlencode(params)).read())


class EmailProcessingException(Exception):

    def __init__(self, message_string):
        super(EmailProcessingException, self).__init__()
        logger.error("Error processing message. Writing to database.")
        self.message_string = message_string
        interesting_email = InterestingEmail(text=message_string)
        try:
            interesting_email.save()
        except Exception:
            logger.error("could not save email. For further analysis.")
            logger.error("Here it is:")
            for line in message_string.split('\n'):
                logger.info(">> %s" % line)

    def __unicode__(self):
        if len(self.message_string) > 10:
            return "Sample: '%s...'" % self.message_string[:10]
        else:
            return "Sample: '%s'" % self.message_string

    def __repr__(self):
        return self.__unicode__(self)


class FakeImapConn(object):
    """
    Sometimes we need to be able to test our system
    without having to talk to Google.
    """

    MSG_COUNT = 10

    def __init__(self, profile):
        # We store the profile so we can know what message
        # numbers to send.
        self.profile = profile

    def authenticate(self, _mechanism, authobject):
        return

    def select(self, _mailbox, readonly):
        last = self.profile.last_message_processed
        return "OK", [last + self.MSG_COUNT]

    def search(self, _charset, _criterion):
        last = self.profile.last_message_processed
        msg_data = ' '.join([str(x) for x in xrange(1, last+self.MSG_COUNT)])
        return "OK", [msg_data]

    def fetch(self, message_set, message_parts):
        count = Word.objects.all().count()
        indexes = [random.randrange(0, count) for x in xrange(0, 100)]
        message_body = ' '.join([Word.objects.get(pk=x).word for x in indexes])
        fake_message = TEST_EMAIL_TEMPLATE % message_body
        return "OK", [['', fake_message]]

    def close(self):
        pass

    def logout(self):
        pass


class Analytics(object):

    def __init__(self, user, message, word_use_dict, to=None, sent=None):
        self.user = user
        self.message = message
        self.to = to
        self.word_use_dict = word_use_dict
        if not self.to:
            self.to = self.message.get('To')
            if not self.to:
                self.to = "UNKNOWN"
        if len(self.to) >= 100:
            logger.warning("Invalid send-to-value: (%s)" % self.to)
            self.to = "UNKNOWN"
        self.sent = sent
        if not self.sent:
            sent_time = time.mktime(
                email.utils.parsedate(self.message["Date"]))
            self.sent = datetime.fromtimestamp(sent_time)
            if not django.utils.timezone.is_aware(self.sent):
                self.sent = django.utils.timezone.make_aware(
                    self.sent, django.utils.timezone.get_default_timezone())

        self.sent_words = []

    def _process_payload(self, payload):
        """
        We have a payload come in and we need to pull words out of it.
        """
        for line in payload.split('\n'):
            if SEP_MATCHER.findall(line):
                break
            self.sent_words += line.split()

        for new_word, count in Counter(self.sent_words).items():
            with stats.word_processing_timer:
                word_object = None
                with stats.analytic_timer1:
                    word_object = cleanup(new_word)
                if word_object is None or word_object.word == '':
                    continue

                with stats.analytic_timer1a:
                    word_use = self.word_use_dict.get(word_object.word)
                    try:
                        word_use = WordUse.objects.get(word__exact=word_object)
                        self.word_use_dict[word_object.word] = word_use
                    except WordUse.DoesNotExist:
                        word_use = WordUse(word=word_object)
                        self.word_use_dict[word_object.word] = word_use
                        word_use.times_used = 0
                    except WordUse.DatabaseError as dbe:
                        logger.error('dbe: %s' % dbe)
                        log_object(dir(dbe), 'dir(dbe)')

                self.word_use_dict[word_object.word].times_used += count
                self.word_use_dict[word_object.word].last_time_used = self.sent
                self.word_use_dict[word_object.word].last_sent_to = self.to
                self.word_use_dict[word_object.word].user = self.user
                self.word_use_dict[word_object.word].word = word_object
                try:
                    with stats.analytic_timer2a:
                        word_to_learn = WordsToLearn.objects.get(
                            user__id=self.user.id, word__exact=word_object)
                        word_to_learn.date_completed = datetime.utcnow()
                        word_to_learn.save()
                        msg = "Marking success on word used: %s!"
                        logger.info(msg % word_object)
                except WordsToLearn.DoesNotExist:
                    pass

    def process_message(self):
        self.sent_text = ''
        payload = self.message.get_payload()
        content_type = self.message.get_content_type()
        if self.message.is_multipart():
            for message in payload:
                if isinstance(message, email.message.Message):
                    analytics = Analytics(
                        self.user, message, self.word_use_dict,
                        to=self.to, sent=self.sent)
                    analytics.process_message()
        else:
            if content_type == "image/jpeg":
                pass
            elif content_type == "text/html":
                with stats.analytic_timer3:
                    self._process_payload(
                        BeautifulSoup(payload).get_text())
            elif content_type == "text/plain":
                with stats.analytic_timer3:
                    self._process_payload(payload)
            else:
                msg = "Ignoring invalid content-type: %s"
                logger.warning(msg % content_type)


class EmailAnalyzer(object):

    def __init__(self, user):
        self.user = user
        self.profile = self.user.get_profile()
        self.word_use_dict = {}

    def _fetch_sent_messages(self, auth_string):
        """
        Authenticates to IMAP with the given auth_string.

        Prints a debug trace of the attempted IMAP connection.

        Args:
            auth_string: A valid OAuth2 string, as returned by
                generate_oath2_string. Must not be base64-encoded,
                since imaplib does its own base64-encoding.
        """
        status = OK
        imap_conn = None
        if os.environ['ENV'] == 'dev':
            imap_conn = FakeImapConn(self.profile)
        else:
            imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')

        with stats.imap_timer:
            #imap_conn.debug = 4
            imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
            #try:
            #    list_output = imap_conn.list()
            #    log_object(list_output, 'LIST OUTPUT')
            #except Exception as exp:
            #    logger.info("LIST failed: %s" % exp)

            select_status, msg_data = imap_conn.select(
                "[Gmail]/Sent Mail", readonly=True)  # TESTING readonly
            if select_status != "OK":
                msg = "Invalid status recieved when selecting: %s"
                logger.error(msg % select_status)
                return FAIL
            try:
                self.profile.last_message_on_server = int(msg_data[0])
            except Exception as exp:
                logger.error("Unable to determine final message: %s" % exp)
                return FAIL

            _result, message_data = imap_conn.search(None, 'ALL')
            message_numbers = message_data[0]
            message_count = 0

        for num in message_numbers.split():
            if int(num) < self.profile.last_message_processed:
                #logger.info("Skipping message we've processed: %s" % num)
                continue
            message_string = ''
            with stats.fetch_timer:
                _result, data = imap_conn.fetch(num, '(RFC822)')
                msg = 'Processing message %s for %s' % (num, self.user.email)
                logger.info(msg)
                self.profile.last_message_processed = int(num)
                self.profile.save()
                message_string = data[0][1]
            message = email.message_from_string(message_string)
            analytics = Analytics(self.user, message, self.word_use_dict)
            try:
                with stats.process_timer:
                    analytics.process_message()
            except Exception as exp:
                raise EmailProcessingException(message_string)
            message_count += 1
            if message_count > MAX_TO_PROCESS:
                msg = '<== Limiting new messages to %s' % MAX_TO_PROCESS
                logger.info(msg)
                status = YIELD
                break
        imap_conn.close()
        imap_conn.logout()
        self.profile.save()  # We need to record the message_id we last touched
        self._save_word_use()
        return status

    def _save_word_use(self):
        """Save all our word_use items"""
        start_time = time.time()
        msg = "Saving %d word use items..."
        logger.info(msg % len(self.word_use_dict.keys()))
        with stats.word_use_save:
            for key, word_use in self.word_use_dict.items():
                word_use.save()
        logger.info("Finished save (%s seconds)." % time.time() - start_time)

    def _fetch_access_token(self):
        """
        We're going to go ask google if we can have a temporary access-token
        """
        code = self.profile.code
        if not code:
            logger.info('User has no code from Google.')
            return FAIL
        if self.profile.token_is_current():
            msg = "User has a current access_token. No need to get a new one"
            logger.info(msg)
            return OK

        server_response = _get_auth_token(code)
        error = server_response.get("error")
        if error:
            logger.error('Error returned from the server (%s)' % error)
            return FAIL

        code = server_response.get('code')
        access_token = server_response.get('access_token')
        try:
            expires_in = int(server_response.get('expires_in'))
            token_expiration = datetime.fromtimestamp(
                expires_in + time.time())
            utc_exp = django.utils.timezone.make_aware(
                token_expiration, django.utils.timezone.get_default_timezone())
            logger.info("token_expiration: (%s)" % utc_exp)
            self.profile.token_expiration = utc_exp
        except ValueError as exp:
            expires_in = server_response.get('expires_in')
            logger.error("Exception: %s" % exp)
            logger.error("Error converting expiration %s" % expires_in)
        token_type = server_response.get('token_type')
        id_token = server_response.get('id_token')
        self.profile.access_token = access_token
        self.profile.token_type = token_type
        self.profile.id_token = id_token
        self.profile.save()
        return OK

    def _generate_oauth2_string(self, base64_encode=True):
        """
        Generates an IMAP OAuth2 authentication string.

        See https://developers.google.com/google-apps/gmail/oauth2_overview

        Args:
          username: the username (email address) of the account to authenticate
          access_token: An OAuth2 access token.
          base64_encode: Whether to base64-encode the output.

        Returns:
          The SASL argument for the OAuth2 mechanism.
        """
        auth_string = 'user=%s\1auth=Bearer %s\1\1'
        auth_string %= (self.user.email, self.profile.access_token)
        if base64_encode:
            auth_string = base64.b64encode(auth_string)
        return auth_string

    def process(self):
        """
        Main entry point for email processing. Make sure we have rights,
        grab some emails and process them.
        """
        status = FAIL
        try:
            if self._fetch_access_token() == OK:
                creds = self._generate_oauth2_string(base64_encode=False)
                status = self._fetch_sent_messages(creds)
            else:
                logger.error("Unable to obtain access token. Aborting import")
        except EmailProcessingException:
            logger.info("Encountered email we can't process. Skipping.")
            status = YIELD
        if status == YIELD:
            q = Queue(connection=conn)
            logger.info("Queuing another job in EmailAnalyzer")
            q.enqueue(self.process)
        return status

#SDG
