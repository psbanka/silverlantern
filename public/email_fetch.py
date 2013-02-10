import time
import urllib
import json
import os
import logging
import base64
import imaplib

from datetime import datetime
from public.static_data import REDIRECT_URI, GOOGLE_ACCOUNTS_BASE_URL
from public.static_data import TEST_GOOGLE_REPLY, OK, FAIL
import django.utils.timezone
from pprint import pformat

logger = logging.getLogger(__name__)


###############################################
## Lifted from Google's oauth.py
###############################################

def _generate_oauth2_string(username, access_token, base64_encode=True):
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
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
    if base64_encode:
        auth_string = base64.b64encode(auth_string)
    return auth_string


def log_object(object, title):
    "Logs an entire object to the log"
    logger.info("===START==========================%s" % title.upper())
    for line in pformat(object).split('\n'):
        logger.info(line)
    logger.info("===FINISH=========================%s" % title.upper())


def test_imap_auth(user, auth_string):
    """
    Authenticates to IMAP with the given auth_string.

    Prints a debug trace of the attempted IMAP connection.

    Args:
        user: The Gmail username (full email address)
        auth_string: A valid OAuth2 string, as returned by
            generate_oath2_string. Must not be base64-encoded,
            since imaplib does its own base64-encoding.
    """
    logger.info("IMAP ================== 0")
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    logger.info("IMAP ================== 1")
    imap_conn.debug = 4
    logger.info("IMAP ================== 2")
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    logger.info("auth_string: (%s)" % auth_string)
    imap_conn.select('INBOX')
    logger.info("IMAP ================== 4")
    log_object(dir(imap_conn), "imap_conn methods")


def _get_accounts_url(command):
    """Generates the Google Accounts URL.

    Args:
      command: The command to execute.

    Returns:
      A URL for the given command.
    """
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


###############################################
## Lifted from Google's oauth.py
###############################################


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


def _token_is_current(profile):
    token_expiration = profile.token_expiration
    if token_expiration:
        if token_expiration > django.utils.timezone.now():
            return True
    return False


def _fetch_access_token(user):
    """
    We're going to go ask google if we can have a temporary access-token
    """
    profile = user.get_profile()
    code = profile.code
    if not code:
        logger.info('User has no code from Google.')
        return FAIL
    if _token_is_current(profile):
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
        profile.token_expiration = utc_exp
    except ValueError as exp:
        expires_in = server_response.get('expires_in')
        logger.error("Exception: %s" % exp)
        logger.error("Error converting expiration %s" % expires_in)
    token_type = server_response.get('token_type')
    id_token = server_response.get('id_token')
    profile.access_token = access_token
    profile.token_type = token_type
    profile.id_token = id_token
    profile.save()
    return OK


def _get_email(user):
    """
    Main method for fetching email from Google
    """
    profile = user.get_profile()
    creds = _generate_oauth2_string(
        user.email, profile.access_token, base64_encode=False)

    test_imap_auth(user.email, creds)

    counter = 5
    while counter:
        logger.info("fetching email for %s...(%s)" % (user.username, counter))
        time.sleep(1)
        counter -= 1
    return OK


def email_fetch(user):
    if _fetch_access_token(user) == OK:
        return _get_email(user)
    return FAIL