from time import timezone
from django.shortcuts import render, redirect
from participation.models import Participation
from .forms import UserSignupForm
from django.contrib.auth.decorators import user_passes_test
from .models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from collections import defaultdict

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UserSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def manage_accounts(request):

    # 1️⃣ Fetch all Participation objects in a single query
    #    - select_related("user", "match") prefetches related user and match objects
    #      to avoid additional database hits when accessing p.user or p.match later
    all_participations = Participation.objects.select_related("user", "match").all()

    # 2️⃣ Group participations by user_id
    #    - defaultdict(list) automatically creates an empty list for a new key
    #    - Each user's participations will be stored in a list under their user_id
    user_participations = defaultdict(list)
    for p in all_participations:
        user_participations[p.user_id].append(p)

    # 3️⃣ Fetch all users ordered by username
    users = User.objects.all().order_by("username")

    # 4️⃣ Loop through each user and calculate stats
    for user in users:
        # Get all participations for this user; default to empty list if none
        participations = user_participations.get(user.id, [])

        # 5️⃣ Count attended participations
        #    - status="joined" means the user signed up and joined
        #    - not removed ensures we ignore participations that were deleted/removed
        #    - not is_no_show ensures we ignore no-show participations
        attended = sum(
            1 for p in participations if p.status == "joined" and not p.removed and not p.is_no_show
        )

        # 6️⃣ Determine eligible participations for score calculation
        #    - Exclude participations with no_show_reason="excused"
        #    - Exclude participations where the user left early (status="left") but is_no_show is False
        eligible_participations = [
            p for p in participations
            if not (p.no_show_reason == "excused" or (p.is_no_show is False and p.status == "left"))
        ]

        # 7️⃣ Compute score safely
        attendance_score = (attended / len(eligible_participations)) if eligible_participations else 0
        points_ratio = user.points / 15

        if user.is_suspended and user.suspension_until:
            total_suspension_seconds = (timezone.timedelta(days=15)).total_seconds()
            remaining_seconds = (user.suspension_until - timezone.now()).total_seconds()
            suspension_penalty = max(0, min(1, remaining_seconds / total_suspension_seconds))
        else:
            suspension_penalty = 0

        past_suspension_penalty = min(0.1, 0.02 * user.suspension_count)  # 2% penalty per past suspension, max 10%

        score = (attendance_score * 0.7 + points_ratio * 0.3) * 100
        score = score * (1 - suspension_penalty) * (1 - past_suspension_penalty)



   


        # 8️⃣ Dynamically attach the score to the user object
        #    - This makes it easy to access in templates like {{ user.score }}
        if(score):
            user.score = round(score, 2)
        else:
            user.score = None
        user.total_eligible = len(eligible_participations)


        # We will add last 7 participations to user object
        last_n = 7
        last_participations = sorted([p for p in participations if not p.match.can_edit_attendance], key=lambda p: p.match.date, reverse=True)[:last_n]
        last_participations = sorted(last_participations, key=lambda p: p.match.date)
   
   
        icons = []
        for p in last_participations:
            if p.is_active_participant():
                icons.append("✅")
            elif p.no_show_reason == "excused":
                icons.append("⚪")
            else :
                icons.append("❌")

        user.last_five_icons = " ".join(icons)


    return render(request, "accounts/manage_accounts.html", {"users": users, "last_n": last_n})

@user_passes_test(is_admin)
def toggle_account_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Prevent superuser from disabling themselves
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("manage_accounts")

    user.is_disabled = not user.is_disabled
    user.save()

    if user.is_disabled:
        messages.warning(request, _("🚫 %(username)s has been deactivated.") % {'username': user.username})
    else:
        messages.success(request, _("✅ %(username)s has been activated.") % {'username': user.username})

    return redirect("manage_accounts")