from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import date
from .forms import MatchForm
from django.shortcuts import render, get_object_or_404
from .models import Match
from participation.models import Participation


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def manage_matches(request):
    """
    Page for admin to manage all matches:
    - Upcoming matches: view / modify / delete
    - Past matches: view only
    """
    matches = Match.objects.all().order_by('-date', '-time')  # latest first

    # Annotate matches with an is_past flag
    today = date.today()
    for m in matches:
        m.is_past = m.date < today

    return render(request, 'matches/manage_matches.html', {'matches': matches})


def create_match(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("matches:manage")  # back to manage matches page
    else:
        form = MatchForm()

    return render(request, "matches/create_match.html", {"form": form})


def view_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    # Get all participants for this match
    participants = Participation.objects.filter(match=match)

    context = {
        'match': match,
        'participants': participants,
    }
    return render(request, 'matches/view_match.html', context)