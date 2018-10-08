import decimal
import dateutil.parser
from datetime import date, datetime
import simplejson as json


registered_courses = ('web-dev-1', 'web-dev-2', 'web-dev-3', 'web-dev-4', 'web-dev-5', 'web-dev-6', 'javascript')


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError ("Type %s not serializable" % type(obj))


def setup_course(course):
    for k, v in course['grading_scheme'].items():
        tmpkey = k + '_each'
        course['totals'][tmpkey] = decimal.Decimal(v / course['totals'][k] / 100)
        course['grading_scheme'][k] = decimal.Decimal(v / 100)

    for k, v in course['grading_scheme_algonquin'].items():
        tmpkey = k +'_each_algonquin'
        course['totals'][tmpkey] = decimal.Decimal(v / course['totals'][k] / 100)
        course['grading_scheme_algonquin'][k] = decimal.Decimal(v / 100)

    for a in course['assessments']:
        a['assessment_each'] = course['totals']['exercises_each']
        a['assessment_each_algonquin'] = course['totals']['exercises_each_algonquin']
        if 'activit' in a['assessment_type'] or 'lesson' in a['assessment_type']:
            a['assessment_each'] = course['totals']['activities_plus_lessons_each']
            a['assessment_each_algonquin'] = course['totals']['activities_plus_lessons_each_algonquin']
        if 'video' in a['assessment_type']:
            a['assessment_each'] = course['totals']['videos_each']
            a['assessment_each_algonquin'] = course['totals']['videos_each_algonquin']
        if 'project' in a['assessment_type']:
            a['assessment_each'] = course['totals']['videos_each']
            a['assessment_each_algonquin'] = course['totals']['projects_each_algonquin']

        if 'due_dates' in a:
            for dd in a['due_dates']:
                if 'due_dates_algonquin' not in a: a['due_dates_algonquin'] = {}
                a['due_dates_algonquin'][dd['course_section']] = dateutil.parser.isoparse(dd['due'])

    return course


for course_id in registered_courses:
    with open(f'config/courses/{course_id}.json') as json_data:
        course = setup_course(json.load(json_data))
        json.dump(course, open(f'config/courses/{course_id}-compiled.json', 'w'), indent=2, default=json_serial)
