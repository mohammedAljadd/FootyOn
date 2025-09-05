from django.contrib.auth.decorators import login_required
from matches.models import Match
from .models import Participation
from .forms import NoShowForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test



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




@user_passes_test(lambda u: u.is_superuser)
def mark_no_show(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)

    if request.method == 'POST':
        form = NoShowForm(request.POST, instance=participation)
        if form.is_valid():
            participation.is_no_show = True
            form.save()
            return redirect('matches:view_match', match_id=participation.match.id)
    else:
        form = NoShowForm(instance=participation)

    return render(request, 'participation/mark_no_show.html', {
        'form': form,
        'participation': participation,
    })

@user_passes_test(lambda u: u.is_superuser)
def remove_no_show(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    
    if not participation.is_no_show:
        messages.warning(request, f"{participation.user.username} is not marked as no-show.")
    else:
        participation.is_no_show = False
        participation.no_show_reason = None
        participation.save()
        messages.success(request, f"No-show removed for {participation.user.username}.")

    # Redirect back to the match view
    return redirect('matches:view_match', match_id=participation.match.id)