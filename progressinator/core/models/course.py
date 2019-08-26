from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField


class Course(models.Model):
    slug = models.SlugField(null=True)
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name='courses', null=True)
    order = models.SmallIntegerField(blank=True, null=True)
    data = JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.data.title} ({self.data.course_code})"

    class Meta:
        verbose_name = "course"
        verbose_name_plural = "courses"
        ordering = ('term', 'order',)
