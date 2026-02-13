"""
Trainer models for 2moreFitness
"""
from django.db import models
from django.contrib.auth.models import User


class Trainer(models.Model):
    """Trainer profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer')
    specialization = models.CharField(max_length=200, help_text="e.g., Strength Training, Yoga, CrossFit")
    bio = models.TextField()
    certifications = models.TextField(help_text="List certifications, one per line")
    years_of_experience = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profile_image = models.ImageField(upload_to='trainers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trainers'
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"
    
    def get_certifications_list(self):
        """Return certifications as a list"""
        return [c.strip() for c in self.certifications.split('\n') if c.strip()]
