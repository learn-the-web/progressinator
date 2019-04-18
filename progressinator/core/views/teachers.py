import decimal, math, datetime
import pendulum

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils.html import strip_tags
from django import forms

from progressinator.common.util import build_dict_index, build_queryset_index, model_to_dict
import progressinator.common.grades as grade_helper
from progressinator.core.models import Term, Course, UserProgress, UserProgressForm, UserProgressLatenessChoices, UserProfile
from progressinator.core.serializers import UserProgressSerializer


def empty_is_none(data):
    return data if data else None


def comment_is_different(data1, data2):
    comment1 = ''
    comment2 = ''

    if data1 and 'comment' in data1: comment1 = data1['comment']
    if 'details' in data2 and 'comment' in data2['details']: comment2 = data2['details']['comment']

    return empty_is_none(comment1) != empty_is_none(comment2)


def crud_grades(request, user_grades, assessment_uri_index=None, user_id_index=None):
    posted_grades = {'update': [], 'create': [], 'delete': []}
    post_user_progress_id = request.POST.getlist('user_progress_id')
    post_grade = request.POST.getlist('grade')
    post_assessment_uri = request.POST.getlist('assessment_uri')
    post_submitted_by = request.POST.getlist('submitted_by')
    post_excuse_lateness = request.POST.getlist('excuse_lateness')
    post_comments = request.POST.getlist('comment')
    post_user_id = request.POST.getlist('user_id')

    for (i, prog_id) in enumerate(post_user_progress_id):
        the_grade = strip_tags(post_grade[i].strip())
        user_progress_model = {
            'grade': decimal.Decimal(the_grade) if the_grade is not '' else '',
            'assessment_uri': strip_tags(post_assessment_uri[i].strip()),
            'user_id': int(post_user_id[i]),
            'submitted_by': strip_tags(post_submitted_by[i].strip()),
            'excuse_lateness': post_excuse_lateness[i],
            'details': {
                'comment': post_comments[i].strip(),
            },
        }

        if post_grade[i].strip() is not '':
            if prog_id.strip() is '':
                posted_grades['create'].append(UserProgress(**user_progress_model))
            else:
                if assessment_uri_index:
                    current_user_progress = user_grades[assessment_uri_index[user_progress_model['assessment_uri']]]
                else:
                    current_user_progress = user_grades[user_id_index[user_progress_model['user_id']]]

                if (decimal.Decimal(current_user_progress.grade).quantize(grade_helper.TWO_DECIMALS) != decimal.Decimal(user_progress_model['grade']).quantize(grade_helper.TWO_DECIMALS)
                    or comment_is_different(current_user_progress.details, user_progress_model)
                    or empty_is_none(current_user_progress.excuse_lateness) != empty_is_none(user_progress_model['excuse_lateness'])
                    ):
                    current_user_progress.grade = user_progress_model['grade']
                    current_user_progress.submitted_by = f"{request.user.first_name} {request.user.last_name}"
                    current_user_progress.cheated = False
                    current_user_progress.excuse_lateness = user_progress_model['excuse_lateness']
                    if not isinstance(current_user_progress.details, dict): current_user_progress.details = {}
                    current_user_progress.details['comment'] = user_progress_model['details']['comment']
                    posted_grades['update'].append(current_user_progress)
        else:
            if prog_id.strip():
                if assessment_uri_index:
                    if user_progress_model['assessment_uri'] in assessment_uri_index:
                        posted_grades['delete'].append(user_grades[assessment_uri_index[user_progress_model['assessment_uri']]])
                else:
                    if user_progress_model['user_id'] in user_id_index:
                        posted_grades['delete'].append(user_grades[user_id_index[user_progress_model['user_id']]])

    for model_type in ('update', 'create'):
        for prog in posted_grades[model_type]:
            try:
                prog.full_clean()
                prog.save()
            except:
                pass

    for prog in posted_grades['delete']:
        try:
            prog.delete()
        except:
            pass


@staff_member_required(login_url='core:sign_in')
def courses(request):
    terms = Term.objects.filter(end_date__gte=datetime.date(1982, 10, 28))[:2]
    courses = Course.objects.filter(term__in=terms)

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Courses · Teachers",
        'username': request.user.username,
        'courses': courses,
        'nav_current': 'teachers',
        'h1_title': "Teachers ·",
        'hide_markbot': True,
    }

    for course in context['courses']:
        course.data['totals']['students'] = Course.objects.get(pk=course.pk).profiles.count()

    return render(request, 'core/teachers/courses.html', context)


@staff_member_required(login_url='core:sign_in')
def course_status(request, term_id, course_id):
    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
    except:
        return redirect('core:teacher_courses')

    students = UserProfile.objects.filter(current_course=course).select_related('user').order_by('user__last_name', 'user__first_name')
    assessment_index = build_dict_index(course.data['assessments'], 'uri')
    all_grades = UserProgress.objects.filter(user_id__in=(s.user_id for s in students))
    max_assessments_per_section = grade_helper.max_assessments_per_section(course.data['assessments'])
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
        student_grades = (grade_helper.calc_grade(g, assessment_index, course.data['assessments']) for g in all_grades if g.user_id == student.user_id)
        student.current_grade = decimal.Decimal(math.fsum(student_grades))
        student.current_grade_max = max_assessments_per_section[student.current_section]
        student.current_grade_average = student.current_grade / student.current_grade_max if student.current_grade_max > 0 else 0
        stats_grade_total += student.current_grade_average
        stats_actual_total += student.current_grade
        stats_max_total += student.current_grade_max
        stats_grade_status[grade_helper.grade_as_status(student.current_grade_average)] += 1

    for prog in all_grades:
        if prog.assessment_uri in assessment_index and prog.grade > 0:
            if 'total_students_pass' not in course.data['assessments'][assessment_index[prog.assessment_uri]]:
                course.data['assessments'][assessment_index[prog.assessment_uri]]['total_students_pass'] = 0
            course.data['assessments'][assessment_index[prog.assessment_uri]]['total_students_pass'] += 1

    for assessment in course.data['assessments']:
        if 'total_students_pass' in assessment:
            assessment['total_students_pass_rate'] = assessment['total_students_pass'] / students.count()
        else:
            assessment['total_students_pass_rate'] = 0
        stats_pass_rate_total += assessment['total_students_pass_rate']

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{course.data['title']} · Teachers",
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': f"{course.data['title']} ·",
        'hide_markbot': True,
        'course': course,
        'students': students,
        'stats_grade_avg': stats_grade_total / students.count() if students.count() > 0 else 0,
        'stats_actual_avg': stats_actual_total / students.count() if students.count() > 0 else 0,
        'stats_max_avg': stats_max_total / students.count() if students.count() > 0 else 0,
        'stats_grade_status': stats_grade_status,
        'stats_assessments_total': len(course.data['assessments']),
        'stats_assessments_no_zeros': len(course.data['assessments']) - len([a for a in course.data['assessments'] if a['assessment_each_algonquin'] <= 0]),
        'stats_pass_rate_avg': stats_pass_rate_total / len(course.data['assessments']),
    }

    return render(request, 'core/teachers/course-status.html', context)


@staff_member_required(login_url='core:sign_in')
def user_grades(request, term_id, course_id, user_id):
    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
        student_profile = UserProfile.objects.get(user=user_id, current_course=course)
    except:
        return redirect('core:teacher_courses')

    user_grades = list(UserProgress.objects.filter(user=user_id))
    current_grade = decimal.Decimal(0.0)
    all_students = UserProfile.objects.filter(current_course=course).select_related('user').order_by('user__last_name', 'user__first_name')
    max_assessments_per_section = grade_helper.max_assessments_per_section(course.data['assessments'])

    for a in course.data['assessments']:
        if student_profile and 'due_dates_algonquin' in a and student_profile.current_section in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = pendulum.parse(a['due_dates_algonquin'][student_profile.current_section], tz='America/Toronto')

    if student_profile and student_profile.current_section:
        course.data['assessments'] = sorted(course.data['assessments'], key=lambda k: k['user_due_date_algonquin'])
    assessment_index = build_dict_index(course.data['assessments'], 'uri')

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if (prog.created
                and 'user_due_date_algonquin' in course.data['assessments'][assessment_index[prog.assessment_uri]]
                and prog.created > course.data['assessments'][assessment_index[prog.assessment_uri]]['user_due_date_algonquin']
                and (prog.excuse_lateness == 'LATENESS_NOT_EXCUSED' or not prog.excuse_lateness)
                ):
                prog.late = True
            if prog.details and 'started' in prog.details: prog.details['started'] = pendulum.parse(prog.details['started'])
            if prog.details and 'finished' in prog.details: prog.details['finished'] = pendulum.parse(prog.details['finished'])
            course.data['assessments'][assessment_index[prog.assessment_uri]]['grade'] = prog
            current_grade += grade_helper.calc_grade(prog, assessment_index, course.data['assessments'])

    current_grade_max = max_assessments_per_section[student_profile.current_section]

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{student_profile.user.first_name} {student_profile.user.last_name} · Teachers",
        'username': request.user.username,
        'submitted_by': f"{request.user.first_name} {request.user.last_name}",
        'github_username': student_profile.user.username,
        'nav_current': 'teachers',
        'h1_title': f"{student_profile.user.first_name} {student_profile.user.last_name} ·",
        'allow_grade_editing': True,
        'hide_markbot': True,
        'current_grade': current_grade,
        'current_grade_max': current_grade_max,
        'current_grade_average': current_grade / current_grade_max if current_grade_max > 0 else 0,
        'course': course,
        'excuse_lateness_options': UserProgressLatenessChoices.choices(),
        'today': pendulum.now(tz='America/Toronto'),
        'student_details': {
            'full_name': f"{student_profile.user.first_name} {student_profile.user.last_name}",
            'github_url': f"https://github.com/{student_profile.user.username}",
        },
        'all_students': all_students,
    }

    if student_profile:
        context['student_profile'] = student_profile

    return render(request, 'core/grades.html', context)


@staff_member_required(login_url='core:sign_in')
def user_grades_save(request, term_id, course_id, user_id):
    if request.method != 'POST' and 'user_progress_id' not in request.POST:
        return redirect('core:teacher_user_grades', term_id=term_id, course_id=course_id, user_id=user_id)

    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
    except:
        return redirect('core:teacher_courses')

    user_grades = list(UserProgress.objects.filter(user=user_id))
    assessment_uri_index = build_queryset_index(user_grades, 'assessment_uri')

    crud_grades(request=request, user_grades=user_grades, assessment_uri_index=assessment_uri_index)

    return redirect('core:teacher_user_grades', term_id=term_id, course_id=course_id, user_id=user_id)


@staff_member_required(login_url='core:sign_in')
def assessment_grades(request, term_id, course_id, assessment_id):
    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
    except:
        return redirect('core:teacher_courses')

    students = UserProfile.objects.filter(current_course=course).select_related('user').order_by('user__last_name', 'user__first_name')
    student_grades = list(UserProgress.objects.filter(user__in=[s.user.id for s in students], assessment_uri=assessment_id))
    assessment_index = build_dict_index(course.data['assessments'], 'uri')
    student_grade_index = build_queryset_index(student_grades, 'user_id')
    all_student_grades = []
    stats_pass_rate_total = 0
    show_markbot_stats = False
    markbot_commits_min = 10000000
    markbot_commits_max = 0
    markbot_commits_total = 0
    markbot_time_min = 10000000
    markbot_time_max = 0
    markbot_time_total = 0

    if assessment_id not in assessment_index:
        return redirect('core:teacher_courses')

    assessment = course.data['assessments'][assessment_index[assessment_id]]

    for student in students:
        grade_info = assessment.copy()
        if student.user.id in student_grade_index:
            grade_info['grade'] = model_to_dict(student_grades[student_grade_index[student.user.id]])

            if grade_info['grade']['grade'] > 0:
                stats_pass_rate_total += 1;

            if grade_info['grade']['details'] and 'number_of_commits' in grade_info['grade']['details']:
                show_markbot_stats = True
                markbot_commits_total += grade_info['grade']['details']['number_of_commits']
                if grade_info['grade']['details']['number_of_commits'] < markbot_commits_min:
                    markbot_commits_min = grade_info['grade']['details']['number_of_commits']
                if grade_info['grade']['details']['number_of_commits'] > markbot_commits_max:
                    markbot_commits_max = grade_info['grade']['details']['number_of_commits']

            if grade_info['grade']['details'] and 'estimated_time' in grade_info['grade']['details']:
                show_markbot_stats = True
                markbot_time_total += float(grade_info['grade']['details']['estimated_time'])
                if float(grade_info['grade']['details']['estimated_time']) < markbot_time_min:
                    markbot_time_min = float(grade_info['grade']['details']['estimated_time'])
                if float(grade_info['grade']['details']['estimated_time']) > markbot_time_max:
                    markbot_time_max = float(grade_info['grade']['details']['estimated_time'])

        grade_info['name'] = f"{student.user.last_name}, {student.user.first_name}"
        grade_info['user_id'] = student.user.id
        grade_info['student_section'] = student.current_section
        grade_info['github_username'] = student.user.username
        grade_info['assessment_each_algonquin'] = assessment['assessment_each_algonquin']
        grade_info['user_due_date_algonquin'] = pendulum.parse(assessment['due_dates_algonquin'][student.current_section])
        if 'grade' in grade_info:
            grade_info['grade']['late'] = False
            if ('created' in grade_info['grade']
                and grade_info['grade']['created']
                and grade_info['grade']['created'] > grade_info['user_due_date_algonquin']
                and (grade_info['grade']['excuse_lateness'] == 'LATENESS_NOT_EXCUSED' or not grade_info['grade']['excuse_lateness'])
                ):
                grade_info['grade']['late'] = True
        all_student_grades.append(grade_info)

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{assessment['name']} · Teachers",
        'username': request.user.username,
        'submitted_by': f"{request.user.first_name} {request.user.last_name}",
        'nav_current': 'teachers',
        'h1_title': f"{assessment['name']} ·",
        'hide_markbot': True,
        'allow_grade_editing': True,
        'course': course,
        'students': students,
        'assessment': assessment,
        'excuse_lateness_options': UserProgressLatenessChoices.choices(),
        'all_student_grades': all_student_grades,
        'stats_total_submissions': len(student_grades),
        'stats_pass_rate_avg': stats_pass_rate_total / len(students),
        'show_markbot_stats': show_markbot_stats,
        'markbot_commits_min': markbot_commits_min,
        'markbot_commits_max': markbot_commits_max,
        'markbot_commits_avg': round(markbot_commits_total / len(students)),
        'markbot_time_min': round(markbot_time_min, 2),
        'markbot_time_max': round(markbot_time_max, 2),
        'markbot_time_avg': round(markbot_time_total / len(students), 1),
    }
    return render(request, 'core/teachers/assessment-grades.html', context)


@staff_member_required(login_url='core:sign_in')
def assessment_grades_save(request, term_id, course_id, assessment_id):
    if request.method != 'POST' and 'user_progress_id' not in request.POST:
        return redirect('core:teacher_assessment_grades', term_id=term_id, course_id=course_id, assessment_id=assessment_id)

    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
    except:
        return redirect('core:teacher_courses')

    students = UserProfile.objects.filter(current_course=course).select_related('user').order_by('user__last_name', 'user__first_name')
    user_grades = list(UserProgress.objects.filter(user__in=[s.user.id for s in students], assessment_uri=assessment_id))
    user_id_index = build_queryset_index(user_grades, 'user_id')

    crud_grades(request=request, user_grades=user_grades, user_id_index=user_id_index)

    return redirect('core:teacher_assessment_grades', term_id=term_id, course_id=course_id, assessment_id=assessment_id)
