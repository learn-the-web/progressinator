import decimal, math, datetime, urllib
import pendulum
import csv

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view

from progressinator.core.lib import MarkbotHelper
from progressinator.core.models import UserProgress
from progressinator.common.util import build_dict_index, build_queryset_index, model_to_dict, NumberFormatter
import progressinator.common.grades as grade_helper
from progressinator.core.models import Term, Course, UserProgress, UserProgressForm, UserProgressLatenessChoices, UserProfile
from progressinator.core.serializers import UserProgressSerializer


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


@login_required
def user_grades_download(request, term_id, course_id, user_id):
    if not request.user.is_staff and request.user.id != user_id:
        return HttpResponse('Not authorized.', status=status.HTTP_401_UNAUTHORIZED, content_type='text/plain')

    try:
        term = Term.objects.get(slug=term_id)
        course = Course.objects.get(slug=course_id, term=term)
        student_profile = UserProfile.objects.get(user=user_id, current_course=course)
    except:
        return HttpResponse('URL parameters not acceptable.', status=status.HTTP_406_NOT_ACCEPTABLE, content_type='text/plain')

    user_grades = UserProgress.objects.filter(user=user_id)
    current_grade = decimal.Decimal(0.0)
    max_assessments_per_section = grade_helper.max_assessments_per_section(course.data['assessments'])

    for a in course.data['assessments']:
        if student_profile and 'due_dates_algonquin' in a and student_profile.current_section in a['due_dates_algonquin']:
            a['user_due_date_algonquin'] = pendulum.parse(a['due_dates_algonquin'][student_profile.current_section])

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

    if student_profile and student_profile.current_course.slug == course_id and student_profile.current_section in max_assessments_per_section:
        current_grade_max = max_assessments_per_section[student_profile.current_section]
    else:
        current_grade_max = False

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    # response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{urllib.parse.quote_plus(student_profile.user.last_name)}-{urllib.parse.quote_plus(student_profile.user.first_name)}-{course.slug}-{term.slug}.csv"
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)

    first_row = ['Name:', f"{student_profile.user.first_name} {student_profile.user.last_name}"]

    if current_grade_max:
        first_row += ['', grade_helper.grade_as_letter(current_grade / current_grade_max), NumberFormatter.percent_humanize(current_grade / current_grade_max, small=True) + "/" + NumberFormatter.percent_humanize(current_grade_max, small=True)]

    writer.writerow(first_row)
    writer.writerow(['GitHub:', f"{student_profile.user.username}"])
    writer.writerow(['Term:', term.name])
    writer.writerow(['Course:', f"{course.data['title']} ({course.data['course_code']})"])
    writer.writerow(['Professors:', ", ".join([p['name'] for p in course.data['professors']])])
    writer.writerow(['Start date:', pendulum.parse(f"{course.data['year']}-W{str(course.data['start_week']).rjust(2, '0')}-1", tz='America/Toronto').to_formatted_date_string()])
    writer.writerow(['End date:', pendulum.parse(f"{course.data['year']}-W{str(course.data['start_week'] + 15).rjust(2, '0')}-5", tz='America/Toronto').to_formatted_date_string()])
    writer.writerow(['Section:', student_profile.current_section])

    if 'sections' in course.data:
        section_data = [s for s in course.data['sections'] if s['title'] == student_profile.current_section]
        start_time = pendulum.parse(f"{course.data['year']}-W{str(course.data['start_week']).rjust(2, '0')}-{section_data[0]['day']}T{str(section_data[0]['start_time']).rjust(2, '0')}:00", tz='America/Toronto')
        end_time = pendulum.parse(f"{course.data['year']}-W{str(course.data['start_week']).rjust(2, '0')}-{section_data[0]['day']}T{str(section_data[0]['start_time'] + 3).rjust(2, '0')}:00", tz='America/Toronto')
        writer.writerow(['Class time:', f"{start_time.format('ddd, h:mm A')} - {end_time.format('h:mm A')} @ {section_data[0]['room']}"])
    writer.writerow([''])
    writer.writerow(['Assessment', 'Grade', 'Worth', 'Graded by', 'Submission time', 'Late?', 'Lateness exception', 'Cheated?', 'Started', 'Finished', 'Estimated completion', 'No. commits', 'Comments'])

    for assessment in course.data['assessments']:
        if assessment['assessment_each_algonquin'] > 0:
            assess_details = []
            assess_details.append(assessment['name'])
            if 'grade' in assessment:
                assess_details.append(NumberFormatter.percent_humanize(assessment['grade'].grade, small=True))
                assess_details.append(NumberFormatter.percent_humanize(assessment['assessment_each_algonquin'], small=True))
                assess_details.append(assessment['grade'].submitted_by)
                assess_details.append(pendulum.instance(assessment['grade'].created).in_tz(tz='America/Toronto').to_datetime_string())
                assess_details.append('Late' if assessment['grade'].late else '')
                assess_details.append(assessment['grade'].excuse_lateness)
                assess_details.append('Cheated' if assessment['grade'].cheated else '')
                if assessment['grade'].details:
                    assess_details.append(pendulum.instance(assessment['grade'].details['started']).in_tz(tz='America/Toronto').to_datetime_string() if 'started' in assessment['grade'].details else '')
                    assess_details.append(pendulum.instance(assessment['grade'].details['finished']).in_tz(tz='America/Toronto').to_datetime_string() if 'finished' in assessment['grade'].details else '')
                    assess_details.append(f"~{assessment['grade'].details['estimated_time']} h" if 'estimated_time' in assessment['grade'].details else '')
                    assess_details.append(assessment['grade'].details['number_of_commits'] if 'number_of_commits' in assessment['grade'].details else '')
                    assess_details.append(assessment['grade'].details['comment'] if 'comment' in assessment['grade'].details else '')
            # else:
            #     assess_details += ['' for i in range(0, 10)]
            writer.writerow(assess_details)

    return response
