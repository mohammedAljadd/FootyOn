from functools import wraps
from django.utils import timezone
from django.shortcuts import render

def active_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # This will reset suspension if it's over
        if user.is_authenticated:
            user.can_participate()

        if not user.is_authenticated:
            return view_func(request, *args, **kwargs)

        if user.is_disabled:
            return render(request, "accounts/disabled_user.html")

        if user.is_suspended and user.suspension_until:
            delta = user.suspension_until - timezone.now()
            if delta.total_seconds() > 0:
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, _ = divmod(remainder+60, 60)
            else:
                days = hours = minutes = 0

            return render(
                request,
                "accounts/suspended_user.html",
                {
                    "days_left": days,
                    "hours_left": hours,
                    "minutes_left": minutes,
                }
            )

        return view_func(request, *args, **kwargs)

    return wrapper
