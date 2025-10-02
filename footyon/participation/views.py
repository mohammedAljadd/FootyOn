from django.contrib.auth.decorators import login_required
from matches.models import Match
from .models import Participation
from .forms import NoShowForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import active_user_required
from django.utils import timezone

@login_required
@active_user_required
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
@active_user_required
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
            participation.no_show_time = timezone.now()
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
    match = participation.match

    if request.method == "POST":
        # Step 1: Check if form already confirmed
        if 'confirm' in request.POST and request.POST['confirm'] == 'yes':
            
            if match.spots_left > 0:
                
                # Admin confirmed → remove no-show
                participation.is_no_show = False
                participation.no_show_reason = None
                participation.no_show_time = None
                participation.save()
                messages.success(request, f"No-show removed for {participation.user.username}.")
                return redirect('matches:view_match', match_id=match.id)
            
            if new_capacity := request.POST.get('new_capacity'):
                new_capacity = int(new_capacity)
                match.max_players = new_capacity
                match.save()
                participation.is_no_show = False
                participation.no_show_reason = None
                participation.save()
                messages.success(request, f"No-show removed for {participation.user.username} with new capacity {new_capacity}.")
                return redirect('matches:view_match', match_id=match.id)

            return render(request, 'participation/increase_capacity.html', {'participation': participation, 'match': match})
        
        # Step 2: Show confirmation page first
        return render(request, 'participation/confirm_remove_no_show.html', {
            'participation': participation,
            'match': match
        })

    # GET request → redirect back
    return redirect('matches:view_match', match_id=match.id)





@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only admin
def remove_participant(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    participation.removed = True
    participation.removed_time = timezone.now()
    participation.status = 'joined' # because status_time is not changed, we leave this as joined, convenient
    participation.save()

    messages.success(request, f"{participation.user.username} has been removed from the match.")
    return redirect('matches:view_match', match_id=participation.match.id)

@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only admin
def restore_participant(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    match = participation.match

    if request.method == "POST":
        # Step 1: Capacity increase form submitted
        if 'new_capacity' in request.POST:
            new_capacity = int(request.POST['new_capacity'])
            match.max_players = new_capacity
            match.save()
            participation.removed = False
            participation.save()
            messages.success(request, f"{participation.user.username} added back with new capacity {new_capacity}.")
            return redirect('matches:view_match', match_id=match.id)

        # Step 2: Initial confirm restore
        if 'confirm' not in request.POST or request.POST['confirm'] == 'no':
            return render(request, 'participation/confirm_restore.html', {'participation': participation, 'match': match})

        # Step 3: Enough spots: restore directly
        if match.spots_left > 0:
            participation.removed = False
            participation.save()
            messages.success(request, f"{participation.user.username} added back.")
            return redirect('matches:view_match', match_id=match.id)

        # Step 4: No spots left → show capacity increase form
        return render(request, 'participation/increase_capacity.html', {'participation': participation, 'match': match})

    # GET → redirect back
    return redirect('matches:view_match', match_id=match.id)



@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only admin
def mark_present(request, participation_id):
    """Mark a participant as present."""
    participation = get_object_or_404(Participation, id=participation_id)
    participation.is_present = True
    participation.save()
    # Redirect back to match view
    return redirect('matches:view_match', match_id=participation.match.id)


@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only admin
def remove_present(request, participation_id):
    """Remove the present mark if admin made a mistake."""
    participation = get_object_or_404(Participation, id=participation_id)
    participation.is_present = False
    participation.save()
    return redirect('matches:view_match', match_id=participation.match.id)


# Permanently delete a participation record
# Differentiate from "remove_participant" which is a soft remove
@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_participation(request, participation_id):
    participation = get_object_or_404(Participation, id=participation_id)
    match = participation.match

    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            username = participation.user.username
            participation.delete()
            messages.error(request, f"⚠️ {username}'s participation was permanently deleted.")
            return redirect('matches:view_match', match_id=match.id)

        # If canceled → redirect back
        return redirect('matches:view_match', match_id=match.id)

    # GET request → show confirmation page
    return render(request, 'participation/confirm_hard_delete.html', {
        'participation': participation,
        'match': match
    })
