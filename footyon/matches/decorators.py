from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from .models import Match

def editable_match_required(view_func):
    """
    Decorator that only allows editing matches if match.can_edit_match is True.
    Adds an error message if the match is no longer editable.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        match = kwargs.get('match')
        if match is None:
            match_id = kwargs.get('match_id')
            match = get_object_or_404(Match, id=match_id)
            kwargs['match'] = match  # pass it to view

        if not match.can_edit_match:
            messages.error(request, "This match can no longer be edited (editable up to 1 hour after match time).")
            return redirect('matches:view_match', match_id=match.id)

        return view_func(request, *args, **kwargs)
    return _wrapped_view
