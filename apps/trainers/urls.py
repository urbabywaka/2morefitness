"""
URL patterns for trainers app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.trainer_list, name='trainer_list'),
    path('<int:trainer_id>/', views.trainer_detail, name='trainer_detail'),
    path('profile/', views.trainer_profile, name='trainer_profile'),
    path('classes/', views.trainer_classes, name='trainer_classes'),
]
