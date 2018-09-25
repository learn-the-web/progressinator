from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


@login_required
def grades(request):
    context = {
        'doc_title': 'Grades',
        'username': request.user.username,
        'email': request.user.email,
    }
    return render(request, 'core/grades.html', context)

