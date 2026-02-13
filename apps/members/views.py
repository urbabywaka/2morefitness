"""
Views for members app - MEMBER VIEWS ONLY
Admin views are now in core/views.py
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# Import from core models
from apps.core.models import UserProfile, MembershipPlan, ContactMessage
# Import from members models
from .models import Member, Membership


@login_required
def member_profile(request):
    """Member profile view"""
    try:
        member = Member.objects.get(user=request.user)
        context = {
            'member': member,
            'profile': request.user.profile,
        }
        return render(request, 'members/profile.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')


@login_required
def member_classes(request):
    """Member's enrolled classes"""
    try:
        member = Member.objects.get(user=request.user)
        enrolled_classes = member.enrolled_classes.filter(is_active=True)
        
        context = {
            'member': member,
            'enrolled_classes': enrolled_classes,
        }
        return render(request, 'members/classes.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')


@login_required
def member_memberships(request):
    """Member's membership history"""
    try:
        member = Member.objects.get(user=request.user)
        memberships = Membership.objects.filter(member=member).order_by('-start_date')
        
        context = {
            'member': member,
            'memberships': memberships,
        }
        return render(request, 'members/memberships.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')


@login_required
def update_profile(request):
    """Update member profile"""
    if request.method == 'POST':
        try:
            member = Member.objects.get(user=request.user)
            profile = request.user.profile
            
            # Update profile fields
            profile.phone = request.POST.get('phone', profile.phone)
            profile.address = request.POST.get('address', profile.address)
            profile.date_of_birth = request.POST.get('date_of_birth', profile.date_of_birth)
            profile.emergency_contact = request.POST.get('emergency_contact', profile.emergency_contact)
            profile.emergency_phone = request.POST.get('emergency_phone', profile.emergency_phone)
            profile.save()
            
            # Update member fields
            member.gender = request.POST.get('gender', member.gender)
            member.height = request.POST.get('height', member.height)
            member.weight = request.POST.get('weight', member.weight)
            member.medical_conditions = request.POST.get('medical_conditions', member.medical_conditions)
            member.fitness_goals = request.POST.get('fitness_goals', member.fitness_goals)
            member.save()
            
            # Update user fields
            user = request.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('member_profile')
            
        except Member.DoesNotExist:
            messages.error(request, 'Member profile not found.')
            return redirect('index')
    
    return redirect('member_profile')


@login_required
def purchase_membership(request, plan_id):
    """Purchase a membership plan"""
    try:
        member = Member.objects.get(user=request.user)
        plan = MembershipPlan.objects.get(id=plan_id, is_active=True)
        
        if request.method == 'POST':
            # Calculate end date based on duration
            start_date = timezone.now().date()
            if plan.duration == 'monthly':
                end_date = start_date + timedelta(days=30)
            elif plan.duration == 'quarterly':
                end_date = start_date + timedelta(days=90)
            elif plan.duration == 'semi_annual':
                end_date = start_date + timedelta(days=180)
            else:  # annual
                end_date = start_date + timedelta(days=365)
            
            # Create membership
            membership = Membership.objects.create(
                member=member,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                status='pending',
                payment_status='pending',
                payment_amount=plan.price,
                payment_date=None,
                payment_reference=request.POST.get('reference', ''),
                notes=request.POST.get('notes', '')
            )
            
            messages.success(request, f'Membership request for {plan.name} submitted! Please proceed to payment.')
            return redirect('member_memberships')
        
        context = {
            'member': member,
            'plan': plan,
        }
        return render(request, 'members/purchase_membership.html', context)
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')
    except MembershipPlan.DoesNotExist:
        messages.error(request, 'Membership plan not found.')
        return redirect('membership_plans')


@login_required
def enroll_class(request, class_id):
    """Enroll in a gym class"""
    from apps.classes.models import GymClass  # Pwede rin Class or Classes - check mo actual name
    
    try:
        member = Member.objects.get(user=request.user)
        gym_class = GymClass.objects.get(id=class_id, is_active=True)
        
        # Check if already enrolled
        if member.enrolled_classes.filter(id=class_id).exists():
            messages.info(request, 'You are already enrolled in this class.')
        else:
            member.enrolled_classes.add(gym_class)
            messages.success(request, f'Successfully enrolled in {gym_class.name}!')
        
        return redirect('member_classes')
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')
    except GymClass.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('class_list')


@login_required
def unenroll_class(request, class_id):
    """Unenroll from a gym class"""
    from apps.classes.models import GymClass  # Pwede rin Class or Classes - check mo actual name
    
    try:
        member = Member.objects.get(user=request.user)
        gym_class = GymClass.objects.get(id=class_id)
        
        if member.enrolled_classes.filter(id=class_id).exists():
            member.enrolled_classes.remove(gym_class)
            messages.success(request, f'Unenrolled from {gym_class.name}.')
        else:
            messages.info(request, 'You are not enrolled in this class.')
        
        return redirect('member_classes')
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')
    except GymClass.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('member_classes')