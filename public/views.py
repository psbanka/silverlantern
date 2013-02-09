# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from forms import MessageForm
from contact import ContactForm
from public.models import Poll, Choice
from django.template import Context
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import logging
import os
import urllib
import json
import time
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)
GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'
REDIRECT_URI = 'http://www.silverlantern.net/oauth2callback'


def index(request):
    # This view is missing all form handling logic
    # for simplicity of the example
    return render(request, 'index.html', {'form': MessageForm()})


def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
            else:
                state = "Your account is not active, "\
                    "please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('auth.html', {
        'state': state, 'username': username
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def profile(request):
    #url = "https://accounts.google.com/o/oauth2/auth?scope=%s&state=%s
    #&redirect_uri=%s&response_type=code&client_id=%s&access_type=%s"
    client_id = os.environ['GOOGLE_CLIENT_ID']
    scope = 'https://mail.google.com/ profile'

    url = "https://accounts.google.com/o/oauth2/auth?scope=%s&"\
        "redirect_uri=%s&response_type=code&client_id=%s"
    url %= (scope, REDIRECT_URI, client_id)
    model = {
        'user': request.user,
        'google_auth_url': url,
    }
    return render_to_response('profile.html', model)


def _get_accounts_url(command):
    """Generates the Google Accounts URL.

    Args:
      command: The command to execute.

    Returns:
      A URL for the given command.
    """
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def _get_auth_token(authorization_code):
    """
    Go ask google for an access token for this user instead of
    just an authorization code.
    """
    params = {}
    params['client_id'] = os.environ['GOOGLE_CLIENT_ID']
    params['client_secret'] = os.environ['GOOGLE_CLIENT_SECRET']
    params['code'] = authorization_code
    params['redirect_uri'] = REDIRECT_URI
    params['grant_type'] = 'authorization_code'
    request_url = _get_accounts_url('o/oauth2/token')

    response = urllib.urlopen(request_url, urllib.urlencode(params)).read()
    with open('/tmp/google_response.json', 'w') as fh:
        fh.write(response)
        fh.flush()
    return json.loads(response)


@login_required
def oauth2callback(request):
    if request.method == "POST":
        logger.error("POST condition")
    if request.method == "GET":
        logger.info("GET condition")
    for key, value in request.GET.items():
        logger.info("Key: %s / Value: %s" % (key, value))
    code = request.GET.get('code')
    error = request.GET.get('error')
    model = {
        'authorized': False,
        'code': code,
        'error': error,
        'access_token': '',
    }
    if code:
        server_response = _get_auth_token(code)
        for key, value in server_response.items():
            msg = "Server Response: Key: (%s) Value: (%s)" % (key, value)
            logger.info(msg)
        error = server_response.get("error")
        if error:
            logger.info('ERROR RETURNED FROM THE SERVER')
            model['error'] = error
            model['authorized'] = False
        else:
            logger.info('--------------------0')
            code = server_response.get('code')
            logger.info('--------------------1')
            access_token = server_response.get('access_token')
            logger.info('--------------------2')
            try:
                expires_in = int(server_response.get('expires_in'))
                token_expiration = datetime.fromtimestamp(
                    expires_in + time.time())
                request.user.token_expiration = token_expiration
                logger.info('--------------------3')
            except ValueError as exp:
                expires_in = server_response.get('expires_in')
                logger.error("Exception: %s" % exp)
                logger.error("Error converting expiration %s" % expires_in)
            logger.info('--------------------4')
            token_type = server_response.get('token_type')
            logger.info('--------------------5')
            id_token = server_response.get('id_token')
            logger.info('--------------------6')
            model['authorized'] = True
            model['access_token'] = access_token
            logger.info('--------------------7')
            request.user.access_token = access_token
            request.user.token_type = token_type
            request.user.id_token = id_token
            request.user.save()
            logger.info('--------------------8')
    else:
        logger.info('NO CODE RETURNED')

    return render_to_response('oauth_results.html', model)


@login_required
def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        logger.info("codePOST condition")
        form = ContactForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/polls/thanks/')
    else:
        logger.info("GET condition")
        form = ContactForm()  # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })


def thanks(request):
    return HttpResponse("Thanks.")


def pollview(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    context = Context({
        'latest_poll_list': latest_poll_list,
    })
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    try:
        poll = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/results.html', {'poll': poll})


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect('/polls/%s/results' % p.id)
