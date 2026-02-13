from django.contrib import admin
from .models import GymClass  # or Class depending on your model name

@admin.register(GymClass)  # or @admin.register(Class)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'day_of_week', 'time', 'is_active']
    list_filter = ['difficulty', 'is_active', 'day_of_week']
    search_fields = ['name', 'description']