from datetime import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):

    # Optional flags
    is_recruiter = models.BooleanField(default=False)  # Cannot participate, for demo/resume
    is_disabled = models.BooleanField(default=False)   # Admin-disabled, cannot join future matches


    # Points system
    points = models.IntegerField(default=15)  # like a driving license, full = 15
    is_suspended = models.BooleanField(default=False)  # temporarily suspended
    suspension_until = models.DateTimeField(null=True, blank=True)
    suspension_count = models.IntegerField(default=0)  # how many suspensions so far

    def can_participate(self):
        """ Determine if user can join matches """
        self.check_suspension_over() # auto check if suspension is over
        if not self.is_active or self.is_recruiter:
            return [False, "inactive_or_recruiter"]
        if self.is_disabled:  # permanent
            return [False, "disabled"]
        if self.suspension_until and self.suspension_until > timezone.now():  # temporary
            return [False, "suspended"]
        return [True, "can_participate"]

    
    def __str__(self):
        return self.username
    


    def update_suspension_status(self, no_show_reason, reverse=False):
        if not self.can_participate():
            return False
        
        if no_show_reason == "excused":
            point_deduction = 0
            return
        elif no_show_reason == "not_excused":
            point_deduction = 4
        elif no_show_reason == "last_minute":
            point_deduction = 2

        if(reverse == False):
            self.points -= point_deduction
        elif(reverse == True):
            self.points += point_deduction

        # Check for suspension
        if self.points <= 0 and not reverse:
            self.is_suspended = True
            self.suspension_count += 1
            self.points = 0

            # Set suspension duration (e.g., 15 days)
            self.suspension_until = timezone.now() + timezone.timedelta(days=15)

            # check if player abused the system, 5 suspensions = permanent disable
            if self.suspension_count >= 5:
                self.is_disabled = True
                self.is_suspended = False
                self.suspension_until = None


        if(reverse):
            if self.is_suspended and self.points > 0:
                self.is_suspended = False
                self.suspension_until = None

        if self.points > 15:
                self.points = 15  # max points is 15

        self.save()


    # check if suppension is over
    def check_suspension_over(self):
        if self.is_suspended and self.suspension_until and self.suspension_until <= timezone.now():
            self.is_suspended = False
            self.suspension_until = None
            self.points = 15  # reset points to full
            self.save()
            return True
        return False