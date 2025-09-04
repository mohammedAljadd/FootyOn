from django.shortcuts import render
from datetime import date
from matches.models import Match
from participation.models import Participation

def home(request):
    """
    Home page view: shows upcoming matches and Join/Leave buttons
    """

    upcoming_matches = Match.objects.filter(date__gte=date.today()).order_by('date', 'time')
    
    context = {
        'upcoming_matches': upcoming_matches,
    }
    return render(request, 'home.html', context)
