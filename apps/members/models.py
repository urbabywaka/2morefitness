"""
Member models for 2moreFitness
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import MembershipPlan


class Member(models.Model):
    """Member profile with gym-specific information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or allergies")
    fitness_goals = models.TextField(blank=True)
    enrolled_classes = models.ManyToManyField('classes.GymClass', blank=True, related_name='enrolled_members')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'members'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    @property
    def has_active_membership(self):
        """Check if member has an active membership"""
        from datetime import datetime
        return self.memberships.filter(
            status='active',
            end_date__gte=datetime.now()
        ).exists()
    
    @property
    def current_membership(self):
        """Get the current active membership"""
        from datetime import datetime
        return self.memberships.filter(
            status='active',
            end_date__gte=datetime.now()
        ).first()


class Membership(models.Model):
    """Member's membership subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'memberships'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.member} - {self.plan.name} ({self.status})"
    
    @property
    def is_active(self):
        """Check if membership is currently active"""
        from datetime import datetime
        return (
            self.status == 'active' and
            self.start_date <= datetime.now().date() <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Calculate days remaining in membership"""
        from datetime import datetime
        if self.is_active:
            delta = self.end_date - datetime.now().date()
            return delta.days
        return 0