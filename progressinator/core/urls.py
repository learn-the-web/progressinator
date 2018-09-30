from django.urls import path
from progressinator.core.views import auth, grades, profile


app_name = 'core'

urlpatterns = [
    path('', grades.courses, name='courses'),
    path('courses/<slug:course_id>/', grades.course_grades, name='grades'),
    path('auth/sign-in/', auth.signin, name='sign_in'),
    path('auth/sign-out/', auth.signout, name='sign_out'),
    path('profile/', profile.index, name='profile'),
    path('api/v1/submit-assessment', grades.submit_assessment, name='submit'),
]
