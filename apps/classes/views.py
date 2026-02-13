from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import GymClass
from apps.members.models import Member

# ============================================
# PUBLIC CLASS LIST (LANDING PAGE)
# ============================================
def class_list(request):
    """Public class list for landing page"""
    classes = GymClass.objects.filter(is_active=True)[:6]
    return render(request, 'classes/class_list.html', {'classes': classes})


# ============================================
# MEMBER CLASS LIST (BROWSE CLASSES) - FIXED
# ============================================
@login_required
def member_class_list(request):
    """Member class list with filters and enrollment"""
    classes = GymClass.objects.filter(is_active=True).order_by('day_of_week', 'time')
    
    # Apply filters
    category = request.GET.get('category')
    if category:
        classes = classes.filter(description__icontains=category)
    
    difficulty = request.GET.get('level')
    if difficulty:
        classes = classes.filter(difficulty=difficulty)
    
    day = request.GET.get('day')
    if day:
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }
        if day in day_map:
            classes = classes.filter(day_of_week=day_map[day])
    
    duration = request.GET.get('duration')
    if duration:
        classes = classes.filter(duration=duration)
    
    search = request.GET.get('search')
    if search:
        classes = classes.filter(name__icontains=search) | classes.filter(description__icontains=search)
    
    # Pagination
    paginator = Paginator(classes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's enrolled classes
    enrolled_class_ids = []
    active_membership = None
    
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            enrolled_class_ids = member.enrolled_classes.values_list('id', flat=True)
            # FIXED: membership_set -> memberships
            active_membership = member.memberships.filter(status='active').first()
        except Member.DoesNotExist:
            pass
    
    # Calculate spots available
    for class_obj in page_obj:
        enrolled_count = class_obj.enrolled_members.count()
        class_obj.spots_available = class_obj.max_capacity - enrolled_count
    
    context = {
        'classes': page_obj,
        'enrolled_class_ids': enrolled_class_ids,
        'active_membership': active_membership,
    }
    return render(request, 'classes/member_class_list.html', context)


# ============================================
# CLASS DETAIL
# ============================================
def class_detail(request, class_id):
    """Class detail view"""
    class_obj = get_object_or_404(GymClass, id=class_id, is_active=True)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            is_enrolled = member.enrolled_classes.filter(id=class_id).exists()
        except Member.DoesNotExist:
            pass
    
    context = {
        'class': class_obj,
        'is_enrolled': is_enrolled,
        'enrolled_count': class_obj.enrolled_members.count(),
        'spots_available': class_obj.max_capacity - class_obj.enrolled_members.count(),
    }
    return render(request, 'classes/class_detail.html', context)


# ============================================
# CLASS SCHEDULE
# ============================================
def class_schedule(request):
    """Class schedule view"""
    classes = GymClass.objects.filter(is_active=True).order_by('day_of_week', 'time')
    return render(request, 'classes/class_schedule.html', {'classes': classes})