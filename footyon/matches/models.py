from django.db import models
from participation.models import Participation
import calendar

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