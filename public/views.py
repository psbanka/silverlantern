# -*- coding: utf-8 -*-
from django.shortcuts import render
from forms import MessageForm

def index(request):
    # This view is missing all form handling logic for simplicity of the example
    return render(request, 'index.html', {'form': MessageForm()})