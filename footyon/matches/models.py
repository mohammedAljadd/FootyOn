from django.db import models
from participation.models import Participation
import calendar
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

from django.utils.translation import gettext_lazy as _

class Match(models.Model):
    date = models.DateField(verbose_name=_("Date"))
    time = models.TimeField(null=True, blank=True, verbose_name=_("Time"))
    day_of_week = models.CharField(max_length=10, verbose_name=_("Day of Week"))
    location_name = models.CharField(max_length=100, verbose_name=_("Location"))
    location_google_maps_embed_url = models.TextField(
        blank=True, null=True, verbose_name=_("Google Maps Embed URL")
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
        """
        Check if the match date and time is in the past.
        Works with self.date (DateField) and self.time (TimeField).
        """

        # Get the current time with timezone awareness (Django handles this in UTC or your set TZ)
        now = timezone.now()

        # Case 1: The match date is before today → already in the past
        if self.date < now.date():
            return True

        # Case 2: The match is today and a time is set
        elif self.date == now.date() and self.time:
            # Combine date and time into a datetime object (naive by default, no timezone info)
            match_datetime = datetime.combine(self.date, self.time)

            # Convert the naive datetime into a timezone-aware one
            # using the project's current timezone (important if USE_TZ=True in settings.py)
            match_datetime = timezone.make_aware(match_datetime, timezone.get_current_timezone())

            # Compare the match datetime with the current datetime
            return match_datetime < now

        # Case 3: Match is in the future (either later today or on a future date)
        return False

    @property
    def can_edit_attendance(self):
        if not self.time:
            return False  # No time set, cannot edit
        match_datetime = datetime.combine(self.date, self.time)
        match_datetime = timezone.make_aware(match_datetime)  # ensure timezone-aware
        return timezone.now() <= match_datetime + timedelta(hours=24)