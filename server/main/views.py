# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
#from django.http import Http404
#from django.shortcuts import get_object_or_404
from django.shortcuts import render
from contact import ContactForm
from main.form_word_chooser import WordChooserForm
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import logging
import os
from rq import Queue
from main.worker import conn

from django.template import RequestContext
from main.email_fetch import EmailAnalyzer
from main.static_data import REDIRECT_URI, TEST_OAUTH_CALLBACK
from main.models import Word, WordsToLearn
import django.utils.timezone

logger = logging.getLogger(__name__)


def index(request):
    return render_to_response(
        'app.html', {}, context_instance=RequestContext(request))


def partial_helper(request, template_name):
    """
    Provides access to Angular's routing
    :param request: not used
    :param template_name: The name of the partial template to render
    :return: rendered template
    """
    model = {
        'user': request.user,
        'authenticated': request.user.is_authenticated(),
    }
    return render_to_response(template_name, model)


def current_user(request):
    """
    RESTFUL call to obtain information about the currently-logged in user, also provides
    information about how much of their email is currently imported.
    :param request: Django request object
    :return: JSON data about the current user
    """
    client_id = os.environ['GOOGLE_CLIENT_ID']
    scope = 'https://mail.google.com/ profile'

    url = ''
    if os.environ['ENV'] == 'dev':
        url = TEST_OAUTH_CALLBACK
    else:
        url = "https://accounts.google.com/o/oauth2/auth?scope=%s&" \
              "redirect_uri=%s&response_type=code&client_id=%s"
        url %= (scope, REDIRECT_URI, client_id)

    ready_to_import = False
    profile = request.user.get_profile()
    if request.user.email and profile.code:
        ready_to_import = True
    percent_imported = 0.0
    current = profile.last_message_processed
    final = profile.last_message_on_server
    if current and final:
        percent_imported = 100.0 * (float(current) / float(final))
    data = {
        'username': request.user.username,
        'email': request.user.email,
        'authenticated': request.user.is_authenticated(),
        'first_name': request.user.first_name,
        'token_expiration': request.user.get_profile().token_expiration,
        'ready_to_import': ready_to_import,
        'percent_imported': percent_imported,
        'google_auth_url': url,
    }

    return_json = simplejson.dumps(data)
    return HttpResponse(return_json, mimetype='application/json')


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
    """
    The user is requesting logout
    :param request:
    :return: Redirect to the opening page
    """
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def fetch_my_mail(request):
    """
    This is going to use our google credentials to go fetch all our mail!
    """
    q = Queue(connection=conn)
    if not request.user.email:
        return HttpResponse("User must have email defined.")
    logger.info("Queuing job in EmailAnalyzer")
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
        if not request.user.email:
            return HttpResponse("User must have email defined.")
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
def study(request):
    """
    Primary landing page for the user to decide what they want to study.
    """
    if request.method == 'POST':  # If the form has been submitted...
        form = WordChooserForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            word = Word.objects.get(word__exact=form.cleaned_data['new_word'])
            new_word_to_learn = WordsToLearn(
                word=word,
                user=request.user,
                date_added=django.utils.timezone.now()
            )
            new_word_to_learn.save()
            #return HttpResponseRedirect('/accounts/profile/')
    else:
        logger.info("GET condition")
        form = WordChooserForm()  # An unbound form

    learning_list = []
    try:
        learning_list = WordsToLearn.objects.filter(user__id=request.user.id)
    except WordsToLearn.DoesNotExist:
        pass

    return render(request, 'study.html', {
        'page_name': 'study',
        'learning_list': learning_list,
        'form': form,
    })


@login_required
def gallery(request):
    """
    Choosing a new word is fun! Show them off
    """
    return render(request, 'gallery.html', {
        'page_name': 'gallery',
        'controller_name': 'galleryCtrl',
        'controller_script': 'galleryCtrl.js',
    })


def definition(request, word_to_lookup):
    """
    the user wants to look a word up
    """
    return render(request, 'definition.html')


@login_required
def remove(request, word_to_remove):
    """
    the user wants to remove a word from their study-list
    """

    word_object = Word.objects.get(word__exact=word_to_remove)
    word_to_learn = WordsToLearn.objects.filter(
        user__id=request.user.id, word=word_object)
    word_to_learn.delete()
    return HttpResponseRedirect('/study')


def e2e(request):
    'Run the end-to-end test'
    return render(request, 'runner.html', {})


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
