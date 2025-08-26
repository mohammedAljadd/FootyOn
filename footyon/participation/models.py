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

    player = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE)  # string , avoid reference circular import

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')
    status_time = models.DateTimeField(auto_now_add=True) # time when status was set (joined or left)

    # Removed by admin
    removed = models.BooleanField(default=False)
    removed_time = models.DateTimeField(null=True, blank=True)

    is_no_show = models.BooleanField(default=False)
    no_show_reason = models.CharField(
        max_length=20, choices=NO_SHOW_REASON_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return f"{self.player} - {self.match} ({self.status})"