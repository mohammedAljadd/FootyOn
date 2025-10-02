from django.db import models
from participation.models import Participation
import calendar
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

class Match(models.Model):
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    day_of_week = models.CharField(max_length=10)
    location_name = models.CharField(max_length=100)
    location_google_maps_embed_url = models.TextField(blank=True, null=True)  # store embeddable URL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_players = models.PositiveIntegerField(default=12)

    def __str__(self):
        return f"{self.location_name} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Automatically set the day of the week from the date
        if self.date:
            self.day_of_week = calendar.day_name[self.date.weekday()]
        super().save(*args, **kwargs)

    @property  # without it : match.spots_left, Django is not executing the method. It either treats it as a string or nothing
    def spots_left(self):
        """Calculate remaining spots based on current participation"""
        current_count = Participation.objects.filter(
            match=self, status='joined', removed=False, is_no_show=False
        ).count()
        return max(0, self.max_players - current_count)
    
    @property
    def is_full(self):
        return self.spots_left <= 0
    

    @property
    def is_past(self):
        
        """Check if the match date and time is in the past"""
        if self.date < timezone.now().date():
            return True
        elif self.date == timezone.now().date() and self.time:
            match_datetime = datetime.combine(self.date, self.time)
            return match_datetime < timezone.now()
        return False
    
    @property
    def can_edit_attendance(self):
        if not self.time:
            return False  # No time set, cannot edit
        match_datetime = datetime.combine(self.date, self.time)
        match_datetime = timezone.make_aware(match_datetime)  # ensure timezone-aware
        return timezone.now() <= match_datetime + timedelta(hours=24)