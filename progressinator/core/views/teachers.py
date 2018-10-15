from datetime import datetime
import decimal
import pytz
import dateutil.parser

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from progressinator.core.lib import Courses
from progressinator.core.models import UserProgress, UserProfile, Course
from progressinator.core.serializers import UserProgressSerializer

import logging


@staff_member_required
def courses(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Courses · Teachers',
        'username': request.user.username,
        'courses': Courses.all(),
        'nav_current': 'teachers',
        'h1_title': 'Teachers ·',
    }

    for course in context['courses']:
        course['totals']['students'] = Course.objects.get(slug=course['course']).profiles.count()

    return render(request, 'core/teachers/courses.html', context)


@staff_member_required
def course_status(request, course_id):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Web Dev · Teachers',
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': 'Web Dev ·',
    }
    return render(request, 'core/teachers/course-status.html', context)


@staff_member_required
def user_grades(request, course_id, user_id):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'User · Teachers',
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': 'User ·',
    }
    return render(request, 'core/teachers/user-grades.html', context)


@staff_member_required
def assessment_grades(request, course_id, assessment_id):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Assessment · Teachers',
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': 'Assessment ·',
    }
    return render(request, 'core/teachers/assessment-grades.html', context)
