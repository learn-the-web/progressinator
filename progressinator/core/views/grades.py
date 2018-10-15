from datetime import datetime
import decimal
import pytz
import dateutil.parser

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from progressinator.core.lib import Courses
from progressinator.core.models import UserProgress, UserProfile
from progressinator.core.serializers import UserProgressSerializer
from progressinator.common.util import build_dict_index


@login_required
def courses(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Courses',
        'username': request.user.username,
        'courses': Courses.all(),
        'nav_current': 'courses',
    }

    return render(request, 'core/courses.html', context)


@login_required
def course_grades(request, course_id):
    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:courses')

    assessment_index = build_dict_index(course['assessments'], 'uri')
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    user_grades = UserProgress.objects.filter(user=request.user)
    amount_complete = decimal.Decimal(0.0)

    for a in course['assessments']:
        if user_profile and 'due_dates_algonquin' in a and user_profile.current_section in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = datetime.fromisoformat(a['due_dates_algonquin'][user_profile.current_section]).replace(tzinfo=pytz.UTC)

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if (prog.created
                and 'user_due_date_algonquin' in course['assessments'][assessment_index[prog.assessment_uri]]
                and prog.created > course['assessments'][assessment_index[prog.assessment_uri]]['user_due_date_algonquin']):
                prog.late = True
            if prog.details and 'started' in prog.details: prog.details['started'] = dateutil.parser.isoparse(prog.details['started'])
            if prog.details and 'finished' in prog.details: prog.details['finished'] = dateutil.parser.isoparse(prog.details['finished'])
            course['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog
            amount_complete += prog.grade * decimal.Decimal(course['assessments'][assessment_index[prog.assessment_uri]]['assessment_each_algonquin'])

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"Grades for {course['title']}",
        'h1_title': course['title'],
        'username': request.user.username,
        'amount_complete': amount_complete,
        'course': course,
    }

    if user_profile:
        context['user_profile'] = user_profile

    return render(request, 'core/grades.html', context)

