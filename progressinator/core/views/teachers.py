from datetime import datetime
import decimal, math, pytz
import dateutil.parser

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from progressinator.common.util import build_dict_index, build_queryset_index
import progressinator.common.grades as grade_helper
from progressinator.core.lib import Courses
from progressinator.core.models import UserProgress, UserProfile, Course
from progressinator.core.serializers import UserProgressSerializer

import logging


@staff_member_required
def courses(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Courses · Teachers",
        'username': request.user.username,
        'courses': Courses.all(),
        'nav_current': 'teachers',
        'h1_title': "Teachers ·",
    }

    for course in context['courses']:
        course['totals']['students'] = Course.objects.get(slug=course['course']).profiles.count()

    return render(request, 'core/teachers/courses.html', context)


@staff_member_required
def course_status(request, course_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:teacher_courses')

    students = UserProfile.objects.filter(current_course=course_in_db).select_related('user').order_by('user__last_name', 'user__first_name')
    assessment_index = build_dict_index(course['assessments'], 'uri')
    all_grades = UserProgress.objects.filter(user_id__in=(s.user_id for s in students))
    max_assessments_per_section = grade_helper.max_assessments_per_section(course['assessments'])
    stats_actual_total = 0
    stats_max_total = 0
    stats_grade_total = 0
    stats_pass_rate_total = 0
    stats_grade_status = {
        'Excellent': 0,
        'Satisfactory': 0,
        'Weak': 0,
        'Failing': 0,
    }

    for student in students:
        student_grades = (grade_helper.calc_grade(g, assessment_index, course['assessments']) for g in all_grades if g.user_id == student.user_id)
        student.current_grade = decimal.Decimal(math.fsum(student_grades))
        student.current_grade_max = max_assessments_per_section[student.current_section]
        student.current_grade_average = student.current_grade / student.current_grade_max
        stats_grade_total += student.current_grade_average
        stats_actual_total += student.current_grade
        stats_max_total += student.current_grade_max
        stats_grade_status[grade_helper.grade_as_status(student.current_grade_average)] += 1

    for prog in all_grades:
        if prog.assessment_uri in assessment_index and prog.grade > 0:
            if 'total_students_pass' not in course['assessments'][assessment_index[prog.assessment_uri]]:
                course['assessments'][assessment_index[prog.assessment_uri]]['total_students_pass'] = 0
            course['assessments'][assessment_index[prog.assessment_uri]]['total_students_pass'] += 1

    for assessment in course['assessments']:
        if 'total_students_pass' in assessment:
            assessment['total_students_pass_rate'] = assessment['total_students_pass'] / students.count()
        else:
            assessment['total_students_pass_rate'] = 0
        stats_pass_rate_total += assessment['total_students_pass_rate']

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{course['title']} · Teachers",
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': f"{course['title']} ·",
        'course': course,
        'students': students,
        'stats_grade_avg': stats_grade_total / students.count(),
        'stats_actual_avg': stats_actual_total / students.count(),
        'stats_max_avg': stats_max_total / students.count(),
        'stats_grade_status': stats_grade_status,
        'stats_assessments_total': len(course['assessments']),
        'stats_assessments_no_zeros': len(course['assessments']) - len([a for a in course['assessments'] if a['assessment_each_algonquin'] <= 0]),
        'stats_pass_rate_avg': stats_pass_rate_total / len(course['assessments']),
    }

    return render(request, 'core/teachers/course-status.html', context)


@staff_member_required
def user_grades(request, course_id, user_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:teacher_courses')

    try:
        student_profile = UserProfile.objects.get(user=user_id)
    except:
        student_profile = None

    user_grades = UserProgress.objects.filter(user=user_id)
    current_grade = decimal.Decimal(0.0)
    assessment_index = build_dict_index(course['assessments'], 'uri')
    max_assessments_per_section = grade_helper.max_assessments_per_section(course['assessments'])

    for a in course['assessments']:
        if student_profile and 'due_dates_algonquin' in a and student_profile.current_section in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = datetime.fromisoformat(a['due_dates_algonquin'][student_profile.current_section]).replace(tzinfo=pytz.UTC)

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
            current_grade += grade_helper.calc_grade(prog, assessment_index, course['assessments'])

    current_grade_max = max_assessments_per_section[student_profile.current_section]

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{student_profile.user.first_name} {student_profile.user.last_name} · Teachers",
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': f"{student_profile.user.first_name} {student_profile.user.last_name} ·",
        'current_grade': current_grade,
        'current_grade_max': current_grade_max,
        'current_grade_average': current_grade / current_grade_max,
        'course': course,
    }

    if student_profile:
        context['student_profile'] = student_profile

    return render(request, 'core/teachers/user-grades.html', context)


@staff_member_required
def assessment_grades(request, course_id, assessment_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Courses.get(course_id)
    except:
        return redirect('core:teacher_courses')

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Assessment · Teachers",
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': "Assessment ·",
    }
    return render(request, 'core/teachers/assessment-grades.html', context)
