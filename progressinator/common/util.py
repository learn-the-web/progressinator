import re
import decimal
from enum import Enum
from collections import namedtuple, OrderedDict
from functools import partial
from django.utils import numberformat
from django.db import models
from django.db.models.fields.related import ManyToManyField


ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M'
DECIMAL_PERCENT = decimal.Decimal('0.00000000')
DECIMAL_PERCENT_HUMANIZED = decimal.Decimal('0.000000')
DECIMAL_PERCENT_SMALL = decimal.Decimal('0.000')
DECIMAL_PERCENT_SMALL_HUMANIZED = decimal.Decimal('0.0')


def classify(item):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9-]', '-', item.lower()))


def classify_underscores(item):
    return classify(item).replace('-', '_')


def sum_list_prop(lst, prop):
    return sum([getattr(i, prop) for i in lst])


def model_to_dict(mod):
    dic = mod.__dict__
    if '_state' in dic: del dic['_state']
    if '_initial_state' in dic: del dic['_initial_state']
    return dic


def build_dict_index(seq, key):
    return dict((d[key], index) for (index, d) in enumerate(seq))


def build_queryset_index(seq, key):
    return {getattr(d, key): index for (index, d) in enumerate(seq)}


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)

    @classmethod
    def choice_values(cls):
        return tuple((x.value, x.value) for x in cls)

    @classmethod
    def _(cls, x):
        return str(cls[x].name)

    def __str__(self):
        return str(self.name)


class NumberFormatter():
    @classmethod
    def percent(cls, val, small=False):
        decimal_format = DECIMAL_PERCENT if not small else DECIMAL_PERCENT_SMALL
        return decimal.Decimal(val).quantize(decimal_format)

    @classmethod
    def percent_humanize(cls, val, small=False, strip=False):
        decimal_format = DECIMAL_PERCENT_HUMANIZED if not small else DECIMAL_PERCENT_SMALL_HUMANIZED
        val = str(decimal.Decimal(val * 100).quantize(decimal_format))
        if strip: val = val.rstrip('0').rstrip('.')
        return val + '%'
