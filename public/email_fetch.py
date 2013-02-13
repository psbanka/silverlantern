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

from datetime import datetime
from public.static_data import REDIRECT_URI, GOOGLE_ACCOUNTS_BASE_URL
from public.static_data import TEST_GOOGLE_REPLY, OK, FAIL
from public.static_data import TEST_EMAIL1, TEST_EMAIL2
from public.models import WordUse

import django.utils.timezone
from pprint import pformat

logger = logging.getLogger(__name__)
SEP_MATCHER = re.compile('On \S*, .* wrote:')

PUNCTUATION = [
    "'", ",", ".", "(", ")", ";", '"', "!", "-", "[",
    "]", "{", "}", "?", "/"
]


def cleanup(word):
    """
    We have been given a word with potentially a bunch of punctuation
    and stuff around it. Let's clean it up.
    """
    logger.info("Incoming word: %s" % word)
    if word[0] in PUNCTUATION:
        word = word[1:]
    if word[-1] in PUNCTUATION:
        word = word[:-1]
    logger.info("Cleaned word: %s" % word)
    return word


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

    def __init__(self, message_string):
        self.message = email.message_from_string(message_string)
        self.to = self.message.get('To')
        logger.info("DATE: (%s)" % self.message["Date"])
        sent_time = time.mktime(email.utils.parsedate(self.message["Date"]))
        self.sent = datetime.fromtimestamp(sent_time)
        self.sent_words = []

    def process_message(self, user):
        self.sent_text = ''
        for line in self.message.get_payload().split('\n'):
            if SEP_MATCHER.findall(line):
                break
            self.sent_words += line.split()

        for new_word, count in Counter(self.sent_words).items():
            try:
                word_use = WordUse.objects.get(word__exact=cleanup(new_word))
            except WordUse.DoesNotExist:
                word_use = WordUse(word=new_word)
                word_use.times_used = 0

            word_use.times_used += count
            word_use.last_time_used = self.sent
            word_use.last_sent_to = self.to
            word_use.user = user
            word_use.save()


class EmailAnalyzer(object):

    def __init__(self, user):
        self.user = user
        self.profile = self.user.get_profile()

    def _process_messages(self, messages):
        """
        Go through all the new messages received and do things
        with them
        """
        for message_string in messages:
            analytics = Analytics(message_string)
            analytics.process_message(self.user)

    def _fetch_sent_messages(self, auth_string):
        """
        Authenticates to IMAP with the given auth_string.

        Prints a debug trace of the attempted IMAP connection.

        Args:
            auth_string: A valid OAuth2 string, as returned by
                generate_oath2_string. Must not be base64-encoded,
                since imaplib does its own base64-encoding.
        """
        if os.environ['ENV'] == 'dev':
            return [TEST_EMAIL1, TEST_EMAIL2]
        imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
        imap_conn.debug = 4
        imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
        new_messages = []
        try:
            list_output = imap_conn.list()
            log_object(list_output, 'LIST OUTPUT')
        except Exception as exp:
            logger.info("LIST failed: %s" % exp)

        status, msg_data = imap_conn.select("[Gmail]/Sent Mail")
        try:
            self.profile.last_message_on_server = int(msg_data[0])
        except Exception as exp:
            logger.info("Unable to determine final message: %s" % exp)
            return []
        try:
            _result, message_data = imap_conn.search(None, 'ALL')
            message_numbers = message_data[0]
            log_object(message_numbers, "Message numbers")
            try:
                logger.info("first message: %s" % int(message_data.split([0])))
                logger.info("last message: %s" % int(message_data.split([-1])))
            except ValueError as exp:
                logger.error("Error examining messages (%s)" % exp)
            for num in message_numbers.split():
                if int(num) < self.profile.last_message_processed:
                    logger.info("Skipping message we've processed: %s" % num)
                    continue
                _result, data = imap_conn.fetch(num, '(RFC822)')
                logger.info('Message %s' % num)
                self.profile.last_message_processed = int(num)
                logger.info("data[0][0]: %s" % data[0][0])
                new_messages.append(data[0][1])
                if len(new_messages) > 20:
                    logger.info('LIMITING NEW MESSAGES TO 20')
                    break
            imap_conn.close()
            imap_conn.logout()
        except Exception as exp:
            logger.info("FETCH FAILED: %s" % exp)
        self.profile.save()  # We need to record the message_id we last touched
        return new_messages

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
            new_messages = self._fetch_sent_messages(creds)
            self._process_messages(new_messages)
            status = OK
        else:
            logger.error("Unable to fetch access token. Aborting import")
        return status
