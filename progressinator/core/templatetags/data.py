import re
from django import template
from django.template.defaultfilters import stringfilter
import phonenumbers
from progressinator.common.util import classify, NumberFormatter


register = template.Library()


@register.filter
@stringfilter
def numbersonly(value):
    """Remove everything that isn’t a number from the string"""
    return re.sub(r'[^\d]', '', value)

@register.filter
def times(value, num):
    """Multiply the number by a specific number"""
    return value * num

@register.filter
@stringfilter
def icon(value):
    """Fix the database version of an icon name to match the SVG ID"""
    return classify(value)

@register.filter
def pretty_percent(value):
    """Take a mathematical, database, percent and make it human readable"""
    if value >= 0: return NumberFormatter.percent_humanize(value)

@register.filter
def pretty_percent_small(value):
    """Take a mathematical, database, percent and make it human readable with a single decimal place"""
    if value >= 0: return NumberFormatter.percent_humanize(value, small=True)

@register.filter
def pretty_percent_strip(value):
    """Take a mathematical, database, percent and make it human readable also stripping trailing 0"""
    if value >= 0: return NumberFormatter.percent_humanize(value, strip=True)

@register.filter
def pretty_percent_raw(value):
    """Take a mathematical, database, percent and make it human readable"""
    if value >= 0: return value * 100

@register.filter
def append_value(value, append):
    """
    If a value exists, append something extra
    Kind of the opposite to the `default` filter
    """
    if value: return f"{value}{append}"
