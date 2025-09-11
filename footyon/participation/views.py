from django.contrib.auth.decorators import login_required
from matches.models import Match
from .models import Participation
from .forms import NoShowForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test
from accounts.decorators import active_user_required


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


from django.utils import timezone
from django.contrib import messages

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

    if not request.user.is_superuser:
        messages.error(request, "You don’t have permission to restore participants.")
        return redirect('matches:view_match', match_id=participation.match.id)

    participation.removed = False
    participation.removed_time = None
    participation.save()

    messages.success(request, f"{participation.user.username} was added back to the match.")
    return redirect('matches:view_match', match_id=participation.match.id)


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


# participation/views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from matches.models import Match  # Adjust import as needed
from .models import Participation


@login_required
@ensure_csrf_cookie
def scan_qr(request):
    """Page with camera to scan QR code."""
    return render(request, 'participation/scan_qr.html')


@login_required
@require_POST
def confirm_presence(request):
    """Mark user as present via QR token."""
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        token = data.get('qr_token')
        
        if not token:
            return JsonResponse({
                'success': False, 
                'message': 'No QR token provided'
            })
        
        # Find match by QR token
        try:
            match = Match.objects.get(qr_token=token)
        except Match.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid QR code. Match not found.'
            })
        
        # Check if match is still active/joinable
        # Add your business logic here (e.g., time restrictions)
        
        # Create or update participation
        participation, created = Participation.objects.get_or_create(
            user=request.user, 
            match=match,
            defaults={'status': 'joined', 'is_present': True}
        )
        
        if not created:
            if participation.is_present:
                return JsonResponse({
                    'success': True, 
                    'message': f'Already marked present for {match.title or "this match"}!'
                })
            participation.is_present = True
            participation.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'✅ Successfully marked present for {match.title or "this match"}!'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid request data'
        })
    except Exception as e:
        # Log the error in production
        print(f"Error in confirm_presence: {e}")
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred. Please try again.'
        })


import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from matches.models import Match  # Adjust import as needed
from .models import Participation


@login_required
@ensure_csrf_cookie
def scan_qr(request):
    """Page with camera to scan QR code."""
    return render(request, 'participation/scan_qr.html')


@login_required
@require_POST
def confirm_presence(request):
    """Mark user as present via QR token."""
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        token = data.get('qr_token')
        
        if not token:
            return JsonResponse({
                'success': False, 
                'message': 'No QR token provided'
            })
        
        # Find match by QR token
        try:
            match = Match.objects.get(qr_token=token)
        except Match.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid QR code. Match not found.'
            })
        
        # Check if match is still active/joinable
        # Add your business logic here (e.g., time restrictions)
        
        # Create or update participation
        participation, created = Participation.objects.get_or_create(
            user=request.user, 
            match=match,
            defaults={'status': 'joined', 'is_present': True}
        )
        
        if not created:
            if participation.is_present:
                return JsonResponse({
                    'success': True, 
                    'message': f'Already marked present for {match.title or "this match"}!'
                })
            participation.is_present = True
            participation.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'✅ Successfully marked present for {match.title or "this match"}!'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid request data'
        })
    except Exception as e:
        # Log the error in production
        print(f"Error in confirm_presence: {e}")
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred. Please try again.'
        })