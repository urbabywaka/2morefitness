"""
Attendance models for 2moreFitness
"""
from django.db import models
from apps.members.models import Member


class Attendance(models.Model):
    """Member attendance tracking"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance'
        ordering = ['-date', '-check_in']
        unique_together = ['member', 'date', 'check_in']
    
    def __str__(self):
        return f"{self.member} - {self.date} at {self.check_in}"
    
    @property
    def duration(self):
        """Calculate duration of gym session"""
        if self.check_out:
            from datetime import datetime, timedelta
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            duration = check_out_dt - check_in_dt
            return duration
        return None
    
    @property
    def duration_minutes(self):
        """Get duration in minutes"""
        duration = self.duration
        if duration:
            return int(duration.total_seconds() / 60)
        return None
