from django.shortcuts import render
from matches.models import Match
from participation.models import Participation

def home(request):
    """
    Home page view
    """

    return render(request, 'home.html')
