"""
URL patterns for attendance app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('history/', views.attendance_history, name='attendance_history'),
    path('report/', views.attendance_report, name='attendance_report'),
]
