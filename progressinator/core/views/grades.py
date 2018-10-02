from datetime import datetime
import pytz
import dateutil.parser

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view

from progressinator.core.lib import Courses, MarkbotHelper
from progressinator.core.models import UserProgress, UserProfile
from progressinator.core.serializers import UserProgressSerializer
from progressinator.common.util import build_dict_index


@login_required
def courses(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': 'Courses',
        'username': request.user.username,
        'email': request.user.email,
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
    user_profile = UserProfile.objects.filter(user=request.user)
    user_grades = UserProgress.objects.filter(user=request.user)
    amount_complete = 0.0

    for a in course['assessments']:
        if user_profile.count() > 0:
            a['user_due_date_algonquin'] = datetime.fromisoformat(a['due_dates_algonquin'][user_profile[0].current_section]).replace(tzinfo=pytz.UTC)

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if prog.created and prog.created > course['assessments'][assessment_index[prog.assessment_uri]]['user_due_date_algonquin']:
                prog.late = True
            if prog.details and 'started' in prog.details: prog.details['started'] = dateutil.parser.isoparse(prog.details['started'])
            if prog.details and 'finished' in prog.details: prog.details['finished'] = dateutil.parser.isoparse(prog.details['finished'])
            course['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog
            amount_complete += prog.grade * course['assessments'][assessment_index[prog.assessment_uri]]['assessment_each_algonquin']

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"Grades for {course['title']}",
        'h1_title': course['title'],
        'username': request.user.username,
        'email': request.user.email,
        'amount_complete': amount_complete,
        'course': course,
    }

    if user_profile.count() > 0:
        context['user_profile'] = user_profile[0]

    return render(request, 'core/grades.html', context)


@api_view(['POST'])
def submit_assessment(request):
    data = JSONParser().parse(request)
    serializer = UserProgressSerializer(data=data)

    if serializer.is_valid():
        if data['github_username'] != request.user.username:
            return JsonResponse({
                'error': status.HTTP_401_UNAUTHORIZED,
                'detail': "The GitHub username does not match the authenticated API token",
                }, status=status.HTTP_401_UNAUTHORIZED)

        if 'Markbot' in serializer.validated_data['submitted_by']:
            if not MarkbotHelper.confirm_version(serializer.validated_data['submitted_by']):
                return JsonResponse({
                    'error': status.HTTP_406_NOT_ACCEPTABLE,
                    'detail': f"Markbot version too old, expecting >= Markbot/{settings.MARKBOT['DESKTOP_VERSION']} or Markbot Online/{settings.MARKBOT['ONLINE_VERSION']}",
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # return HttpResponse(MarkbotHelper.generate_signature(data['github_username'], serializer.validated_data))
        if not MarkbotHelper.confirm_signature(data['github_username'], serializer.validated_data):
            return JsonResponse({
                'error': status.HTTP_406_NOT_ACCEPTABLE,
                'detail': "Incomplete or missing arguments—double check you have the most recent version of Markbot",
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

        previousSubmission = UserProgress.objects.filter(user=request.user, assessment_uri=serializer.validated_data['assessment_uri'])

        if previousSubmission.count() > 0:
            return JsonResponse({
                'error': status.HTTP_409_CONFLICT,
                'detail': "Assessment has already been graded",
                }, status=status.HTTP_409_CONFLICT)

        serializer.save(user=request.user)

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    return JsonResponse(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
