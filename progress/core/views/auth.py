from django.shortcuts import render
from django.urls import reverse


def signin(request):
    context = {
        'doc_title': 'Sign in · Learn the Web',
    }
    return render(request, 'core/signin.html', context)
