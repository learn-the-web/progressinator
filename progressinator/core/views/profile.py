import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.authtoken.models import Token
from progressinator.core.models import Term, Course, UserProfile


@login_required
def index(request):
    try:
        api_token = Token.objects.get(user=request.user)
    except:
        api_token = ""

    try:
        current_term = Term.objects.get(end_date__gte=datetime.date.today())
    except:
        current_term = None

    if current_term:
        try:
            user_profile = UserProfile.objects.get(user=request.user, current_course__term=current_term)
        except:
            user_profile = None
    else:
        user_profile = None

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Profile",
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'api_token': api_token,
        'nav_current': 'profile',
        'current_term': current_term,
    }

    if user_profile:
        context['current_course'] = user_profile.current_course
        context['current_section'] = user_profile.current_section
    else:
        if current_term:
            try:
                all_courses = Course.objects.filter(term=current_term)
            except:
                all_courses = None
        else:
            all_courses = None
        context['all_courses'] = all_courses

    response = render(request, 'core/profile.html', context)

    if user_profile:
        response.set_cookie('ltw-course-section', f'{user_profile.current_course.slug}-{user_profile.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response


@login_required
def save(request):
    if request.method != 'POST' and 'current_section' not in request.POST:
        return redirect('core:profile')

    try:
        current_term = Term.objects.get(end_date__gte=datetime.date.today())
    except:
        return redirect('core:profile')

    previous_user_profile = UserProfile.objects.filter(user=request.user, current_course__term=current_term)

    if previous_user_profile:
        return redirect('core:profile')

    course_bits = request.POST['current_section'].strip().split('::')

    if len(course_bits) != 2:
        return redirect('core:profile')

    user_profile = UserProfile(user=request.user, current_course_id=course_bits[0].strip(), current_section=course_bits[1].strip())

    try:
        user_profile.full_clean()
    except:
        return redirect('core:profile')

    user_profile.save()

    return redirect('core:profile')
