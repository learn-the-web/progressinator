import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.conf import settings


def signin(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Sign in',
        'hide_nav': True,
    }
    return render(request, 'core/signin.html', context)


def signout(request):
    logout(request)
    return redirect('core:sign_in')
