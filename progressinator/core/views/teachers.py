import decimal, math
import pendulum

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils.html import strip_tags
from django import forms

from progressinator.common.util import build_dict_index, build_queryset_index
import progressinator.common.grades as grade_helper
from progressinator.core.models import UserProgress, UserProgressForm, UserProgressLatenessChoices, UserProfile, Course, Term
from progressinator.core.serializers import UserProgressSerializer


@staff_member_required(login_url='core:sign_in')
def courses(request):
    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Courses · Teachers",
        'username': request.user.username,
        'courses': Course.objects.all(),
        'nav_current': 'teachers',
        'h1_title': "Teachers ·",
        'hide_markbot': True,
    }

    for course in context['courses']:
        course.data['totals']['students'] = Course.objects.get(slug=course.slug).profiles.count()

    return render(request, 'core/teachers/courses.html', context)


@staff_member_required(login_url='core:sign_in')
def course_status(request, course_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Course.objects.get(slug=course_id)
    except:
        return redirect('core:teacher_courses')

    students = UserProfile.objects.filter(current_course=course_in_db).select_related('user').order_by('user__last_name', 'user__first_name')
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
        student.current_grade_average = student.current_grade / student.current_grade_max
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
def user_grades(request, course_id, user_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Course.objects.get(slug=course_id)
    except:
        return redirect('core:teacher_courses')

    try:
        student_profile = UserProfile.objects.get(user=user_id)
    except:
        student_profile = None

    user_grades = list(UserProgress.objects.filter(user=user_id))
    current_grade = decimal.Decimal(0.0)
    max_assessments_per_section = grade_helper.max_assessments_per_section(course.data['assessments'])

    for a in course.data['assessments']:
        if a['assessment_each_algonquin'] > 0:
            a['FORM'] = UserProgressForm(initial={
                'user': student_profile,
                'submitted_by': f"{request.user.first_name} {request.user.last_name}",
                'assessment_uri': a['uri'],
            })
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
            if 'FORM' in course.data['assessments'][assessment_index[prog.assessment_uri]]:
                course.data['assessments'][assessment_index[prog.assessment_uri]]['FORM'] = UserProgressForm(instance=prog)

    current_grade_max = max_assessments_per_section[student_profile.current_section]

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': f"{student_profile.user.first_name} {student_profile.user.last_name} · Teachers",
        'username': request.user.username,
        'github_username': student_profile.user.username,
        'nav_current': 'teachers',
        'h1_title': f"{student_profile.user.first_name} {student_profile.user.last_name} ·",
        'allow_grade_editing': True,
        'hide_markbot': True,
        'current_grade': current_grade,
        'current_grade_max': current_grade_max,
        'current_grade_average': current_grade / current_grade_max,
        'course': course,
        'excuse_lateness_options': UserProgressLatenessChoices.choices(),
        'today': pendulum.now(tz='America/Toronto')
    }

    if student_profile:
        context['student_profile'] = student_profile

    return render(request, 'core/grades.html', context)


@staff_member_required(login_url='core:sign_in')
def user_grades_save(request, course_id, user_id):
    if request.method != 'POST' and 'user_progress_id' not in request.POST:
        return redirect('core:teacher_user_grades', course_id=course_id, user_id=user_id)

    course_in_db = get_object_or_404(Course, slug=course_id);
    posted_grades = {'update': [], 'create': []}

    try:
        course = Course.objects.get(slug=course_id)
    except:
        return redirect('core:teacher_courses')

    try:
        student_profile = UserProfile.objects.get(user=user_id)
    except:
        student_profile = None

    def comment_is_different(data1, data2):
        comment1 = ''
        comment2 = ''

        if data1 and 'comment' in data1: comment1 = data1['comment']
        if 'details' in data2 and 'comment' in data2['details']: comment2 = data2['details']['comment']

        return comment1 != comment2

    user_grades = list(UserProgress.objects.filter(user=user_id))
    user_grades_index = build_queryset_index(user_grades, 'assessment_uri')

    post_user_progress_id = request.POST.getlist('user_progress_id')
    post_grade = request.POST.getlist('grade')
    post_assessment_uri = request.POST.getlist('assessment_uri')
    post_submitted_by = request.POST.getlist('submitted_by')
    post_excuse_lateness = request.POST.getlist('excuse_lateness')
    post_comments = request.POST.getlist('comment')

    for (i, prog_id) in enumerate(post_user_progress_id):
        the_grade = strip_tags(post_grade[i].strip())
        user_progress_model = {
            'grade': decimal.Decimal(the_grade) if the_grade is not '' else '',
            'assessment_uri': strip_tags(post_assessment_uri[i].strip()),
            'user_id': user_id,
            'submitted_by': strip_tags(post_submitted_by[i].strip()),
            'excuse_lateness': post_excuse_lateness[i],
        }
        if post_comments[i].strip() is not '':
            user_progress_model['details'] = {
                'comment': post_comments[i].strip()
            }

        if post_grade[i].strip() is not '':
            if prog_id.strip() is '':
                posted_grades['create'].append(UserProgress(**user_progress_model))
            else:
                current_user_progress = user_grades[user_grades_index[user_progress_model['assessment_uri']]]

                if (current_user_progress.grade != user_progress_model['grade']
                    or comment_is_different(current_user_progress.details, user_progress_model)
                    or current_user_progress.excuse_lateness != user_progress_model['excuse_lateness']
                    ):
                    current_user_progress.grade = user_progress_model['grade']
                    current_user_progress.submitted_by = f"{request.user.first_name} {request.user.last_name}"
                    current_user_progress.cheated = False
                    current_user_progress.excuse_lateness = user_progress_model['excuse_lateness']
                    if 'details' in user_progress_model:
                        if not isinstance(current_user_progress.details, dict): current_user_progress.details = {}
                        current_user_progress.details['comment'] = user_progress_model['details']['comment']
                    posted_grades['update'].append(current_user_progress)

    for model_type in ('update', 'create'):
        for prog in posted_grades[model_type]:
            try:
                prog.full_clean()
                prog.save()
            except:
                pass

    # return render(request, 'core/teachers/assessment-grades.html')
    return redirect('core:teacher_user_grades', course_id=course_id, user_id=user_id)


@staff_member_required(login_url='core:sign_in')
def assessment_grades(request, course_id, assessment_id):
    course_in_db = get_object_or_404(Course, slug=course_id);

    try:
        course = Course.objects.get(slug=course_id)
    except:
        return redirect('core:teacher_courses')

    context = {
        'app_version': settings.APP_PKG['version'],
        'doc_title': "Assessment · Teachers",
        'username': request.user.username,
        'nav_current': 'teachers',
        'h1_title': "Assessment ·",
        'hide_markbot': True,
    }
    return render(request, 'core/teachers/assessment-grades.html', context)
