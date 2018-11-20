import decimal, math
import pendulum

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

import progressinator.common.grades as grade_helper
from progressinator.core.lib import Courses
from progressinator.core.models import UserProgress, UserProgressLatenessChoices, UserProfile
from progressinator.core.serializers import UserProgressSerializer
from progressinator.common.util import build_dict_index


@login_required
def courses(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Courses",
        'username': request.user.username,
        'courses': Courses.all(),
        'nav_current': 'courses',
    }

    response = render(request, 'core/courses.html', context)

    if user_profile:
        response.set_cookie('ltw-course-section', f'{user_profile.current_course.slug}-{user_profile.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response


@login_required
def course_grades(request, course_id):
    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:courses')

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None

    assessment_index = build_dict_index(course['assessments'], 'uri')
    user_grades = UserProgress.objects.filter(user=request.user)
    current_grade = decimal.Decimal(0.0)
    max_assessments_per_section = grade_helper.max_assessments_per_section(course['assessments'])

    for a in course['assessments']:
        if user_profile and 'due_dates_algonquin' in a and user_profile.current_section in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = pendulum.parse(a['due_dates_algonquin'][user_profile.current_section])

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if (prog.created
                and 'user_due_date_algonquin' in course['assessments'][assessment_index[prog.assessment_uri]]
                and prog.created > course['assessments'][assessment_index[prog.assessment_uri]]['user_due_date_algonquin']
                and (prog.excuse_lateness == 'LATENESS_NOT_EXCUSED' or not prog.excuse_lateness)
                ):
                prog.late = True
            if prog.details and 'started' in prog.details: prog.details['started'] = pendulum.parse(prog.details['started'])
            if prog.details and 'finished' in prog.details: prog.details['finished'] = pendulum.parse(prog.details['finished'])
            course['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog
            current_grade += grade_helper.calc_grade(prog, assessment_index, course['assessments'])

    if user_profile:
        current_grade_max = max_assessments_per_section[user_profile.current_section]
    else:
        current_grade_max = False

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"Grades for {course['title']}",
        'h1_title': course['title'],
        'username': request.user.username,
        'github_username': request.user.username,
        'current_grade': current_grade,
        'current_grade_max': current_grade_max,
        'current_grade_average': current_grade / current_grade_max if current_grade_max else False,
        'course': course,
        'excuse_lateness_options': UserProgressLatenessChoices.choices(),
        'today': pendulum.now(tz='America/Toronto')
    }

    if user_profile:
        context['user_profile'] = user_profile

    response = render(request, 'core/grades.html', context)

    if user_profile:
        response.set_cookie('ltw-course-section', f'{course["course"]}-{user_profile.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response

