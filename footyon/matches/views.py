from django.shortcuts import render
from .models import Match
from django.contrib.auth.decorators import user_passes_test
from datetime import date

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
