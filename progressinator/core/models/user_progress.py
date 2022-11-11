import decimal
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django_lifecycle import LifecycleModelMixin, hook
from django import forms

from progressinator.common import grades
from progressinator.common.util import ChoiceEnum


class UserProgressLatenessChoices(ChoiceEnum):
    LATENESS_ABSENT = 'Absent'
    LATENESS_SICK = 'Sick'
    LATENESS_PERSONAL = 'Personal'
    LATENESS_EXCEPTION = 'Exception'
    LATENESS_NOT_EXCUSED = 'Not excused'


class UserProgress(LifecycleModelMixin, models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    submitted_by = models.CharField(max_length=256, null=True)
    signature = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    assessment_uri = models.CharField(max_length=256, null=True)
    grade = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    cheated = models.NullBooleanField(default=False)
    excuse_lateness = models.CharField(choices=UserProgressLatenessChoices.choices(), max_length=50, blank=True, null=True)
    details = JSONField(blank=True, null=True)

    @property
    def grade_as_letter(self):
        return grades.grade_as_letter(self.grade)

    @hook('before_save')
    def _save_grade(self):
        if self.cheated:
            self.grade = 0

    def __str__(self):
        if self.cheated:
            return f'{self.user.username} — {self.assessment_uri} — {self.grade} — cheated'
        else:
            return f'{self.user.username} — {self.assessment_uri} — {self.grade}'

    class Meta:
        verbose_name = "user progress"
        verbose_name_plural = "user progress"
        get_latest_by = 'created'
        ordering = ('created',)


class UserProgressForm(forms.ModelForm):
    class Meta:
        model = UserProgress
        exclude = ('user', 'created', 'signature', 'cheated', 'details')
        widgets = {
            'submitted_by': forms.HiddenInput(),
            'user': forms.HiddenInput(),
            'assessment_uri': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UserProgressForm, self).__init__(*args, **kwargs)
        self.fields['grade'].required = False
