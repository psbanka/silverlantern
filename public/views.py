# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from forms import MessageForm
from contact import ContactForm
from public.models import Poll, Choice
from django.template import Context, loader
from django.core.urlresolvers import reverse

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def index(request):
    # This view is missing all form handling logic for simplicity of the example
    return render(request, 'index.html', {'form': MessageForm()})

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        print "POST CONDITION"
        logger.info("POST condition")
        form = ContactForm(request.POST) # A form bound to the POST data
        print "have form object"
        if form.is_valid(): # All validation rules pass
            print "form is valid"
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/polls/thanks/') # Redirect after POST
    else:
        print "GET CONDITION"
        logger.info("GET condition")
        form = ContactForm() # An unbound form

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
