import re
from django import template
from django.template.defaultfilters import stringfilter

from progressinator.common import grades


register = template.Library()


@register.filter
def grade_as_letter(value):
    return grades.grade_as_letter(value)


@register.filter
def grade_as_status(value):
    return grades.grade_as_status(value)
