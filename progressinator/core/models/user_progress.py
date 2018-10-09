import decimal
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django_lifecycle import LifecycleModelMixin, hook


class UserProgress(LifecycleModelMixin, models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    submitted_by = models.CharField(max_length=256, null=True)
    signature = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    assessment_uri = models.CharField(max_length=256, null=True)
    grade = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    cheated = models.NullBooleanField(default=False)
    details = JSONField(blank=True, null=True)

    @property
    def grade_as_letter(self):
        if (self.grade >= .9):
            return "A+"
        elif self.grade >= .85 and self.grade < .9:
            return "A"
        elif self.grade >= .80 and self.grade < .85:
            return "A-"
        elif self.grade >= .77 and self.grade < .80:
            return "B+"
        elif self.grade >= .73 and self.grade < .77:
            return "B"
        elif self.grade >= .70 and self.grade < .73:
            return "B-"
        elif self.grade >= .67 and self.grade < .70:
            return "C+"
        elif self.grade >= .63 and self.grade < .67:
            return "C"
        elif self.grade >= .60 and self.grade < .63:
            return "C-"
        elif self.grade >= .57 and self.grade < .60:
            return "D+"
        elif self.grade >= .53 and self.grade < .57:
            return "D"
        elif self.grade >= .50 and self.grade < .53:
            return "D-"
        else:
            return "F"

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
