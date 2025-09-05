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


from django.urls import reverse

def view_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    previous_url = request.META.get('HTTP_REFERER', None)


    # Active participants for everyone
    active_participants = Participation.objects.filter(match=match, status='joined')

    # Left participants for admins only
    left_participants = Participation.objects.filter(match=match).exclude(status='joined') if request.user.is_superuser else []


    context = {
        'match': match,
        'active_participants': active_participants,
        'left_participants': left_participants,
        'previous_url': previous_url,
        'default_home': reverse('home'),
    }
    return render(request, 'matches/view_match.html', context)


def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    joined_count = Participation.objects.filter(match=match, status='joined').count()

    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()  # No add_error
            return redirect('matches:manage')
    else:
        form = MatchForm(instance=match)

    return render(
        request,
        'matches/edit_match.html',
        {
            'form': form,
            'match': match,
            'joined_count': joined_count,
        }
    )



def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('matches:manage')
    return render(request, 'matches/delete_match.html', {'match': match})