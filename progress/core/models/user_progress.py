from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField


class UserProgress(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    assessment_uri = models.CharField(max_length=256, null=True)
    grade = models.IntegerField(null=True)
    details = JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} — {self.assessment_uri} — {self.grade}'

    class Meta:
        verbose_name = "user progress"
        verbose_name_plural = "user progress"
        get_latest_by = 'created'
        ordering = ('created',)
