from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from datetime import date
from .forms import MatchForm
from django.shortcuts import render, get_object_or_404
from .models import Match
from participation.models import Participation
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
import io
from accounts.decorators import *
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import translation
from django.contrib.auth.decorators import login_required

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

    return render(request, 'matches/manage_matches.html', {'matches': matches})

@user_passes_test(is_admin)
def create_match(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("matches:manage")  # back to manage matches page
    else:
        form = MatchForm()

    return render(request, "matches/create_match.html", {"form": form})



@active_user_required
@login_required
def view_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    previous_url = request.META.get('HTTP_REFERER', None)


    # Active participants for everyone
    active_participants_ = Participation.objects.filter(match=match, status='joined', removed=False, is_no_show=False)
    active_participants_ = active_participants_.order_by("status_time")

    active_participants = list(active_participants_)
    while len(active_participants) < match.max_players:
        active_participants.append(None)

    # Non active participants for admins only
    non_active_participants = Participation.objects.filter(match=match).exclude(id__in=active_participants_.values_list('id', flat=True)).order_by('-status_time') if request.user.is_superuser else []
    
    context = {
        'match': match,
        'active_participants': active_participants,
        'non_active_participants': non_active_participants,
        'previous_url': previous_url,
        'default_home': reverse('home'),
    }
    return render(request, 'matches/view_match.html', context)

@user_passes_test(is_admin)
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


@user_passes_test(is_admin)
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        return redirect('matches:manage')
    return render(request, 'matches/delete_match.html', {'match': match})


@active_user_required
def download_match_image(request, match_id):

    lang = getattr(request, "LANGUAGE_CODE", None)  # usually set by LocaleMiddleware
    if lang:
        translation.activate(lang)

    match = get_object_or_404(Match, id=match_id)
    participants = match.participation_set.filter(status='joined', removed=False, is_no_show=False)
    max_players = match.max_players
    spots_left = match.spots_left

    # --- Image dimensions ---
    width, height = 800, 50 + max(max_players, len(participants)) * 35 + 400  # dynamic height
    image = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(image)

    # --- Fonts ---
    try:
        title_font = ImageFont.truetype('arialbd.ttf', 28)  # bold title
        header_font = ImageFont.truetype('arialbd.ttf', 22)  # bold header
        text_font = ImageFont.truetype('arial.ttf', 18)
        small_font = ImageFont.truetype('arial.ttf', 16)
    except IOError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # --- Background gradient effect ---
    for i in range(height):
        color_intensity = int(248 + (i / height) * 7)  # subtle gradient
        draw.line([(0, i), (width, i)], fill=(color_intensity, color_intensity + 1, color_intensity + 2))

    # --- Header section with background ---
    header_height = 80
    draw.rectangle([0, 0, width, header_height], fill='#28a745')
    draw.rectangle([0, header_height, width, header_height + 2], fill='#1e7e34')  # border
    
    # Title
    draw.text((width//2 - 150, 25), _("FOOTBALL MATCH"), font=title_font, fill="#ffffff")
    
    # --- Match info section with card-like background ---
    y = header_height + 30
    info_width = width - 100
    info_height = 200
    draw.rectangle([50, y, 50 + info_width, y + info_height], fill="#ffffff", outline="#dee2e6", width=2)
    draw.rectangle([50, y, 50 + info_width, y + 40], fill="#e9ecef")
    
    # Section title
    draw.text((70, y + 10), _("MATCH DETAILS"), font=header_font, fill="#495057")
    
    # Match info with text-based icons and better spacing
    info_y = y + 60
    draw.text((70, info_y), f"Date: {match.day_of_week}, {match.date}", font=text_font, fill="#212529")
    info_y += 35


    # Theses variables were created to translate words inside an f-string
    time_str = _("Time")
    location_str = _("Location")
    players_str = _("Players")
    intotal_str = _("in total")
    spots_left_str = _("spots left")

    draw.text((70, info_y), f"{time_str}: {match.time or 'TBD'}", font=text_font, fill="#212529")
    info_y += 35
    draw.text((70, info_y), f"{location_str}: {match.location_name}", font=text_font, fill="#212529")
    info_y += 35
    draw.text((70, info_y), f"{players_str}: {max_players} {intotal_str} • {spots_left} {spots_left_str}", font=text_font, fill="#28a745" if spots_left > 0 else "#dc3545")

    # --- Participants section ---
    y = header_height + info_height + 50
    draw.rectangle([50, y, 50 + info_width, y + 40], fill="#e9ecef")
    draw.text((70, y + 10), _("PARTICIPANTS"), font=header_font, fill="#495057")
    
    # Participants list with alternating background
    y += 50
    for idx, p in enumerate(participants, start=1):
        if idx % 2 == 0:
            draw.rectangle([50, y - 5, 50 + info_width, y + 30], fill="#f8f9fa")
        draw.text((70, y), f"{idx:2d}. {p.user.username}", font=text_font, fill="#212529")
        y += 35

    # Empty slots with different styling
    for idx in range(len(participants)+1, max_players+1):
        if idx % 2 == 0:
            draw.rectangle([50, y - 5, 50 + info_width, y + 30], fill="#f8f9fa")
        draw.text((70, y), f"{idx:2d}. ---", font=small_font, fill="#6c757d")
        y += 35

    # --- Footer ---
    footer_y = height - 40
    draw.rectangle([0, footer_y, width, height], fill="#343a40")
    draw.text((width//2 - 100, footer_y + 10), _("Join this match on FootyOn!"), font=small_font, fill="#ffffff")

    # --- Return image as downloadable file ---
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='image/png')


    """ Dynamically generate filename:"""
    # Format date
    date_part = match.date.strftime("%d_%m_%Y")  # day_month_year
    time_part = match.time.strftime("%Hh%M") if match.time else "TBD"

    # Translate weekday
    weekday_translated = _(match.day_of_week)  # e.g., "Wednesday" → "Mercredi"

    # Build filename
    filename = f"match_{date_part}_{weekday_translated}_{time_part}.png"

    # Set Content-Disposition
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@active_user_required
def share_on_whatsapp(request, match_id):
    """Generate WhatsApp sharing URL with match details"""
    match = get_object_or_404(Match, id=match_id)
    
    # Create the message text
    message = f"""⚽ *Football Match Alert!*

📅 *{match.day_of_week}, {match.date}*
🕐 *Time:* {match.time or 'TBD'}
🏟️ *Location:* {match.location_name}
👥 *Players:* {match.max_players} total • {match.spots_left} spots left

Join this match on FootyOn!
{request.build_absolute_uri(f'/matches/{match_id}/')}"""
    
    # URL encode the message
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    # Create WhatsApp URL
    whatsapp_url = f"https://wa.me/?text={encoded_message}"
    
    # Redirect to WhatsApp
    return redirect(whatsapp_url)


def share_with_image_instructions(request, match_id):
    """Show instructions for sharing image on WhatsApp"""
    match = get_object_or_404(Match, id=match_id)
    
    context = {
        'match': match,
        'image_url': request.build_absolute_uri(f'/matches/share_image/{match_id}/'),
        'match_url': request.build_absolute_uri(f'/matches/{match_id}/'),
    }
    
    return render(request, 'matches/share_instructions.html', context)



