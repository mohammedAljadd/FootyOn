from django.db import models
from accounts.models import User

class Participation(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('left', 'Left'),
    ]

    NO_SHOW_REASON_CHOICES = [
        ('excused', 'Excused'),
        ('not_excused', 'Not Excused'),
        ('last_minute', 'Last Minute'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE)  # string , avoid reference circular import

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')
    status_time = models.DateTimeField(auto_now_add=True) # time when status was set (joined or left)

    # Removed by admin
    removed = models.BooleanField(default=False)
    removed_time = models.DateTimeField(null=True, blank=True)

    is_no_show = models.BooleanField(default=False)

    # This field stores the reason why a participant didn't show up
    # It's optional (null=True, blank=True) because not every participant will have a no-show reason
    no_show_reason = models.CharField(
        max_length=20, choices=NO_SHOW_REASON_CHOICES, null=True, blank=True
    )
    no_show_time = models.DateTimeField(null=True, blank=True)

    # Track attendance: mark participants who actually show up to the match.
    # This makes it easy to determine no-shows without manually checking.
    is_present = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user} - {self.match} ({self.status})"
    

    # Helper method to check if the participant is active (joined and not removed or no-show)
    # better than checking multiple fields in views or serializers
    def is_active_participant(self):
        return self.status == 'joined' and not self.removed and not self.is_no_show