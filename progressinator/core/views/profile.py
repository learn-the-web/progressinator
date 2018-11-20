from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.authtoken.models import Token
from progressinator.core.models import UserProfile


@login_required
def index(request):
    try:
        api_token = Token.objects.get(user=request.user)
    except:
        api_token = ""

    try:
        profile = UserProfile.objects.get(user=request.user)
    except:
        profile = None

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Profile",
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'api_token': api_token,
        'nav_current': 'profile',
    }

    if profile:
        context['current_course'] = profile.current_course
        context['current_section'] = profile.current_section

    response = render(request, 'core/profile.html', context)

    if profile:
        response.set_cookie('ltw-course-section', f'{profile.current_course.slug}-{profile.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response
