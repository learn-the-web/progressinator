from django.urls import path
from progress.core.views import auth, grades


app_name = 'core'

urlpatterns = [
    path('', grades.courses, name='courses'),
    path('courses/<slug:course_id>/', grades.course_grades, name='grades'),
    path('sign-in/', auth.signin, name='sign_in'),
]
