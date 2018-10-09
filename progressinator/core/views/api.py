from django.http import HttpResponse, JsonResponse
from django.conf import settings

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view

from progressinator.core.lib import MarkbotHelper
from progressinator.core.models import UserProgress
from progressinator.core.serializers import UserProgressSerializer


@api_view(['POST'])
def submit_assessment(request):
    data = JSONParser().parse(request)
    serializer = UserProgressSerializer(data=data)

    if serializer.is_valid():
        if data['github_username'] != request.user.username:
            return JsonResponse({
                'error': status.HTTP_401_UNAUTHORIZED,
                'detail': "The GitHub username does not match the authenticated API token",
                }, status=status.HTTP_401_UNAUTHORIZED)

        if 'Markbot' in serializer.validated_data['submitted_by']:
            if not MarkbotHelper.confirm_version(serializer.validated_data['submitted_by']):
                return JsonResponse({
                    'error': status.HTTP_406_NOT_ACCEPTABLE,
                    'detail': f"Markbot version too old, expecting >= Markbot/{settings.MARKBOT['DESKTOP_VERSION']} or Markbot Online/{settings.MARKBOT['ONLINE_VERSION']}",
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)

        # return HttpResponse(MarkbotHelper.generate_signature(data['github_username'], serializer.validated_data))
        if not MarkbotHelper.confirm_signature(data['github_username'], serializer.validated_data):
            return JsonResponse({
                'error': status.HTTP_406_NOT_ACCEPTABLE,
                'detail': "Incomplete or missing arguments—double check you have the most recent version of Markbot",
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

        previousSubmission = UserProgress.objects.filter(user=request.user, assessment_uri=serializer.validated_data['assessment_uri'])

        if previousSubmission.count() > 0:
            return JsonResponse({
                'error': status.HTTP_409_CONFLICT,
                'detail': "Assessment has already been graded",
                }, status=status.HTTP_409_CONFLICT)

        serializer.save(user=request.user)

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    return JsonResponse(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
