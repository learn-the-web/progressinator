import simplejson as json

from progressinator.core.lib import CourseNotFoundError


registered_courses = ('web-dev-1', 'web-dev-2', 'web-dev-3', 'web-dev-4', 'web-dev-5', 'web-dev-6', 'javascript')


class Courses:

    @classmethod
    def all(cls):
        courses = []

        for course_id in registered_courses:
            try:
                with open(f'config/courses/{course_id}-compiled.json') as json_data:
                    d = json.load(json_data)
                    courses.append(d)
            except FileNotFoundError:
                pass

        return courses


    @classmethod
    def get(cls, course_id):
        if course_id not in registered_courses:
            raise CourseNotFoundError("The course is not a registered Learn the Web course.")

        try:
            with open(f'config/courses/{course_id}-compiled.json') as json_data:
                d = json.load(json_data)
                return d
        except FileNotFoundError:
            raise CourseNotFoundError("The course details cannot be found in the system.")
