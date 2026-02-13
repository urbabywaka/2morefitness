"""
URL patterns for members app - MEMBER URLs ONLY
"""
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.member_profile, name='member_profile'),
    path('classes/', views.member_classes, name='member_classes'),
    path('memberships/', views.member_memberships, name='member_memberships'),
    path('membership-history/', views.member_memberships, name='membership_history'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('purchase-membership/<int:plan_id>/', views.purchase_membership, name='purchase_membership'),
    path('enroll-class/<int:class_id>/', views.enroll_class, name='enroll_class'),
    path('unenroll-class/<int:class_id>/', views.unenroll_class, name='unenroll_class'),
]