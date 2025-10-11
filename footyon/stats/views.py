from django.shortcuts import render
from accounts.models import User
from matches.models import Match, Participation
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper, Avg
from matches.models import Match
from collections import defaultdict
import datetime
from django.contrib.auth.decorators import login_required

@login_required
def stats_dashboard(request):

    # annotate each match with attended_count
    # date_lt : less then
    matches_with_attendance = Match.objects.filter(date__lt=now().date()).annotate(
        attended_count=Count(
            'participation',
            filter=Q(participation__status='joined', participation__removed=False),
            distinct=True
        )
    ).annotate( # compute attendance ratio per match
        attendance=ExpressionWrapper(
            F('attended_count') * 1.0 / F('max_players'),
            output_field=FloatField()
        )
    )
    """ F('attended_count') → refers to the calculated field from Step 1.
    F('max_players') → refers to the max_players field in the Match model.
    Multiplying by 1.0 ensures Python/SQL does float division, not integer division.
    ExpressionWrapper(..., output_field=FloatField()) tells Django:
    “this calculation produces a float, store it as such.” """

    # now calculate average attendance
    # .aggregate() is a Django ORM method that calculates a summary across all rows in a queryset.
    average_attendance = matches_with_attendance.aggregate(avg_attendance=Avg('attendance'))['avg_attendance']
    avg_attendance_percent = average_attendance * 100

    # 1️⃣ Fetch all participation objects in one query
    #    - select_related('user', 'match') pulls related objects to avoid extra queries later
    all_participations = Participation.objects.select_related('user', 'match').all()

    # 2️⃣ Organize participations by user_id in a dictionary
    #    - key = user_id, value = list of participations for that user+
    user_participations = defaultdict(list)
    for p in all_participations:
        user_participations[p.user_id].append(p)
    
    # 3️⃣ Loop through all users to calculate stats
    user_stats = []
    for user in User.objects.all().order_by('username'):
     
        # get all participations for this user
        participations = user_participations.get(user.id, [])
        
        # total enrolled = all participations
        total_enrolled = len(participations)
        
        # total times user left = count where status='left'
        total_left = sum(1 for p in participations if p.status == 'left')


        # total absent excused = participations marked as no-show with reason='excused'
        total_absent_excused = sum(
            1 for p in participations if p.is_no_show and p.no_show_reason == 'excused'
        )

        # total absent not excused = participations marked as no-show with reason='not_excused'
        total_absent_not_excused = sum(
            1 for p in participations if p.is_no_show and p.no_show_reason == 'not_excused'
        )

        # total absent not excused = participations marked as no-show with reason='not_excused'
        total_absent_last_minute = sum(
            1 for p in participations if p.is_no_show and p.no_show_reason == 'last_minute'
        )

        


        # append stats for this user to the final list
        attended = sum(1 for p in participations if p.status == 'joined' and not p.removed and not p.is_no_show)


        perc_attended = (attended / total_enrolled * 100) if total_enrolled else 0
        perc_left = (total_left / total_enrolled * 100) if total_enrolled else 0
        perc_absent_excused = (total_absent_excused / total_enrolled * 100) if total_enrolled else 0
        perc_absent_not_excused = (total_absent_not_excused / total_enrolled * 100) if total_enrolled else 0
        perc_absent_last_minute = (total_absent_last_minute / total_enrolled * 100) if total_enrolled else 0


        # score is attended / eligible_participations
        # eligible_participations excluded the following: 
        # no-shows is not set or excused
        eligible_participations = [
            p for p in participations 
            if not (p.no_show_reason == 'excused' or (p.is_no_show == False and p.status == 'left'))
        ]
        
        # 7️⃣ Compute score safely
        attendance_score = (attended / len(eligible_participations)) if eligible_participations else 0
        points_ratio = user.points / 15

        if user.is_suspended and user.suspension_until:
            total_suspension_seconds = datetime.timedelta(days=15).total_seconds()
            remaining_seconds = (user.suspension_until - timezone.now()).total_seconds()
            suspension_penalty = max(0, min(1, remaining_seconds / total_suspension_seconds))
        else:
            suspension_penalty = 0

        past_suspension_penalty = min(0.1, 0.02 * user.suspension_count)  # 2% penalty per past suspension, max 10%

        score = (attendance_score * 0.7 + points_ratio * 0.3) * 100
        score = score * (1 - suspension_penalty) * (1 - past_suspension_penalty)
        
        if(score):
            score = round(score, 2)
            if(int(score) == 100):
                score = 100 
        else:
            score = None


        # We will add last 5 participations to user object
        last_n = 5
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

        last_five_icons = " ".join(icons)


        user_stats.append({
            'username': user.username,
            'total_enrolled': total_enrolled,
            'eligible_participations' : len(eligible_participations),
            'attended': attended,
            'total_left': total_left,
            'total_absent_excused': total_absent_excused,
            'total_absent_not_excused': total_absent_not_excused,
            'total_absent_last_minute': total_absent_last_minute,
            'perc_attended': round(perc_attended, 2),
            'perc_left': round(perc_left, 2),
            'perc_absent_excused': round(perc_absent_excused, 2),
            'perc_absent_not_excused': round(perc_absent_not_excused, 2),
            'perc_absent_last_minute' : round(perc_absent_last_minute, 2), 
            'times_suspended': user.suspension_count,
            'points': user.points,
            'score': score,
            'last_five_icons': last_five_icons,
            'can_participate': user.can_participate(),
        })

    # Sort users by score descending
    user_stats = sorted(
        user_stats,
        key=lambda x: (x['score'] is None, -(x['score'] or 0))
    )
    
    # Get unique scores only from eligible users
    eligible_scores = sorted(
        {u['score'] for u in user_stats if u['score'] is not None and u['can_participate'][0]},
        reverse=True
    )

    
    # Map scores to medals
    score_to_medal = {}
    if len(eligible_scores) > 0:
        score_to_medal[eligible_scores[0]] = 'gold'
    if len(eligible_scores) > 1:
        score_to_medal[eligible_scores[1]] = 'silver'
    if len(eligible_scores) > 2:
        score_to_medal[eligible_scores[2]] = 'bronze'

    # Assign medals to users based on their score
    for user in user_stats:
        can_play, reason = user['can_participate']
        if can_play:
            user['medal'] = score_to_medal.get(user['score'], '')
        else:
            user['medal'] = ''
    months = range(1, 13)  # 1 to 12

    current_year = datetime.date.today().year
    years = range(current_year-1, current_year+2)



    context = {
        "total_matches": matches_with_attendance.count(),
        "matches_with_attendance": matches_with_attendance,
        "avg_attendance_percent": round(avg_attendance_percent, 2),
        "user_stats": user_stats,
        "months": months,
        "years": years,
        "last_n": last_n,
    }
    return render(request, "stats/dashboard.html", context)
