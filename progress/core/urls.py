from django.urls import path
from progress.core.views import auth


app_name = 'core'

urlpatterns = [
    path('', auth.signin, name='sign_in'),
]
