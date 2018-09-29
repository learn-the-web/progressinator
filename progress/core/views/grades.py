from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from progress.core.lib import Courses
from progress.core.models import UserProgress
from progress.common.util import build_dict_index
import logging


@login_required
def courses(request):
    context = {
        'doc_title': 'Courses',
        'username': request.user.username,
        'email': request.user.email,
        'courses': Courses.all(),
    }

    return render(request, 'core/courses.html', context)


@login_required
def course_grades(request, course_id):
    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:courses')

    assessment_index = build_dict_index(course['assessments'], 'uri')
    user_grades = UserProgress.objects.filter(user=request.user)

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            course['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog

    context = {
        'doc_title': f"Grades for {course['title']}",
        'username': request.user.username,
        'email': request.user.email,
        'course': course,
    }

    return render(request, 'core/grades.html', context)
