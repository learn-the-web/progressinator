import json
import decimal

from progressinator.core.lib import CourseNotFoundError


registered_courses = ('web-dev-1', 'web-dev-2', 'web-dev-3', 'web-dev-4', 'web-dev-5', 'web-dev-6', 'javascript')


class Courses:

    @classmethod
    def setup_course(cls, course):
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
            if 'activit' in a['assessment_type']:
                a['assessment_each'] = course['totals']['activities_each']
                a['assessment_each_algonquin'] = course['totals']['activities_each_algonquin']
            if 'video' in a['assessment_type']:
                a['assessment_each'] = course['totals']['videos_each']
                a['assessment_each_algonquin'] = course['totals']['videos_each_algonquin']
            if 'project' in a['assessment_type']:
                a['assessment_each'] = course['totals']['videos_each']
                a['assessment_each_algonquin'] = course['totals']['projects_each_algonquin']

        return course


    @classmethod
    def all(cls):
        courses = []

        for course_id in registered_courses:
            try:
                with open(f'config/courses/{course_id}.json') as json_data:
                    d = json.load(json_data)
                    courses.append(cls.setup_course(d))
            except FileNotFoundError:
                pass

        return courses


    @classmethod
    def get(cls, course_id):
        if course_id not in registered_courses:
            raise CourseNotFoundError("The course is not a registered Learn the Web course.")

        try:
            with open(f'config/courses/{course_id}.json') as json_data:
                d = json.load(json_data)
                return cls.setup_course(d)
        except FileNotFoundError:
            raise CourseNotFoundError("The course details cannot be found in the system.")
