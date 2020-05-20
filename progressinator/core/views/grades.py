import decimal, math, datetime
import pendulum

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

import progressinator.common.grades as grade_helper
from progressinator.core.models import (
    Term,
    Course,
    UserProgress,
    UserProgressLatenessChoices,
    UserProfile,
)
from progressinator.core.serializers import UserProgressSerializer
from progressinator.common.util import build_dict_index
from progressinator.core.lib import CourseHelper


@login_required
def courses(request):
    try:
        user_profiles = UserProfile.objects.filter(user=request.user).select_related(
            "current_course", "current_course__term"
        )
    except:
        user_profiles = None

    courses = CourseHelper.courses_as_dict(
        Course.objects.filter(term=settings.COURSES["SELF_DIRECTED_ID"])
    )
    grades = {}
    user_courses = (
        CourseHelper.courses_as_dict(
            Course.objects.filter(id__in=(p.current_course_id for p in user_profiles))
        )
        if user_profiles
        else None
    )
    if user_courses:
        courses.update(user_courses)
    user_profiles_details = (
        CourseHelper.user_profiles_as_dict(user_profiles) if user_profiles else None
    )

    compare_date = datetime.date.today()
    # compare_date = datetime.date(2019, 9, 4)
    current_course = None
    current_week = None
    current_week_number = None
    next_week = None

    try:
        current_term = Term.objects.get(
            start_date__lte=compare_date, end_date__gte=compare_date
        )
        for slug, course in courses.items():
            if course["term_id"] == current_term.id:
                current_course = course
    except:
        current_term = None
        current_course = None

    user_grades = UserProgress.objects.filter(user=request.user)
    for slug, course in courses.items():
        user_profile = None
        grades[slug] = {}
        if user_profiles_details:
            for ups, up in user_profiles_details.items():
                if up["current_course_id"] == course["id"]:
                    user_profile = up
        grades[slug]["grade"] = decimal.Decimal(0)
        grades[slug][
            "max_assessments_per_section"
        ] = grade_helper.max_assessments_per_section(course["data"]["assessments"])
        assessment_index = build_dict_index(course["data"]["assessments"], "uri")
        for prog in user_grades:
            if prog.assessment_uri in assessment_index:
                grades[slug]["grade"] += grade_helper.calc_grade(
                    prog, assessment_index, course["data"]["assessments"]
                )
        if (
            user_profile
            and user_profile["current_course_slug"] == slug
            and user_profile["current_section"]
            in grades[slug]["max_assessments_per_section"]
        ):
            grades[slug]["current_grade_max"] = grades[slug][
                "max_assessments_per_section"
            ][user_profile["current_section"]]
        else:
            grades[slug]["current_grade_max"] = False

    if current_course and "weeks" in current_course["data"]:
        for week_number, week in current_course["data"]["weeks"].items():
            if "start_date" not in week or "end_date" not in week:
                continue
            if pendulum.instance(
                datetime.datetime.combine(compare_date, datetime.time.min)
            ) >= pendulum.parse(week["start_date"]) and pendulum.instance(
                datetime.datetime.combine(compare_date, datetime.time.min)
            ) <= pendulum.parse(
                week["end_date"]
            ):
                current_week = week
                current_week["start_date"] = pendulum.parse(current_week["start_date"])
                current_week["end_date"] = pendulum.parse(current_week["end_date"])
                current_week_number = int(week_number)
                break

    if current_week:
        if str(current_week_number + 1) in current_course["data"]["weeks"]:
            next_week = current_course["data"]["weeks"][str(current_week_number + 1)]
            next_week["start_date"] = pendulum.parse(next_week["start_date"])
            next_week["end_date"] = pendulum.parse(next_week["end_date"])

    context = {
        "app_version": settings.APP_PKG["version"],
        "doc_title": "Courses",
        "username": request.user.username,
        "courses": courses,
        "user_profiles_details": user_profiles_details,
        "nav_current": "courses",
        "current_term": current_term,
        "current_course": current_course,
        "grades": grades,
        "current_week": current_week,
        "next_week": next_week,
        "completed_assignments": [a.assessment_uri for a in user_grades],
    }

    if current_course:
        response = render(request, "core/courses-with-term.html", context)
    else:
        response = render(request, "core/courses-without-term.html", context)

    if user_profiles:
        user_profile_for_cookie = user_profiles.latest(
            "current_course__term__start_date"
        )
        response.set_cookie(
            "ltw-course-section",
            f"{user_profile_for_cookie.current_course.slug}-{user_profile_for_cookie.current_section}",
            max_age=settings.SESSION_COOKIE_AGE,
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE,
        )

    return response


@login_required
def course_grades(request, course_id):
    try:
        user_profiles = UserProfile.objects.filter(user=request.user).select_related(
            "current_course", "current_course__term"
        )
    except:
        user_profiles = None

    user_profiles_details = (
        CourseHelper.user_profiles_as_dict(user_profiles) if user_profiles else None
    )

    if user_profiles_details and course_id in user_profiles_details:
        user_profile = user_profiles_details[course_id]
        course = Course.objects.get(
            pk=user_profiles_details[course_id]["current_course_id"]
        )
    else:
        user_profile = None
        course = Course.objects.get(
            slug=course_id, term=settings.COURSES["SELF_DIRECTED_ID"]
        )

    if not course:
        return redirect("core:courses")

    user_grades = UserProgress.objects.filter(user=request.user)
    current_grade = decimal.Decimal(0.0)
    max_assessments_per_section = grade_helper.max_assessments_per_section(
        course.data["assessments"]
    )
    markbot_total_assessments = 0
    markbot_commits_min = 10000
    markbot_commits_max = 0
    markbot_commits_total = 0
    markbot_time_min = 10000
    markbot_time_max = 0
    markbot_time_total = 0

    for a in course.data["assessments"]:
        if (
            user_profile
            and "due_dates_algonquin" in a
            and user_profile["current_section"] in a["due_dates_algonquin"]
        ):
            a["user_due_date_algonquin"] = pendulum.parse(
                a["due_dates_algonquin"][user_profile["current_section"]]
            )

    if (
        user_profile
        and user_profile["current_section"]
        and user_profile["current_section"] in course.data["sections"]
    ):
        course.data["assessments"] = sorted(
            course.data["assessments"], key=lambda k: k["user_due_date_algonquin"]
        )
    assessment_index = build_dict_index(course.data["assessments"], "uri")

    for prog in user_grades:
        if prog.assessment_uri in assessment_index:
            prog.late = False
            if (
                prog.created
                and user_profile
                and user_profile["current_section"]
                and "user_due_date_algonquin"
                in course.data["assessments"][assessment_index[prog.assessment_uri]]
                and prog.created
                > course.data["assessments"][assessment_index[prog.assessment_uri]][
                    "user_due_date_algonquin"
                ]
                and (
                    prog.excuse_lateness == "LATENESS_NOT_EXCUSED"
                    or not prog.excuse_lateness
                )
            ):
                prog.late = True
            if prog.details and "started" in prog.details:
                prog.details["started"] = pendulum.parse(prog.details["started"])
            if prog.details and "finished" in prog.details:
                prog.details["finished"] = pendulum.parse(prog.details["finished"])
            course.data["assessments"][assessment_index[prog.assessment_uri]][
                "grade"
            ] = prog
            current_grade += grade_helper.calc_grade(
                prog, assessment_index, course.data["assessments"]
            )

            if prog.details and "number_of_commits" in prog.details:
                markbot_total_assessments += 1
                if (
                    prog.details["number_of_commits"] is not None
                    and prog.details["number_of_commits"] is not False
                    and int(prog.details["number_of_commits"] > 0)
                ):
                    markbot_commits_total += prog.details["number_of_commits"]
                    if prog.details["number_of_commits"] <= markbot_commits_min:
                        markbot_commits_min = prog.details["number_of_commits"]
                    if prog.details["number_of_commits"] >= markbot_commits_max:
                        markbot_commits_max = prog.details["number_of_commits"]

            if prog.details and "estimated_time" in prog.details:
                if (
                    prog.details["estimated_time"] is not None
                    and prog.details["estimated_time"] is not False
                    and float(prog.details["estimated_time"]) > 0
                ):
                    estimated_time = (
                        float(prog.details["estimated_time"])
                        if float(prog.details["estimated_time"]) <= 50
                        else 50
                    )
                    markbot_time_total += estimated_time
                    if estimated_time < markbot_time_min:
                        markbot_time_min = estimated_time
                    if estimated_time > markbot_time_max:
                        markbot_time_max = estimated_time

    if (
        user_profile
        and user_profile["current_course_slug"] == course_id
        and user_profile["current_section"] in max_assessments_per_section
    ):
        current_grade_max = max_assessments_per_section[user_profile["current_section"]]
    else:
        current_grade_max = False

    if markbot_total_assessments <= 0:
        markbot_total_assessments = 1
        markbot_commits_min = 0
        markbot_time_min = 0

    if markbot_commits_min >= 10000:
        markbot_commits_min = 0
    if markbot_time_min >= 10000:
        markbot_time_min = 0

    context = {
        "app_version": settings.APP_PKG["version"],
        "doc_title": f"Grades for {course.data['title']}",
        "h1_title": course.data["title"],
        "username": request.user.username,
        "github_username": request.user.username,
        "student_user_id": request.user.id,
        "current_grade": current_grade,
        "current_grade_max": current_grade_max,
        "current_grade_average": current_grade / current_grade_max
        if current_grade_max
        else False,
        "term": course.term,
        "course": course,
        "excuse_lateness_options": UserProgressLatenessChoices.choices(),
        "today": pendulum.now(tz="America/Toronto"),
        "markbot_commits_min": markbot_commits_min,
        "markbot_commits_max": markbot_commits_max,
        "markbot_commits_avg": round(markbot_commits_total / markbot_total_assessments),
        "markbot_time_min": round(markbot_time_min, 1),
        "markbot_time_max": round(markbot_time_max, 1),
        "markbot_time_avg": round(markbot_time_total / markbot_total_assessments, 1),
    }

    if user_profile:
        context["user_profile"] = user_profile

    response = render(request, "core/grades.html", context)

    if user_profiles:
        user_profile_for_cookie = user_profiles.latest(
            "current_course__term__start_date"
        )
        response.set_cookie(
            "ltw-course-section",
            f"{user_profile_for_cookie.current_course.slug}-{user_profile_for_cookie.current_section}",
            max_age=settings.SESSION_COOKIE_AGE,
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE,
        )

    return response
