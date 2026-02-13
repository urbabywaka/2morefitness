"""
URL patterns for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Pages
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('franchise/', views.franchise, name='franchise'),
    path('corporate/', views.corporate, name='corporate'),
    path('membership-plans/', views.membership_plans, name='membership_plans'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('careers/', views.careers, name='careers'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Dashboard redirect
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('member-dashboard/', views.member_dashboard, name='member_dashboard'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    
    # Profile
    path('profile/', views.member_profile, name='member_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # ===== ADMIN MEMBER CRUD - SINGLE PAGE =====
    path('admin-members/', views.admin_member_list, name='admin_member_list'),
    path('admin-members/<int:member_id>/', views.admin_member_detail, name='admin_member_detail'),
    
    # ===== ADMIN CLASS CRUD - SINGLE PAGE =====
    path('admin-classes/', views.admin_class_list, name='admin_class_list'),
    path('admin-classes/<int:class_id>/', views.admin_class_detail, name='admin_class_detail'),
    path('admin-classes/trainers-list/', views.admin_trainers_list, name='admin_trainers_list'),
    
    # ===== ADMIN ATTENDANCE CRUD - SINGLE PAGE =====
    path('admin-attendance/', views.admin_attendance_report, name='admin_attendance_report'),
]