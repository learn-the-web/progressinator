import re, decimal, json
from django import template
from django.template.defaultfilters import stringfilter
import phonenumbers
from progressinator.common.util import classify, NumberFormatter


register = template.Library()


@register.filter(is_safe=True)
def jsonify(var):
    return mark_safe(json.dumps(var, ensure_ascii=False, default=str))


@register.filter
@stringfilter
def numbersonly(value):
    """Remove everything that isn’t a number from the string"""
    return re.sub(r"[^\d]", "", value)


@register.filter
def times(value, num):
    """Multiply the number by a specific number"""
    if value is None or num is None:
        return None
    if isinstance(value, str):
        return value
    return value * num


@register.filter
def divided_by(value, num):
    """Divided the number by a specific number"""
    if value is None or num is None:
        return None
    if isinstance(value, str):
        return value
    return value / num


@register.filter
def plus(value, num):
    if value is None or num is None:
        return None
    if isinstance(value, str):
        return value
    return value + num


@register.filter
def minus(value, num):
    if value is None or num is None:
        return None
    if isinstance(value, str):
        return value
    return value - num


@register.filter
def absolute(value):
    return abs(value)


@register.filter
def bool_opposite(value):
    return not value


@register.filter
@stringfilter
def icon(value):
    """Fix the database version of an icon name to match the SVG ID"""
    return classify(value)


@register.filter
def pretty_percent(value):
    """Take a mathematical, database, percent and make it human readable"""
    if value:
        value = decimal.Decimal(value)
        if value >= 0:
            return NumberFormatter.percent_humanize(value)


@register.filter
def pretty_percent_small(value):
    """Take a mathematical, database, percent and make it human readable with a single decimal place"""
    if value:
        value = decimal.Decimal(value)
        if value >= 0:
            return NumberFormatter.percent_humanize(value, small=True)


@register.filter
def pretty_percent_strip(value):
    """Take a mathematical, database, percent and make it human readable also stripping trailing 0"""
    if value:
        value = decimal.Decimal(value)
        if value >= 0:
            return NumberFormatter.percent_humanize(value, strip=True)


@register.filter
def pretty_percent_raw(value):
    """Take a mathematical, database, percent and make it human readable"""
    if value:
        value = decimal.Decimal(value)
        if value >= 0:
            return value * 100


@register.filter
def append_value(value, append):
    """
    If a value exists, append something extra
    Kind of the opposite to the `default` filter
    """
    if value:
        return f"{value}{append}"


@register.filter
def time_24_to_12(time):
    if time > 12:
        return time - 12
    return time


@register.filter
def day_num_to_text(day):
    if day == 1:
        return "Mo."
    if day == 2:
        return "Tu."
    if day == 3:
        return "We."
    if day == 4:
        return "Th."
    if day == 5:
        return "Fr."
