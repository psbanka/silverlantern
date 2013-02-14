import time
import urllib
import json
import os
import logging
import base64
import imaplib
import email
import re
from collections import Counter
import traceback
import StringIO
from rq import Queue

from datetime import datetime
from public.static_data import REDIRECT_URI, GOOGLE_ACCOUNTS_BASE_URL
from public.static_data import TEST_GOOGLE_REPLY, OK, FAIL, YIELD
from public.static_data import TEST_EMAIL1, TEST_EMAIL2
from public.models import WordUse, Word, WordsToLearn

import django.utils.timezone
from pprint import pformat
import string
from worker import conn

logger = logging.getLogger(__name__)
SEP_MATCHER = re.compile('On \S*, .* wrote:')
DISQUALIFIERS = string.digits + '`~!@#$%^&*()_=+{[}]\|";:<,.>/?'
MAX_TO_PROCESS = 10


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
        return ''
    try:
        Word.objects.get(word__exact=new_word)
    except Word.DoesNotExist:
        new_word = new_word.lower()
        try:
            Word.objects.get(word__exact=new_word)
        except Word.DoesNotExist:
            new_word = new_word.capitalize()
            try:
                Word.objects.get(word__exact=new_word)
            except Word.DoesNotExist:
                logger.info("(%s) is NOT a dictionary word" % new_word)
                return ''
    return new_word


def _get_accounts_url(command):
    """Generates the Google Accounts URL.

    Args:
      command: The command to execute.

    Returns:
      A URL for the given command.
    """
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


class Analytics(object):

    def __init__(self, user, message_string):
        self.user = user
        self.message = email.message_from_string(message_string)
        self.to = self.message.get('To')
        logger.info("DATE: (%s)" % self.message["Date"])
        sent_time = time.mktime(email.utils.parsedate(self.message["Date"]))
        self.sent = datetime.fromtimestamp(sent_time)
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
            new_word = cleanup(new_word)
            if not new_word:
                continue
            try:
                word_use = WordUse.objects.get(word__exact=new_word)
            except WordUse.DoesNotExist:
                word_use = WordUse(word=new_word)
                word_use.times_used = 0

            word_use.times_used += count
            word_use.last_time_used = self.sent
            word_use.last_sent_to = self.to
            word_use.user = self.user
            word_use.save()
            try:
                word_to_learn = WordsToLearn.objects.get(
                    user__id=self.user.id, word__exact=new_word)
                word_to_learn.date_completed = datetime.utcnow()
                logger.info("Marking success on word used: %s!" % new_word)
            except WordsToLearn.DoesNotExist:
                pass

    def process_message(self):
        self.sent_text = ''
        payload = self.message.get_payload()
        if isinstance(payload, list):
            for hunk in payload:
                log_object(hunk, "PAYLOAD hunk")
                self._process_payload(hunk)
        else:
            self._process_payload(payload)


class EmailAnalyzer(object):

    def __init__(self, user):
        self.user = user
        self.profile = self.user.get_profile()

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
        if os.environ['ENV'] == 'dev':
            return [TEST_EMAIL1, TEST_EMAIL2]
        imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
        #imap_conn.debug = 4
        imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
        #try:
        #    list_output = imap_conn.list()
        #    log_object(list_output, 'LIST OUTPUT')
        #except Exception as exp:
        #    logger.info("LIST failed: %s" % exp)

        select_status, msg_data = imap_conn.select("[Gmail]/Sent Mail")
        if select_status != "OK":
            msg = "Invalid status recieved when selecting: %s" % select_status
            logger.info(msg)
            return FAIL
        try:
            self.profile.last_message_on_server = int(msg_data[0])
        except Exception as exp:
            logger.info("Unable to determine final message: %s" % exp)
            return FAIL
        try:
            _result, message_data = imap_conn.search(None, 'ALL')
            message_numbers = message_data[0]
            message_count = 0
            for num in message_numbers.split():
                if int(num) < self.profile.last_message_processed:
                    logger.info("Skipping message we've processed: %s" % num)
                    continue
                _result, data = imap_conn.fetch(num, '(RFC822)')
                logger.info('Message %s' % num)
                self.profile.last_message_processed = int(num)
                self.profile.save()
                message_string = data[0][1]
                analytics = Analytics(self.user, message_string)
                analytics.process_message()
                message_count += 1
                if message_count > MAX_TO_PROCESS:
                    logger.info('LIMITING NEW MESSAGES TO %s' % MAX_TO_PROCESS)
                    status = YIELD
                    break
            imap_conn.close()
            imap_conn.logout()
        except Exception as exp:
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            for line in fp.getvalue().split('\n'):
                logger.error("%% %s" % line)
        self.profile.save()  # We need to record the message_id we last touched
        return status

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
            logger.info('ERROR RETURNED FROM THE SERVER (%s)' % error)
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
        if self._fetch_access_token() == OK:
            creds = self._generate_oauth2_string(base64_encode=False)
            status = self._fetch_sent_messages(creds)
        else:
            logger.error("Unable to fetch access token. Aborting import")
        if status == YIELD:
            q = Queue(connection=conn)
            logger.info("Queuing another job in EmailAnalyzer")
            q.enqueue(self.process)
        return status
