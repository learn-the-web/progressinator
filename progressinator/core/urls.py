from django.urls import path
from progressinator.core.views import auth, grades, profile, api, teachers


app_name = 'core'

urlpatterns = [
    path('', grades.courses, name='courses'),
    path('courses/<slug:course_id>/', grades.course_grades, name='grades'),
    path('auth/sign-in/', auth.signin, name='sign_in'),
    path('auth/sign-out/', auth.signout, name='sign_out'),
    path('profile/', profile.index, name='profile'),
    path('teachers/courses/', teachers.courses, name='teacher_courses'),
    path('teachers/courses/<slug:course_id>/', teachers.course_status, name='teacher_course'),
    path('teachers/courses/<slug:course_id>/users/<int:user_id>/', teachers.user_grades, name='teacher_user_grades'),
    path('teachers/courses/<slug:course_id>/assessments/<int:assessment_id>/', teachers.assessment_grades, name='teacher_assessment_grades'),
    path('api/v1/submit-assessment', api.submit_assessment, name='submit'),
]
