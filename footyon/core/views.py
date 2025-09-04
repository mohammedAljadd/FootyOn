from django.shortcuts import render
from datetime import date
from matches.models import Match
from participation.models import Participation

def home(request):
    """
    Home page view: shows upcoming matches and Join/Leave buttons
    """

    upcoming_matches = Match.objects.filter(date__gte=date.today()).order_by('date', 'time')

    if request.user.is_authenticated:
        for match in upcoming_matches:
            participation = Participation.objects.filter(user=request.user, match=match).first()
            match.user_participation = participation
    
    context = {
        'upcoming_matches': upcoming_matches,
    }
    return render(request, 'home.html', context)
