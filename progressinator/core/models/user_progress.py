from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django_lifecycle import LifecycleModelMixin, hook


class UserProgress(LifecycleModelMixin, models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    submitted_by = models.CharField(max_length=256, null=True)
    signature = models.CharField(max_length=256, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    assessment_uri = models.CharField(max_length=256, null=True)
    grade = models.IntegerField(null=True)
    cheated = models.NullBooleanField(default=False)
    details = JSONField(blank=True, null=True)

    @hook('before_save')
    def _save_grade(self):
        if self.cheated:
            self.grade = 0

    def __str__(self):
        if self.cheated:
            return f'{self.user.username} — {self.assessment_uri} — {self.grade} — cheated'
        else:
            return f'{self.user.username} — {self.assessment_uri} — {self.grade}'

    class Meta:
        verbose_name = "user progress"
        verbose_name_plural = "user progress"
        get_latest_by = 'created'
        ordering = ('created',)
