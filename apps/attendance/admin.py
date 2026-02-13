"""
Admin configuration for attendance app
"""
from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'date', 'check_in', 'check_out', 'duration_minutes', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['member__user__username', 'member__user__first_name', 'member__user__last_name']
    readonly_fields = ['created_at', 'duration_minutes']
    date_hierarchy = 'date'
