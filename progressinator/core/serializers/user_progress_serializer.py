from rest_framework import serializers
from progressinator.core.models import UserProgress

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'
        read_only_fields = ('created', 'user', )
