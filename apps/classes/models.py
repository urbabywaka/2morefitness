"""
Gym Class models for 2moreFitness
"""
from django.db import models
from apps.trainers.models import Trainer


class GymClass(models.Model):
    """Gym class/session"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, related_name='classes')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='beginner')
    duration = models.IntegerField(help_text="Duration in minutes")
    max_capacity = models.IntegerField(default=20)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)  # String, hindi integer!
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gym_classes'
        ordering = ['day_of_week', 'time']
        verbose_name = 'Gym Class'
        verbose_name_plural = 'Gym Classes'
    
    def __str__(self):
        return f"{self.name} - {self.get_day_of_week_display()} {self.time.strftime('%I:%M %p')}"
    
    @property
    def enrolled_count(self):
        """Get number of enrolled members"""
        return self.enrolled_members.count()
    
    @property
    def spots_available(self):
        """Get number of available spots"""
        return self.max_capacity - self.enrolled_count
    
    @property
    def is_full(self):
        """Check if class is full"""
        return self.enrolled_count >= self.max_capacity
    
    # REMOVED duplicate available_spots property - gamitin na lang ang spots_available