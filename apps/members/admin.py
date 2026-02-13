"""
Admin configuration for members app
"""
from django.contrib import admin
from .models import Member, Membership


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'is_active', 'has_active_membership', 'created_at']
    list_filter = ['gender', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['enrolled_classes']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'start_date', 'end_date', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['member__user__username', 'member__user__email', 'plan__name', 'payment_reference']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
