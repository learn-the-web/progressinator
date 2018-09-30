from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout


def signin(request):
    context = {
        'doc_title': 'Sign in · Learn the Web',
        'hide_nav': True,
    }
    return render(request, 'core/signin.html', context)


def signout(request):
    logout(request)
    return redirect('core:sign_in')
