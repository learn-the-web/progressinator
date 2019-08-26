import re
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
def icon(slug):
    if slug[-1].isnumeric():
        return f"#icon-topic-{slug[-1]}"
    return '#icon-topic-infinite'


@register.filter
def course_grade_meter(grades, slug):
    if slug not in grades:
        return 710
    return 710 - (grades[slug]['grade'] * 710)


@register.filter
def course_grade_meter_tick(grades, slug):
    if slug not in grades:
        return 0
    return grades[slug]['current_grade_max'] * 360


@register.filter
def get_course_grade(grades, slug):
    if slug not in grades:
        return 0
    return grades[slug]['grade']
