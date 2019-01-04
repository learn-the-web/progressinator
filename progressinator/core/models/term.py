from django.conf import settings
from django.db import models


class Term(models.Model):
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=50, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "term"
        verbose_name_plural = "terms"
        ordering = ('start_date',)
