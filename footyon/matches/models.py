from django.db import models
from participation.models import Participation
import calendar
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.utils.translation import gettext_lazy as _

class Stadium(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Stadium Name"))
    google_maps_short_url = models.URLField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name

  
class Match(models.Model):
    date = models.DateField(verbose_name=_("Date"))
    time = models.TimeField(null=True, blank=True, verbose_name=_("Time"))
    day_of_week = models.CharField(max_length=10, verbose_name=_("Day of Week"))
    
    stadium = models.ForeignKey(
        Stadium,
        on_delete=models.PROTECT,
        related_name='matches',
        verbose_name=_("Stadium")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    max_players = models.PositiveIntegerField(default=12, verbose_name=_("Max Players"))
    
    def __str__(self):
        return f"{self.location_name} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Automatically set the day of the week from the date
        if self.date:
            self.day_of_week = calendar.day_name[self.date.weekday()]
        super().save(*args, **kwargs)

    @property
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
        """Check if the match date and time is in the past."""
        now = timezone.now()
        if self.date < now.date():
            return True
        elif self.date == now.date() and self.time:
            match_datetime = datetime.combine(self.date, self.time)
            match_datetime = timezone.make_aware(match_datetime, timezone.get_current_timezone())
            return match_datetime < now
        return False

    @property
    def can_edit_attendance(self):
        """Check if attendance can still be edited (within 24 hours after match time)"""
        if not self.time:
            return False
        match_datetime = datetime.combine(self.date, self.time)
        match_datetime = timezone.make_aware(match_datetime)
        return timezone.now() <= match_datetime + timedelta(hours=24)
    
    @property
    def can_edit_match(self):
        """Check if match details can still be edited (up to 1 hour after match time)"""
        if not self.time:
            return False
        match_datetime = datetime.combine(self.date, self.time)
        match_datetime = timezone.make_aware(match_datetime)
        return timezone.now() <= match_datetime + timedelta(minutes=60)


