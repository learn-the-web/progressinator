from progressinator.common.util import model_to_dict


class CourseHelper:

    @classmethod
    def user_profiles_as_dict(cls, user_profiles):
        user_profiles_dict = {}
        for u in user_profiles:
            user_profiles_dict[u.current_course.slug] = {
                'current_term_id': u.current_course.term_id,
                'current_term_slug': u.current_course.term.slug,
                'current_term_name': u.current_course.term.name,
                'current_course_id': u.current_course_id,
                'current_course_slug': u.current_course.slug,
                'current_section': u.current_section,
            }
        return user_profiles_dict


    @classmethod
    def courses_as_dict(cls, courses):
        courses_dict = {}
        for c in courses:
            if c.slug not in courses_dict:
                courses_dict[c.slug] = model_to_dict(c)
        return courses_dict
