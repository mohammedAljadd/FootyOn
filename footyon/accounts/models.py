from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    # Optional flags
    is_recruiter = models.BooleanField(default=False)  # Cannot participate, for demo/resume
    is_disabled = models.BooleanField(default=False)   # Admin-disabled, cannot join future matches

    def can_participate(self):
        """Check if the user can join matches."""
        return self.is_active and not self.is_recruiter and not self.is_disabled
    
    def __str__(self):
        return self.username