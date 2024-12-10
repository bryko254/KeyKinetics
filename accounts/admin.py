from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_employee')
    list_filter = ('role', 'is_active_employee', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Information', {
            'fields': ('role', 'phone_number', 'department', 'is_active_employee', 'last_login_yard')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Information', {
            'fields': ('role', 'phone_number', 'department', 'is_active_employee', 'last_login_yard')
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')

admin.site.register(CustomUser, CustomUserAdmin)
