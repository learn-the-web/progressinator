from django.conf import settings
from django.db import models
from progressinator.common.util import ChoiceEnum

class UserProfileSectionChoices(ChoiceEnum):
    SECTION_010 = '010'
    SECTION_020 = '020'
    SECTION_030 = '030'
    SECTION_040 = '040'

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    current_course = models.ForeignKey('Course', on_delete=models.SET_NULL, related_name='profiles', blank=True, null=True)
    current_section = models.CharField(choices=UserProfileSectionChoices.choice_values(), max_length=3, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} — {self.current_course.slug} — {self.current_section}'

    class Meta:
        verbose_name = "user profile"
        verbose_name_plural = "user profile"
        get_latest_by = 'created'
        ordering = ('id', 'user',)
