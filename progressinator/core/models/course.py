from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=24, null=True)
    course_number = models.CharField(max_length=7, null=True)
    slug = models.SlugField(null=True)

    def __str__(self):
        return f"{self.name} ({self.course_number})"

    class Meta:
        verbose_name = "course"
        verbose_name_plural = "courses"
        ordering = ('name', 'course_number')
