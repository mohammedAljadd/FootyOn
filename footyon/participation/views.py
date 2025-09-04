from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from matches.models import Match
from .models import Participation

@login_required
def join_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Check if user already joined
    participation, created = Participation.objects.get_or_create(
        user=request.user,
        match=match,
        defaults={'status': 'joined'}
    )

    # If participation existed but status was 'left', update it
    if not created and participation.status != 'joined':
        participation.status = 'joined'
        participation.save()

    return redirect('home')  # back to home page


@login_required
def leave_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    try:
        participation = Participation.objects.get(user=request.user, match=match)
        participation.status = 'left'
        participation.save()
    except Participation.DoesNotExist:
        # User never joined, ignore
        pass

    return redirect('home')
