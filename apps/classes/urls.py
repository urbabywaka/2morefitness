"""
URL patterns for classes app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public class list (landing page)
    path('', views.class_list, name='class_list'),
    
    # Member class list (browse classes with filters)
    path('member/', views.member_class_list, name='member_class_list'),
    
    # Class detail
    path('<int:class_id>/', views.class_detail, name='class_detail'),
    
    # Class schedule
    path('schedule/', views.class_schedule, name='class_schedule'),
]