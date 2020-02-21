'''
admin.py
'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'company_name',
                'password')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions')
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'company_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'id')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
