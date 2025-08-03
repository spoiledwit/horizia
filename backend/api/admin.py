from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, JiraIntegration

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(JiraIntegration)
class JiraIntegrationAdmin(ModelAdmin):
    list_display = ['user', 'site_name', 'site_url', 'is_active', 'is_token_expired', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'site_name', 'site_url']
    readonly_fields = ['_access_token', '_refresh_token', 'cloud_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Jira Instance', {
            'fields': ('site_name', 'site_url', 'cloud_id')
        }),
        ('Status', {
            'fields': ('is_active', 'last_sync_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
