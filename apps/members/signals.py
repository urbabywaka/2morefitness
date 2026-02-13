"""
Signals for members app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.core.models import UserProfile
from .models import Member


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """Create UserProfile and Member when User is created"""
    if created:
        try:
            # Create UserProfile if it doesn't exist
            profile, profile_created = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'role': 'member'}
            )
            
            # Create Member if it doesn't exist
            Member.objects.get_or_create(user=instance)
            
        except Exception as e:
            print(f"Error creating profiles: {e}")