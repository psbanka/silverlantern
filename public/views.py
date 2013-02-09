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

# Get an instance of a logger
logger = logging.getLogger(__name__)
#logger = logging.getLogger('console')


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
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('auth.html', {'state': state, 'username': username})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def profile(request):
    #url = "https://accounts.google.com/o/oauth2/auth?scope=%s&state=%s&redirect_uri=%s&response_type=code&client_id=%s&access_type=%s"
    client_id = "554293961623.apps.googleusercontent.com"
    scope = 'https://mail.google.com/ profile'
    redirect_url = 'http://www.silverlantern.net/oauth2callback'

    url = "https://accounts.google.com/o/oauth2/auth?scope=%s&redirect_uri=%s&response_type=code&client_id=%s"
    url %= (scope, redirect_url, client_id)
    model = {
        'user': request.user,
        'google_auth_url': url
    }
    return render_to_response('profile.html', model)


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
        'authorized': "NO",
        'code': code,
        'error': error
    }
    return render_to_response('oauth_results.html', model)


@login_required
def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        print "POST CONDITION"
        logger.info("codePOST condition")
        form = ContactForm(request.POST)  # A form bound to the POST data
        print "have form object"
        if form.is_valid():  # All validation rules pass
            print "form is valid"
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/polls/thanks/')  # Redirect after POST
    else:
        print "GET CONDITION"
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
