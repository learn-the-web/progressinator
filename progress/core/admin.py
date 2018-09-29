from django.contrib import admin

from .models import UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
   autocomplete_fields = ['user']
