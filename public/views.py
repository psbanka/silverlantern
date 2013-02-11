# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
#from django.http import Http404
#from django.shortcuts import get_object_or_404
from django.shortcuts import render
from contact import ContactForm
from public.form_word_chooser import WordChooserForm
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import logging
import os
from rq import Queue
from worker import conn

from public.email_fetch import EmailAnalyzer
from public.static_data import REDIRECT_URI, TEST_OAUTH_CALLBACK
from public.models import WordsToLearn
import django.utils.timezone

# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    model = {
        'user': request.user,
    }
    return render_to_response('index.html', model)

    # Example of how to do a nice form:
    #from forms import MessageForm
    #return render(request, 'index.html', {'form': MessageForm()})


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

    url = ''
    if os.environ['ENV'] == 'dev':
        url = TEST_OAUTH_CALLBACK
    else:
        url = "https://accounts.google.com/o/oauth2/auth?scope=%s&"\
            "redirect_uri=%s&response_type=code&client_id=%s"
        url %= (scope, REDIRECT_URI, client_id)

    model = {
        'user': request.user,
        'profile': request.user.get_profile(),
        'google_auth_url': url,
    }
    return render_to_response('profile.html', model)


@login_required
def fetch_my_mail(request):
    """
    This is going to use our google credentials to go fetch all our mail!
    """
    q = Queue(connection=conn)
    email_analyzer = EmailAnalyzer(request.user)
    q.enqueue(email_analyzer.process)
    return HttpResponse("Job queued.")


@login_required
def oauth2callback(request):
    if request.method == "POST":
        logger.error("POST condition")
    if request.method == "GET":
        logger.info("GET condition")
    for key, value in request.GET.items():
        logger.info("Key: %s / Value: %s" % (key, value))
    code = request.GET.get('code')
    model = {
        'authorized': False,
        'message': ''
    }
    if code:
        profile = request.user.get_profile()
        profile.code = code
        profile.save()
        q = Queue(connection=conn)
        email_analyzer = EmailAnalyzer(request.user)
        q.enqueue(email_analyzer.process)
        model['message'] = "Fetching email..."
        model['authorized'] = True
    else:
        model['authorized'] = False
        error = request.GET.get('error')
        if error:
            model['message'] = error
        else:
            model['message'] = "Not authorized. Unknown reason."

    return render_to_response('oauth_results.html', model)


@login_required
def choose_new_word(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = WordChooserForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            new_word_to_learn = WordsToLearn(
                word=form.cleaned_data['new_word'],
                user=request.user,
                date_added=django.utils.timezone.now()
            )
            new_word_to_learn.save()
            return HttpResponseRedirect('/accounts/profile/')
    else:
        logger.info("GET condition")
        form = WordChooserForm()  # An unbound form

    return render(request, 'choose_new_word.html', {
        'form': form,
    })


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
