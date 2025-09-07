from functools import wraps
from django.shortcuts import render

def active_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_disabled:
            return render(request, "accounts/disabled_user.html")
        return view_func(request, *args, **kwargs)
    return wrapper
