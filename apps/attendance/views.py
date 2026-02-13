"""
Attendance views for 2moreFitness
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Attendance
from apps.members.models import Member


@login_required
def check_in(request):
    """Member check-in"""
    try:
        member = Member.objects.get(user=request.user)
        
        # Check if already checked in today
        today = datetime.now().date()
        existing = Attendance.objects.filter(
            member=member,
            date=today,
            check_out__isnull=True
        ).first()
        
        if existing:
            messages.warning(request, 'You are already checked in!')
            return redirect('member_dashboard')
        
        # Create attendance record
        Attendance.objects.create(
            member=member,
            date=today,
            check_in=datetime.now().time()
        )
        
        messages.success(request, 'Check-in successful! Have a great workout!')
        return redirect('member_dashboard')
    
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('dashboard')


@login_required
def check_out(request):
    """Member check-out"""
    try:
        member = Member.objects.get(user=request.user)
        
        # Find today's active check-in
        today = datetime.now().date()
        attendance = Attendance.objects.filter(
            member=member,
            date=today,
            check_out__isnull=True
        ).first()
        
        if not attendance:
            messages.warning(request, 'No active check-in found for today.')
            return redirect('member_dashboard')
        
        # Update check-out time
        attendance.check_out = datetime.now().time()
        attendance.save()
        
        messages.success(request, f'Check-out successful! You worked out for {attendance.duration_minutes} minutes.')
        return redirect('member_dashboard')
    
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('dashboard')


@login_required
def attendance_history(request):
    """View attendance history"""
    try:
        member = Member.objects.get(user=request.user)
        
        # Get date range from query params
        days = int(request.GET.get('days', 30))
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        records = Attendance.objects.filter(
            member=member,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate statistics
        total_visits = records.count()
        total_minutes = sum([r.duration_minutes or 0 for r in records])
        avg_duration = total_minutes / total_visits if total_visits > 0 else 0
        
        context = {
            'member': member,
            'records': records,
            'total_visits': total_visits,
            'total_minutes': total_minutes,
            'avg_duration': round(avg_duration, 1),
            'days': days,
        }
        
        return render(request, 'attendance/attendance_history.html', context)
    
    except Member.DoesNotExist:
        messages.error(request, 'Member profile not found.')
        return redirect('dashboard')


@login_required
def attendance_report(request):
    """Admin attendance report"""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get date range
    days = int(request.GET.get('days', 7))
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get attendance data
    records = Attendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('member__user')
    
    # Calculate statistics
    total_visits = records.count()
    unique_members = records.values('member').distinct().count()
    
    # Daily breakdown
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        day_visits = records.filter(date=current_date).count()
        daily_stats.append({
            'date': current_date,
            'visits': day_visits
        })
        current_date += timedelta(days=1)
    
    # Top members
    top_members = (
        records.values('member__user__first_name', 'member__user__last_name')
        .annotate(visit_count=Count('id'))
        .order_by('-visit_count')[:10]
    )
    
    context = {
        'records': records[:50],
        'total_visits': total_visits,
        'unique_members': unique_members,
        'daily_stats': daily_stats,
        'top_members': top_members,
        'days': days,
    }
    
    return render(request, 'attendance/attendance_report.html', context)
