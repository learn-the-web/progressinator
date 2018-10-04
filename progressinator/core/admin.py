from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources

from .models import UserProgress, UserProfile, Course


class UserProfileStackedInline(admin.StackedInline):
    model = UserProfile
    exclude = ('api_key', )

class UserProfileTabularInline(admin.TabularInline):
    model = UserProfile
    exclude = ('api_key', )

class UserProgressInline(admin.TabularInline):
    model = UserProgress

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileStackedInline, UserProgressInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class UserProgressResource(resources.ModelResource):
    class Meta:
        model = UserProgress
        skip_unchanged = True
        report_skipped = True
        exclude = ('created', )
        fields = ('id', 'user', 'user__username', 'user__first_name', 'user__last_name', 'assessment_uri', 'grade', 'details')
        export_order = ('id', 'user', 'user__username', 'user__first_name', 'user__last_name', 'assessment_uri', 'grade', 'details')

@admin.register(UserProgress)
class UserProgressAdmin(ImportExportActionModelAdmin):
    resource_class = UserProgressResource
    autocomplete_fields = ['user']

class UserProfileResource(resources.ModelResource):
    class Meta:
        model = UserProfile
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'user', 'user__username', 'user__first_name', 'user__last_name', 'current_course', 'current_course__slug', 'current_section')
        export_order = ('id', 'user', 'user__username', 'user__first_name', 'user__last_name', 'current_course',  'current_course__slug','current_section')

@admin.register(UserProfile)
class UserProfileAdmin(ImportExportActionModelAdmin):
    resource_class = UserProfileResource
    autocomplete_fields = ['user']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = (UserProfileTabularInline, )
