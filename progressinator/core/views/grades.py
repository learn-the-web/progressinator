import decimal, math
import pendulum

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

import progressinator.common.grades as grade_helper
from progressinator.core.models import Term, Course, UserProgress, UserProgressLatenessChoices, UserProfile
from progressinator.core.serializers import UserProgressSerializer
from progressinator.common.util import build_dict_index
from progressinator.core.lib import CourseHelper


@login_required
def courses(request):
    try:
        user_profiles = UserProfile.objects.filter(user=request.user).select_related('current_course', 'current_course__term')
    except:
        user_profiles = None

    courses = CourseHelper.courses_as_dict(Course.objects.filter(term=settings.COURSES['SELF_DIRECTED_ID']))
    user_courses = CourseHelper.courses_as_dict(Course.objects.filter(id__in=(p.current_course_id for p in user_profiles))) if user_profiles else None
    if user_courses: courses.update(user_courses)
    user_profiles_details = CourseHelper.user_profiles_as_dict(user_profiles) if user_profiles else None

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Courses",
        'username': request.user.username,
        'courses': courses,
        'user_profiles_details': user_profiles_details,
        'nav_current': 'courses',
    }

    response = render(request, 'core/courses.html', context)

    if user_profiles:
        user_profile_for_cookie = user_profiles.latest('current_course__term__start_date')
        response.set_cookie('ltw-course-section', f'{user_profile_for_cookie.current_course.slug}-{user_profile_for_cookie.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response


@login_required
def course_grades(request, course_id):
    try:
        user_profiles = UserProfile.objects.filter(user=request.user).select_related('current_course', 'current_course__term')
    except:
        user_profiles = None

    user_profiles_details = CourseHelper.user_profiles_as_dict(user_profiles) if user_profiles else None

    if user_profiles_details and course_id in user_profiles_details:
        user_profile = user_profiles_details[course_id]
        course = Course.objects.get(pk=user_profiles_details[course_id]['current_course_id'])
    else:
        user_profile = None
        course = Course.objects.get(slug=course_id, term=settings.COURSES['SELF_DIRECTED_ID'])

    if not course:
        return redirect('core:courses')

    user_grades = UserProgress.objects.filter(user=request.user)
    current_grade = decimal.Decimal(0.0)
    max_assessments_per_section = grade_helper.max_assessments_per_section(course.data['assessments'])

    for a in course.data['assessments']:
        if user_profile and 'due_dates_algonquin' in a and user_profile['current_section'] in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = pendulum.parse(a['due_dates_algonquin'][user_profile['current_section']])

    if user_profile and user_profile['current_section']:
        course.data['assessments'] = sorted(course.data['assessments'], key=lambda k: k['user_due_date_algonquin'])
    assessment_index = build_dict_index(course.data['assessments'], 'uri')

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if (prog.created
                and user_profile and user_profile['current_section']
                and 'user_due_date_algonquin' in course.data['assessments'][assessment_index[prog.assessment_uri]]
                and prog.created > course.data['assessments'][assessment_index[prog.assessment_uri]]['user_due_date_algonquin']
                and (prog.excuse_lateness == 'LATENESS_NOT_EXCUSED' or not prog.excuse_lateness)
                ):
                prog.late = True
            if prog.details and 'started' in prog.details: prog.details['started'] = pendulum.parse(prog.details['started'])
            if prog.details and 'finished' in prog.details: prog.details['finished'] = pendulum.parse(prog.details['finished'])
            course.data['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog
            current_grade += grade_helper.calc_grade(prog, assessment_index, course.data['assessments'])

    if user_profile and user_profile['current_course_slug'] == course_id and user_profile['current_section'] in max_assessments_per_section:
        current_grade_max = max_assessments_per_section[user_profile['current_section']]
    else:
        current_grade_max = False

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"Grades for {course.data['title']}",
        'h1_title': course.data['title'],
        'username': request.user.username,
        'github_username': request.user.username,
        'student_user_id': request.user.id,
        'current_grade': current_grade,
        'current_grade_max': current_grade_max,
        'current_grade_average': current_grade / current_grade_max if current_grade_max else False,
        'term': course.term,
        'course': course,
        'excuse_lateness_options': UserProgressLatenessChoices.choices(),
        'today': pendulum.now(tz='America/Toronto')
    }

    if user_profile:
        context['user_profile'] = user_profile

    response = render(request, 'core/grades.html', context)

    if user_profiles:
        user_profile_for_cookie = user_profiles.latest('current_course__term__start_date')
        response.set_cookie('ltw-course-section', f'{user_profile_for_cookie.current_course.slug}-{user_profile_for_cookie.current_section}', max_age=settings.SESSION_COOKIE_AGE, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE)

    return response
