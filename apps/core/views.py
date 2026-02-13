"""
Core views for 2moreFitness Gym Management System
Complete CRUD functionality - ALL IN ONE PAGE with modals
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import datetime, timedelta, date
from django.db import models
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import UserProfile, MembershipPlan, ContactMessage
from apps.members.models import Member, Membership
from apps.trainers.models import Trainer

# ============= SAFE IMPORTS FOR CLASSES =============
try:
    from apps.classes.models import GymClass as Class
    from apps.classes.models import ClassBooking
    print("SUCCESS: Imported GymClass as Class")
except ImportError:
    try:
        from apps.classes.models import Class
        from apps.classes.models import ClassBooking
        print("SUCCESS: Imported Class")
    except ImportError:
        try:
            from apps.classes.models import classes as Class
            from apps.classes.models import ClassBooking
            print("SUCCESS: Imported classes as Class")
        except ImportError:
            Class = None
            ClassBooking = None
            print("WARNING: Could not import Class model from apps.classes.models")

from apps.attendance.models import Attendance
# ====================================================

# ============================================
# INDEX VIEW
# ============================================
def index(request):
    """Home page view"""
    membership_plans = MembershipPlan.objects.filter(is_active=True)[:3]
    featured_trainers = Trainer.objects.filter(is_active=True)[:4]
    
    upcoming_classes = []
    if Class is not None:
        upcoming_classes = Class.objects.filter(
            is_active=True,
        )[:6]
    
    total_members = Member.objects.count()
    total_trainers = Trainer.objects.count()
    total_classes = 0
    if Class is not None:
        total_classes = Class.objects.filter(is_active=True).count()
    
    context = {
        'membership_plans': membership_plans,
        'featured_trainers': featured_trainers,
        'upcoming_classes': upcoming_classes,
        'total_members': total_members,
        'total_trainers': total_trainers,
        'total_classes': total_classes,
    }
    return render(request, 'core/index.html', context)


# ============================================
# ABOUT VIEW
# ============================================
def about(request):
    return render(request, 'core/about.html')


# ============================================
# SERVICES VIEW
# ============================================
def services(request):
    return render(request, 'core/services.html')


# ============================================
# FRANCHISE VIEW
# ============================================
def franchise(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you for your franchise inquiry! Our team will contact you within 24 hours.')
        return redirect('index')
    return render(request, 'core/franchise.html')


# ============================================
# CORPORATE VIEW
# ============================================
def corporate(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you for your corporate inquiry! We will send you our wellness program proposal.')
        return redirect('index')
    return render(request, 'core/corporate.html')


# ============================================
# MEMBERSHIP PLANS VIEW
# ============================================
def membership_plans(request):
    plans = MembershipPlan.objects.filter(is_active=True).order_by('price')
    user_member = None
    if request.user.is_authenticated:
        try:
            user_member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            pass
    
    context = {
        'plans': plans,
        'user_member': user_member,
        'total_plans': plans.count()
    }
    return render(request, 'core/membership_plans.html', context)


# ============================================
# CONTACT VIEW
# ============================================
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'Your message has been sent! We will contact you soon.')
        return redirect('index')
    return render(request, 'core/contact.html')


# ============================================
# REGISTER VIEW
# ============================================
def register_view(request):
    """Member registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create or update UserProfile
        from apps.core.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            profile.phone = phone
            profile.address = address
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                user=user,
                phone=phone,
                address=address,
            )
        
        # Create Member
        from apps.members.models import Member
        if not Member.objects.filter(user=user).exists():
            Member.objects.create(
                user=user,
                is_active=False,
            )
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'core/register.html')


# ============================================
# UNIFIED LOGIN VIEW
# ============================================
def login_view(request):
    """Unified login - MEMBER muna, ADMIN pangalawa"""
    
    if request.user.is_authenticated:
        auth_logout(request)
    request.session.flush()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        # ===== STEP 1: CHECK IF REGULAR MEMBER =====
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            try:
                member = Member.objects.get(user=user)
                
                # Member login
                auth_login(request, user)
                request.session['is_member'] = True
                request.session['is_admin'] = False
                request.session['member_id'] = member.id
                request.session['user_type'] = 'member'
                
                if not remember:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('member_dashboard')
                
            except Member.DoesNotExist:
                # Not a member, continue to admin check
                pass
        
        # ===== STEP 2: CHECK IF ADMIN =====
        admin_username = getattr(settings, 'STATIC_ADMIN_USERNAME', 'gymadmin')
        admin_password = getattr(settings, 'STATIC_ADMIN_PASSWORD', 'admin123')
        admin_name = getattr(settings, 'STATIC_ADMIN_NAME', 'System Administrator')
        
        if username == admin_username and password == admin_password:
            request.session['is_admin'] = True
            request.session['is_member'] = False
            request.session['admin_username'] = username
            request.session['admin_name'] = admin_name
            request.session['user_type'] = 'admin'
            
            if not remember:
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {admin_name}!')
            return redirect('admin_dashboard')
        
        # ===== STEP 3: INVALID =====
        messages.error(request, 'Invalid username or password.')
    
    next_url = request.GET.get('next', '')
    context = {'next': next_url}
    return render(request, 'core/login.html', context)


# ============================================
# LOGOUT VIEW
# ============================================
def logout_view(request):
    request.session.flush()
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


# ============================================
# DASHBOARD REDIRECT
# ============================================
def dashboard_redirect(request):
    if request.session.get('is_member', False):
        return redirect('member_dashboard')
    if request.session.get('is_admin', False):
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        try:
            member = Member.objects.get(user=request.user)
            request.session['is_member'] = True
            request.session['member_id'] = member.id
            return redirect('member_dashboard')
        except Member.DoesNotExist:
            pass
    messages.error(request, 'Please login to access your dashboard.')
    return redirect('login')


# ============================================
# ADMIN DASHBOARD
# ============================================
def admin_dashboard(request):
    """Admin dashboard view - with all context variables"""
    
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    today = date.today()
    first_day = today.replace(day=1)
    
    # MEMBER STATISTICS
    total_members = Member.objects.count()
    active_memberships = Membership.objects.filter(status='active').count()
    total_trainers = Trainer.objects.count()
    today_attendance = Attendance.objects.filter(date=today).count()
    
    # NEW MEMBERS THIS MONTH
    new_members_this_month = Member.objects.filter(created_at__date__gte=first_day).count()
    
    # EXPIRING SOON
    expiring_soon = Membership.objects.filter(
        status='active',
        end_date__lte=today + timedelta(days=7),
        end_date__gte=today
    ).count()
    
    # CLASSES TODAY
    classes_today = 0
    if Class is not None:
        import datetime
        today_day = today.strftime('%A').lower()
        classes_today = Class.objects.filter(
            is_active=True,
            day_of_week=today_day
        ).count()
    
    # RECENT MEMBERS
    recent_members = Member.objects.order_by('-created_at')[:5]
    
    # PEAK HOUR
    peak_hour = "5-7 PM"
    
    # RECENT ACTIVITIES
    recent_activities = []
    
    for member in Member.objects.order_by('-created_at')[:3]:
        time_ago = timesince(member.created_at).split(',')[0]
        recent_activities.append({
            'icon': 'user-plus',
            'title': 'New member registered',
            'description': f'{member.user.get_full_name() or member.user.username} joined',
            'time': f'{time_ago} ago'
        })
    
    for attendance in Attendance.objects.order_by('-date', '-check_in')[:3]:
        if attendance.member:
            time_ago = timesince(attendance.date).split(',')[0]
            recent_activities.append({
                'icon': 'clipboard-check',
                'title': 'Member check-in',
                'description': f'{attendance.member.user.get_full_name() or attendance.member.user.username} checked in',
                'time': f'{time_ago} ago'
            })
    
    for membership in Membership.objects.filter(status='active').order_by('-start_date')[:3]:
        time_ago = timesince(membership.start_date).split(',')[0]
        recent_activities.append({
            'icon': 'crown',
            'title': 'Membership purchased',
            'description': f'{membership.member.user.get_full_name() or membership.member.user.username} bought {membership.plan.name}',
            'time': f'{time_ago} ago'
        })
    
    context = {
        'total_members': total_members,
        'active_memberships': active_memberships,
        'total_trainers': total_trainers,
        'today_attendance': today_attendance,
        'recent_members': recent_members,
        'new_members_this_month': new_members_this_month,
        'expiring_soon': expiring_soon,
        'classes_today': classes_today,
        'peak_hour': peak_hour,
        'recent_activities': recent_activities,
        'user': request.user,
    }
    
    return render(request, 'core/admin_dashboard.html', context)


# ============================================
# MEMBER DASHBOARD
# ============================================
def member_dashboard(request):
    """Member dashboard view"""
    
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access your dashboard.')
        return redirect('login')
    
    try:
        member = Member.objects.get(user=request.user)
        
        # FIX SESSION
        request.session['is_member'] = True
        request.session['member_id'] = member.id
        
        # MEMBERSHIP DATA
        active_membership = Membership.objects.filter(
            member=member, 
            status='active'
        ).first()
        
        # Calculate days remaining and percentage
        membership_days_left = 0
        membership_percentage = 0
        
        if active_membership and active_membership.end_date:
            if active_membership.start_date and active_membership.end_date:
                total_days = (active_membership.end_date - active_membership.start_date).days
                days_remaining = (active_membership.end_date - timezone.now().date()).days
                membership_days_left = max(days_remaining, 0)
                if total_days > 0:
                    days_used = total_days - membership_days_left
                    membership_percentage = int((days_used / total_days) * 100)
        
        # CLASS DATA
        upcoming_classes = []
        if Class is not None:
            upcoming_classes = member.enrolled_classes.filter(
                is_active=True,
            ).order_by('day_of_week', 'time')[:4]
        
        # ATTENDANCE DATA
        recent_attendance = Attendance.objects.filter(
            member=member
        ).order_by('-date', '-check_in')[:5]
        
        checkins_count = Attendance.objects.filter(member=member).count()
        
        context = {
            'user': request.user,
            'member': member,
            'active_membership': active_membership,
            'membership_days_left': membership_days_left,
            'membership_percentage': membership_percentage,
            'upcoming_classes': upcoming_classes,
            'recent_attendance': recent_attendance,
            'checkins_count': checkins_count,
        }
        return render(request, 'core/member_dashboard.html', context)
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')


# ============================================
# MEMBER PROFILE VIEW
# ============================================
def member_profile(request):
    """Member profile view"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your profile.')
        return redirect('login')
    
    try:
        # Get user profile
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Get member
        member = Member.objects.get(user=request.user)
        
        # Get active membership
        active_membership = Membership.objects.filter(
            member=member, 
            status='active'
        ).first()
        
        # Calculate days remaining and percentage
        membership_days_left = 0
        membership_percentage = 0
        if active_membership and active_membership.end_date:
            if active_membership.start_date and active_membership.end_date:
                total_days = (active_membership.end_date - active_membership.start_date).days
                days_remaining = (active_membership.end_date - timezone.now().date()).days
                membership_days_left = max(days_remaining, 0)
                if total_days > 0:
                    days_used = total_days - membership_days_left
                    membership_percentage = int((days_used / total_days) * 100)
        
        # Get enrolled classes
        enrolled_classes = []
        if Class is not None:
            enrolled_classes = member.enrolled_classes.filter(
                is_active=True,
            ).order_by('day_of_week', 'time')[:5]
        
        # Get checkins count
        checkins_count = Attendance.objects.filter(member=member).count()
        
        context = {
            'profile': user_profile,
            'member': member,
            'active_membership': active_membership,
            'enrolled_classes': enrolled_classes,
            'checkins_count': checkins_count,
            'membership_days_left': membership_days_left,
            'membership_percentage': membership_percentage,
            'user': request.user,
        }
        return render(request, 'core/profile.html', context)
        
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('index')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('index')


# ============================================
# UPDATE PROFILE VIEW
# ============================================
def update_profile(request):
    """Update member profile"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to update your profile.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            member = Member.objects.get(user=user)
            
            # Update user fields
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Update profile fields
            profile.phone = request.POST.get('phone', profile.phone)
            profile.address = request.POST.get('address', profile.address)
            profile.date_of_birth = request.POST.get('date_of_birth', profile.date_of_birth)
            profile.save()
            
            # Member fields (only is_active lives on Member itself)
            member.save()
            
            messages.success(request, 'Profile updated successfully!')
            
        except UserProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
        except Member.DoesNotExist:
            messages.error(request, 'Member profile not found.')
            
    return redirect('member_profile')


# ============================================
# CHANGE PASSWORD VIEW
# ============================================
def change_password(request):
    """Change user password"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to change your password.')
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('member_profile')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('member_profile')
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('member_profile')
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Re-authenticate user
        user = authenticate(
            username=request.user.username,
            password=new_password
        )
        if user:
            auth_login(request, user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('member_profile')
    
    return redirect('member_profile')


# ============================================
# TRAINER DASHBOARD
# ============================================
def trainer_dashboard(request):
    """Trainer dashboard view"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access your dashboard.')
        return redirect('login')
    
    try:
        trainer = Trainer.objects.get(user=request.user)
        
        assigned_classes = []
        if Class is not None:
            assigned_classes = Class.objects.filter(
                trainer=trainer, 
                is_active=True
            ).order_by('day_of_week', 'time')
        
        today = timezone.now().date()
        today_day = today.strftime('%A').lower()
        today_classes = []
        if Class is not None:
            today_classes = assigned_classes.filter(day_of_week=today_day)
        
        upcoming_classes = []
        if Class is not None:
            upcoming_classes = assigned_classes.order_by('day_of_week', 'time')[:10]
        
        total_members_trained = 0
        if Class is not None:
            total_members_trained = Member.objects.filter(
                enrolled_classes__in=assigned_classes
            ).distinct().count()
        
        today_attendance = Attendance.objects.filter(
            member__in=Member.objects.filter(enrolled_classes__in=assigned_classes),
            date=today
        ).count()
        
        context = {
            'trainer': trainer,
            'assigned_classes': assigned_classes,
            'today_classes': today_classes,
            'upcoming_classes': upcoming_classes,
            'total_classes': len(assigned_classes) if assigned_classes else 0,
            'total_members_trained': total_members_trained,
            'today_attendance': today_attendance,
            'total_hours': sum([c.duration for c in assigned_classes if hasattr(c, 'duration') and c.duration]) / 60 if assigned_classes else 0,
        }
        return render(request, 'core/trainer_dashboard.html', context)
        
    except Trainer.DoesNotExist:
        messages.error(request, 'Trainer profile not found.')
        return redirect('index')


# ============================================
# PROFILE VIEW (LEGACY)
# ============================================
def profile(request):
    """Legacy profile view - redirect to member_profile"""
    return redirect('member_profile')


# ============================================
# EDIT PROFILE VIEW (LEGACY)
# ============================================
def edit_profile(request):
    """Legacy edit profile view"""
    if request.method == 'POST':
        return redirect('update_profile')
    return redirect('member_profile')


# ============================================
# FORGOT PASSWORD VIEW
# ============================================
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            messages.success(request, 'Password reset instructions have been sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
            return redirect('forgot_password')
    return render(request, 'core/forgot_password.html')


# ============================================
# RESET PASSWORD VIEW
# ============================================
def reset_password(request, token):
    return render(request, 'core/reset_password.html')


# ============================================
# TERMS VIEW
# ============================================
def terms(request):
    return render(request, 'core/terms.html')


# ============================================
# PRIVACY VIEW
# ============================================
def privacy(request):
    return render(request, 'core/privacy.html')


# ============================================
# FAQ VIEW
# ============================================
def faq(request):
    return render(request, 'core/faq.html')


# ============================================
# CAREERS VIEW
# ============================================
def careers(request):
    return render(request, 'core/careers.html')


# ============================================
# ADMIN MEMBER LIST - ALL CRUD IN ONE PAGE (FIXED - SINGLE VERSION)
# ============================================
def admin_member_list(request):
    """Admin member list view - ALL CRUD operations in ONE page using modals"""
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    # ===== IMPORT ALL MODELS AT THE VERY BEGINNING =====
    from apps.members.models import Member, Membership
    from apps.core.models import UserProfile
    from django.db import models
    from datetime import date, timedelta
    from django.core.paginator import Paginator
    from django.contrib.auth.models import User
    
    # ===== AJAX: CREATE MEMBER =====
    if request.method == 'POST' and request.POST.get('action') == 'create_member':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not username or not email or not password:
            return JsonResponse({'error': 'Username, email and password are required.'}, status=400)
        
        if password != password_confirm:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
        
        if len(password) < 8:
            return JsonResponse({'error': 'Password must be at least 8 characters.'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered.'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
        )
        
        # Create Member
        member = Member.objects.create(
            user=user,
            is_active=is_active,
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Member {user.get_full_name() or user.username} has been created successfully.',
            'member_id': member.id
        })
    
    # ===== AJAX: UPDATE MEMBER =====
    if request.method == 'POST' and request.POST.get('action') == 'update_member':
        member_id = request.POST.get('member_id')
        
        try:
            member = Member.objects.get(id=member_id)
            user = member.user
            profile, created = UserProfile.objects.get_or_create(user=user)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)
        
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update profile fields
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.save()
        
        # Update member fields
        member.is_active = request.POST.get('is_active') == 'on'
        member.save()
        
        # Update password if provided
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        if new_password:
            if new_password != new_password_confirm:
                return JsonResponse({'error': 'New passwords do not match.'}, status=400)
            if len(new_password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters.'}, status=400)
            user.set_password(new_password)
            user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Member {user.get_full_name() or user.username} has been updated successfully.'
        })
    
    # ===== AJAX: DELETE MEMBER =====
    if request.method == 'POST' and request.POST.get('action') == 'delete_member':
        member_id = request.POST.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            user = member.user
            # Delete profile
            try:
                profile = UserProfile.objects.get(user=user)
                profile.delete()
            except UserProfile.DoesNotExist:
                pass
            member.delete()
            user.delete()
            return JsonResponse({
                'success': True,
                'message': 'Member has been deleted successfully.'
            })
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)
    
    # ===== AJAX: BULK DELETE MEMBERS =====
    if request.method == 'POST' and request.POST.get('action') == 'bulk_delete_members':
        member_ids = request.POST.getlist('member_ids[]')
        if member_ids:
            members = Member.objects.filter(id__in=member_ids)
            count = members.count()
            for member in members:
                user = member.user
                try:
                    profile = UserProfile.objects.get(user=user)
                    profile.delete()
                except UserProfile.DoesNotExist:
                    pass
                member.delete()
                user.delete()
            return JsonResponse({
                'success': True,
                'message': f'{count} member(s) have been deleted successfully.'
            })
        return JsonResponse({'error': 'No members selected.'}, status=400)
    
    # ===== AJAX: TOGGLE MEMBER STATUS =====
    if request.method == 'POST' and request.POST.get('action') == 'toggle_member_status':
        member_id = request.POST.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            member.is_active = not member.is_active
            member.save()
            status = 'activated' if member.is_active else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'Member has been {status} successfully.',
                'is_active': member.is_active
            })
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)
    
    # ===== AJAX: GET MEMBER DATA FOR EDIT =====
    if request.method == 'GET' and request.GET.get('action') == 'get_member_data':
        member_id = request.GET.get('member_id')
        try:
            member = Member.objects.get(id=member_id)
            user = member.user
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                profile = None
            
            data = {
                'id': member.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone if profile else '',
                'address': profile.address if profile else '',
                'is_active': member.is_active,
            }
            return JsonResponse(data)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)
    
    # ===== GET FILTERS =====
    status_filter = request.GET.get('status')
    membership_filter = request.GET.get('membership')
    join_date_filter = request.GET.get('join_date')
    sort = request.GET.get('sort', 'newest')
    search = request.GET.get('search')
    
    # Base queryset
    members = Member.objects.all().select_related('user')
    
    # Apply filters
    if status_filter == 'active':
        members = members.filter(is_active=True)
    elif status_filter == 'inactive':
        members = members.filter(is_active=False)
    
    if join_date_filter == 'today':
        members = members.filter(created_at__date=date.today())
    elif join_date_filter == 'week':
        week_ago = date.today() - timedelta(days=7)
        members = members.filter(created_at__date__gte=week_ago)
    elif join_date_filter == 'month':
        month_ago = date.today() - timedelta(days=30)
        members = members.filter(created_at__date__gte=month_ago)
    elif join_date_filter == 'year':
        year_ago = date.today() - timedelta(days=365)
        members = members.filter(created_at__date__gte=year_ago)
    
    if search:
        members = members.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(user__email__icontains=search)
        )
    
    # Apply sorting
    if sort == 'newest':
        members = members.order_by('-created_at')
    elif sort == 'oldest':
        members = members.order_by('created_at')
    elif sort == 'name_asc':
        members = members.order_by('user__first_name', 'user__last_name')
    elif sort == 'name_desc':
        members = members.order_by('-user__first_name', '-user__last_name')
    
    total_members = members.count()
    active_members = members.filter(is_active=True).count()
    inactive_members = total_members - active_members
    
    # Get UserProfile data for display
    member_ids = [m.id for m in members]
    profiles = UserProfile.objects.filter(user__member__id__in=member_ids).select_related('user')
    profile_dict = {p.user.id: p for p in profiles}
    
    # Pagination
    paginator = Paginator(members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'members': page_obj,
        'profile_dict': profile_dict,
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'active_memberships': Membership.objects.filter(status='active').count(),
        'new_members_this_month': Member.objects.filter(created_at__date__gte=date.today().replace(day=1)).count(),
        'user': request.user,
        'current_filters': {
            'status': status_filter,
            'membership': membership_filter,
            'join_date': join_date_filter,
            'sort': sort,
            'search': search,
        }
    }
    
    return render(request, 'core/admin/admin_member_list.html', context)


# ============================================
# ADMIN MEMBER DETAIL - VIEW ONLY
# ============================================
def admin_member_detail(request, member_id):
    """Admin member detail view - READ only"""
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    try:
        member = Member.objects.get(id=member_id)
        user = member.user
        
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        memberships = Membership.objects.filter(member=member).order_by('-start_date')
        attendance = Attendance.objects.filter(member=member).order_by('-date')[:10]
        
        enrolled_classes = []
        if Class is not None:
            enrolled_classes = member.enrolled_classes.filter(is_active=True)
        
        # Get active membership
        active_membership = memberships.filter(status='active').first()
        
        # Calculate days remaining
        membership_days_left = 0
        if active_membership and active_membership.end_date:
            days_remaining = (active_membership.end_date - date.today()).days
            membership_days_left = max(days_remaining, 0)
        
        context = {
            'member': member,
            'user': user,
            'profile': profile,
            'memberships': memberships,
            'attendance': attendance,
            'enrolled_classes': enrolled_classes,
            'active_membership': active_membership,
            'membership_days_left': membership_days_left,
            'total_classes': enrolled_classes.count() if enrolled_classes else 0,
            'total_attendance': attendance.count(),
            'total_members': Member.objects.count(),
            'request_user': request.user,
        }
        
        return render(request, 'core/admin/admin_member_detail.html', context)
    except Member.DoesNotExist:
        messages.error(request, 'Member not found.')
        return redirect('admin_member_list')


# ============================================
# ADMIN CLASS LIST - ALL CRUD IN ONE PAGE
# ============================================
def admin_class_list(request):
    """Admin class list view - ALL CRUD operations in ONE page using modals"""
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    if Class is None:
        context = {
            'classes': [],
            'total_classes': 0,
            'active_classes': 0,
            'total_enrolled': 0,
            'avg_capacity': 0,
            'trainers': Trainer.objects.filter(is_active=True).select_related('user'),
            'user': request.user,
            'current_filters': {},
        }
        return render(request, 'core/admin/admin_class_list.html', context)
    
    # ===== AJAX: CREATE CLASS =====
    if request.method == 'POST' and request.POST.get('action') == 'create_class':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        trainer_id = request.POST.get('trainer')
        day_of_week = request.POST.get('day_of_week')
        time = request.POST.get('time')
        duration = request.POST.get('duration', 60)
        difficulty = request.POST.get('difficulty', 'beginner')
        max_capacity = request.POST.get('max_capacity', 20)
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not name or not trainer_id or not day_of_week or not time:
            return JsonResponse({'error': 'Please fill in all required fields.'}, status=400)
        
        try:
            trainer = Trainer.objects.get(id=trainer_id)
        except Trainer.DoesNotExist:
            return JsonResponse({'error': 'Selected trainer does not exist.'}, status=400)
        
        # Create class
        class_obj = Class.objects.create(
            name=name,
            description=description,
            trainer=trainer,
            day_of_week=day_of_week,
            time=time,
            duration=int(duration),
            difficulty=difficulty,
            max_capacity=int(max_capacity),
            is_active=is_active
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Class "{class_obj.name}" has been created successfully.',
            'class_id': class_obj.id
        })
    
    # ===== AJAX: UPDATE CLASS =====
    if request.method == 'POST' and request.POST.get('action') == 'update_class':
        class_id = request.POST.get('class_id')
        
        try:
            class_obj = Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found.'}, status=404)
        
        class_obj.name = request.POST.get('name', class_obj.name)
        class_obj.description = request.POST.get('description', class_obj.description)
        
        trainer_id = request.POST.get('trainer')
        if trainer_id:
            try:
                class_obj.trainer = Trainer.objects.get(id=trainer_id)
            except Trainer.DoesNotExist:
                pass
        
        day_of_week = request.POST.get('day_of_week')
        if day_of_week:
            class_obj.day_of_week = day_of_week
        
        time = request.POST.get('time')
        if time:
            class_obj.time = time
        
        duration = request.POST.get('duration')
        if duration:
            class_obj.duration = int(duration)
        
        difficulty = request.POST.get('difficulty')
        if difficulty:
            class_obj.difficulty = difficulty
        
        max_capacity = request.POST.get('max_capacity')
        if max_capacity:
            class_obj.max_capacity = int(max_capacity)
        
        class_obj.is_active = request.POST.get('is_active') == 'on'
        class_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Class "{class_obj.name}" has been updated successfully.'
        })
    
    # ===== AJAX: DELETE CLASS =====
    if request.method == 'POST' and request.POST.get('action') == 'delete_class':
        class_id = request.POST.get('class_id')
        try:
            class_obj = Class.objects.get(id=class_id)
            class_name = class_obj.name
            class_obj.delete()
            return JsonResponse({
                'success': True,
                'message': f'Class "{class_name}" has been deleted successfully.'
            })
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found.'}, status=404)
    
    # ===== AJAX: BULK DELETE CLASSES =====
    if request.method == 'POST' and request.POST.get('action') == 'bulk_delete_classes':
        class_ids = request.POST.getlist('class_ids[]')
        if class_ids:
            classes = Class.objects.filter(id__in=class_ids)
            count = classes.count()
            classes.delete()
            return JsonResponse({
                'success': True,
                'message': f'{count} class(es) have been deleted successfully.'
            })
        return JsonResponse({'error': 'No classes selected.'}, status=400)
    
    # ===== AJAX: TOGGLE CLASS STATUS =====
    if request.method == 'POST' and request.POST.get('action') == 'toggle_class_status':
        class_id = request.POST.get('class_id')
        try:
            class_obj = Class.objects.get(id=class_id)
            class_obj.is_active = not class_obj.is_active
            class_obj.save()
            status = 'activated' if class_obj.is_active else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'Class "{class_obj.name}" has been {status} successfully.',
                'is_active': class_obj.is_active
            })
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found.'}, status=404)
    
    # ===== AJAX: GET CLASS DATA FOR EDIT =====
    if request.method == 'GET' and request.GET.get('action') == 'get_class_data':
        class_id = request.GET.get('class_id')
        try:
            class_obj = Class.objects.get(id=class_id)
            
            # Format time correctly
            time_str = ''
            if class_obj.time:
                if hasattr(class_obj.time, 'strftime'):
                    time_str = class_obj.time.strftime('%H:%M')
                else:
                    time_str = str(class_obj.time)
            
            data = {
                'id': class_obj.id,
                'name': class_obj.name,
                'description': class_obj.description or '',
                'trainer_id': class_obj.trainer.id if class_obj.trainer else '',
                'trainer_name': class_obj.trainer.user.get_full_name() if class_obj.trainer else '',
                'day_of_week': class_obj.day_of_week,
                'time': time_str,
                'duration': class_obj.duration,
                'difficulty': class_obj.difficulty,
                'max_capacity': class_obj.max_capacity,
                'is_active': class_obj.is_active,
            }
            return JsonResponse(data)
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found'}, status=404)
    
    # ===== GET FILTER PARAMETERS =====
    difficulty = request.GET.get('difficulty')
    trainer_id = request.GET.get('trainer')
    day = request.GET.get('day')
    duration = request.GET.get('duration')
    search = request.GET.get('search')
    
    # Base queryset
    classes = Class.objects.all().select_related('trainer', 'trainer__user')
    
    # Apply filters
    if difficulty:
        classes = classes.filter(difficulty=difficulty)
    
    if trainer_id:
        classes = classes.filter(trainer_id=trainer_id)
    
    if day:
        classes = classes.filter(day_of_week=day)
    
    if duration:
        classes = classes.filter(duration=duration)
    
    if search:
        classes = classes.filter(
            models.Q(name__icontains=search) |
            models.Q(description__icontains=search) |
            models.Q(trainer__user__first_name__icontains=search) |
            models.Q(trainer__user__last_name__icontains=search)
        )
    
    # Order by day and time
    classes = classes.order_by('day_of_week', 'time')
    
    total_classes = classes.count()
    active_classes = classes.filter(is_active=True).count()
    
    # Calculate total enrolled and avg capacity
    total_enrolled = 0
    total_capacity = 0
    for class_obj in classes:
        enrolled_count = class_obj.enrolled_members.count()
        total_enrolled += enrolled_count
        total_capacity += class_obj.max_capacity
    
    avg_capacity = 0
    if total_capacity > 0:
        avg_capacity = int((total_enrolled / total_capacity) * 100)
    
    # Get all trainers for filter dropdown
    trainers = Trainer.objects.filter(is_active=True).select_related('user')
    
    # Pagination
    paginator = Paginator(classes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'classes': page_obj,
        'total_classes': total_classes,
        'active_classes': active_classes,
        'total_enrolled': total_enrolled,
        'avg_capacity': avg_capacity,
        'trainers': trainers,
        'user': request.user,
        'total_members': Member.objects.count(),
        'current_filters': {
            'difficulty': difficulty,
            'trainer': trainer_id,
            'day': day,
            'duration': duration,
            'search': search,
        }
    }
    
    return render(request, 'core/admin/admin_class_list.html', context)


# ============================================
# ADMIN CLASS DETAIL - VIEW ONLY
# ============================================
def admin_class_detail(request, class_id):
    """Admin class detail view - READ only"""
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    if Class is None:
        messages.error(request, 'Class model is not available.')
        return redirect('admin_class_list')
    
    try:
        class_obj = Class.objects.get(id=class_id)
        enrolled_members = class_obj.enrolled_members.all().select_related('user')
        
        context = {
            'class': class_obj,
            'enrolled_members': enrolled_members,
            'total_enrolled': enrolled_members.count(),
            'user': request.user,
            'total_members': Member.objects.count(),
            'total_classes': Class.objects.count(),
        }
        return render(request, 'core/admin/admin_class_detail.html', context)
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('admin_class_list')


# ============================================
# ADMIN TRAINERS LIST - FOR AJAX
# ============================================
def admin_trainers_list(request):
    """Return trainers list as JSON for AJAX calls"""
    if not request.session.get('is_admin', False):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    trainers = Trainer.objects.filter(is_active=True).select_related('user')
    trainer_data = []
    
    for trainer in trainers:
        trainer_data.append({
            'id': trainer.id,
            'name': trainer.user.get_full_name() or trainer.user.username
        })
    
    return JsonResponse(trainer_data, safe=False)


# ============================================
# ADMIN ATTENDANCE REPORT - ALL CRUD IN ONE PAGE
# ============================================
def admin_attendance_report(request):
    """Admin attendance report view - ALL CRUD operations in ONE page using modals"""
    if not request.session.get('is_admin', False):
        messages.error(request, 'Please login as administrator to access this page.')
        return redirect('login')
    
    # ===== AJAX: CREATE ATTENDANCE =====
    if request.method == 'POST' and request.POST.get('action') == 'create_attendance':
        member_id = request.POST.get('member')
        date = request.POST.get('date')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out', None)
        notes = request.POST.get('notes', '')
        
        # Validation
        if not member_id or not date or not check_in:
            return JsonResponse({'error': 'Member, date and check-in time are required.'}, status=400)
        
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Selected member does not exist.'}, status=400)
        
        # Check if already checked in
        existing = Attendance.objects.filter(
            member=member,
            date=date,
            check_out__isnull=True
        ).first()
        
        if existing:
            return JsonResponse({
                'warning': f'{member.user.get_full_name() or member.user.username} is already checked in on this date.'
            }, status=400)
        
        # Create attendance
        attendance = Attendance.objects.create(
            member=member,
            date=date,
            check_in=check_in,
            check_out=check_out if check_out else None,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance record for {member.user.get_full_name() or member.user.username} has been created successfully.',
            'attendance_id': attendance.id
        })
    
    # ===== AJAX: UPDATE ATTENDANCE =====
    if request.method == 'POST' and request.POST.get('action') == 'update_attendance':
        attendance_id = request.POST.get('attendance_id')
        
        try:
            attendance = Attendance.objects.get(id=attendance_id)
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found.'}, status=404)
        
        attendance.date = request.POST.get('date', attendance.date)
        attendance.check_in = request.POST.get('check_in', attendance.check_in)
        
        check_out = request.POST.get('check_out')
        attendance.check_out = check_out if check_out else None
        
        attendance.notes = request.POST.get('notes', attendance.notes)
        attendance.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Attendance record has been updated successfully.'
        })
    
    # ===== AJAX: DELETE ATTENDANCE =====
    if request.method == 'POST' and request.POST.get('action') == 'delete_attendance':
        attendance_id = request.POST.get('attendance_id')
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            member_name = attendance.member.user.get_full_name() or attendance.member.user.username
            attendance.delete()
            return JsonResponse({
                'success': True,
                'message': f'Attendance record for {member_name} has been deleted successfully.'
            })
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found.'}, status=404)
    
    # ===== AJAX: BULK DELETE ATTENDANCE =====
    if request.method == 'POST' and request.POST.get('action') == 'bulk_delete_attendance':
        attendance_ids = request.POST.getlist('attendance_ids[]')
        if attendance_ids:
            attendances = Attendance.objects.filter(id__in=attendance_ids)
            count = attendances.count()
            attendances.delete()
            return JsonResponse({
                'success': True,
                'message': f'{count} attendance record(s) have been deleted successfully.'
            })
        return JsonResponse({'error': 'No attendance records selected.'}, status=400)
    
    # ===== AJAX: CHECK OUT =====
    if request.method == 'POST' and request.POST.get('action') == 'check_out':
        attendance_id = request.POST.get('attendance_id')
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            if not attendance.check_out:
                attendance.check_out = timezone.now().time()
                attendance.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Member checked out successfully.',
                    'check_out': attendance.check_out.strftime('%H:%M')
                })
            else:
                return JsonResponse({'warning': 'Member already checked out.'}, status=400)
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found.'}, status=404)
    
    # ===== AJAX: QUICK CHECK IN =====
    if request.method == 'POST' and request.POST.get('action') == 'quick_check_in':
        member_id = request.POST.get('member_id')
        
        try:
            member = Member.objects.get(id=member_id)
            
            # Check if already checked in today
            today = date.today()
            existing = Attendance.objects.filter(
                member=member,
                date=today,
                check_out__isnull=True
            ).first()
            
            if existing:
                return JsonResponse({
                    'warning': f'{member.user.get_full_name() or member.user.username} is already checked in.'
                }, status=400)
            else:
                attendance = Attendance.objects.create(
                    member=member,
                    date=today,
                    check_in=timezone.now().time(),
                    notes='Quick check-in via admin'
                )
                return JsonResponse({
                    'success': True,
                    'message': f'{member.user.get_full_name() or member.user.username} has been checked in successfully.',
                    'attendance_id': attendance.id
                })
                
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found.'}, status=404)
    
    # ===== AJAX: GET ATTENDANCE DATA FOR EDIT =====
    if request.method == 'GET' and request.GET.get('action') == 'get_attendance_data':
        attendance_id = request.GET.get('attendance_id')
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            
            data = {
                'id': attendance.id,
                'member_id': attendance.member.id,
                'member_name': attendance.member.user.get_full_name() or attendance.member.user.username,
                'date': attendance.date.isoformat(),
                'check_in': attendance.check_in.strftime('%H:%M') if attendance.check_in else '',
                'check_out': attendance.check_out.strftime('%H:%M') if attendance.check_out else '',
                'notes': attendance.notes or '',
            }
            return JsonResponse(data)
        except Attendance.DoesNotExist:
            return JsonResponse({'error': 'Attendance record not found'}, status=404)
    
    # ===== GET FILTER PARAMETERS =====
    today = date.today()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    member_search = request.GET.get('member')
    
    # Base queryset
    attendances = Attendance.objects.all().select_related('member', 'member__user')
    
    # Apply filters
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if member_search:
        attendances = attendances.filter(
            models.Q(member__user__first_name__icontains=member_search) |
            models.Q(member__user__last_name__icontains=member_search) |
            models.Q(member__user__username__icontains=member_search)
        )
    
    # Order by date and time
    attendances = attendances.order_by('-date', '-check_in')
    
    # Statistics
    today_attendance = Attendance.objects.filter(date=today).count()
    
    # Week attendance
    week_start = today - timedelta(days=today.weekday())
    week_attendance = Attendance.objects.filter(date__gte=week_start).count()
    
    # Month attendance
    month_start = today.replace(day=1)
    month_attendance = Attendance.objects.filter(date__gte=month_start).count()
    
    # Pagination
    paginator = Paginator(attendances, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate average daily attendance for this month
    days_passed = today.day
    avg_daily = int(month_attendance / days_passed) if days_passed > 0 else 0
    
    # Get members for dropdown
    members = Member.objects.filter(is_active=True).select_related('user').order_by('user__first_name')
    
    # Get classes for filter dropdown
    classes = []
    if Class is not None:
        classes = Class.objects.filter(is_active=True)
    
    context = {
        'attendances': page_obj,
        'today_attendance': today_attendance,
        'week_attendance': week_attendance,
        'month_attendance': month_attendance,
        'avg_daily': avg_daily,
        'today_date': today,
        'total_records': attendances.count(),
        'members': members,
        'classes': classes,
        'user': request.user,
        'total_members': Member.objects.count(),
        'peak_hour': '5-7 PM',
        'peak_count': 0,
        'current_filters': {
            'date_from': date_from,
            'date_to': date_to,
            'member': member_search,
        }
    }
    
    return render(request, 'core/admin/admin_attendance_report.html', context)