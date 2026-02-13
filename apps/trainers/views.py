"""
Trainer views for 2moreFitness
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trainer
from apps.classes.models import GymClass


def trainer_list(request):
    """List all active trainers (public)"""
    trainers = Trainer.objects.filter(is_active=True)
    context = {'trainers': trainers}
    return render(request, 'trainers/trainer_list.html', context)


def trainer_detail(request, trainer_id):
    """View trainer details (public)"""
    trainer = get_object_or_404(Trainer, id=trainer_id, is_active=True)
    classes = GymClass.objects.filter(trainer=trainer, is_active=True)
    context = {
        'trainer': trainer,
        'classes': classes,
    }
    return render(request, 'trainers/trainer_detail.html', context)


@login_required
def trainer_profile(request):
    """View and edit own trainer profile"""
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        messages.error(request, 'Trainer profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        trainer.specialization = request.POST.get('specialization', '')
        trainer.bio = request.POST.get('bio', '')
        trainer.certifications = request.POST.get('certifications', '')
        trainer.years_of_experience = request.POST.get('years_of_experience', 0)
        trainer.hourly_rate = request.POST.get('hourly_rate') or None
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        
        # Update user profile
        profile = request.user.profile
        profile.phone = request.POST.get('phone', '')
        
        try:
            trainer.save()
            request.user.save()
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Failed to update profile: {str(e)}')
        
        return redirect('trainer_profile')
    
    context = {'trainer': trainer}
    return render(request, 'trainers/trainer_profile.html', context)


@login_required
def trainer_classes(request):
    """View classes taught by trainer"""
    try:
        trainer = Trainer.objects.get(user=request.user)
        classes = GymClass.objects.filter(trainer=trainer)
        context = {
            'trainer': trainer,
            'classes': classes,
        }
        return render(request, 'trainers/trainer_classes.html', context)
    except Trainer.DoesNotExist:
        messages.error(request, 'Trainer profile not found.')
        return redirect('dashboard')
