from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    current_course = models.ForeignKey('Course', on_delete=models.CASCADE, blank=True, null=True)
    current_section = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} — {self.assessment_uri} — {self.grade}'

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "user profile"
        get_latest_by = 'created'
        ordering = ('user',)
