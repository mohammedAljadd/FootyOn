from django.shortcuts import render
from accounts.models import User
from matches.models import Match, Participation
from django.utils.timezone import now
from django.db.models import Count, Q, F, FloatField, ExpressionWrapper, Avg
from matches.models import Match
from collections import defaultdict

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

        user_stats.append({
            'username': user.username,
            'total_enrolled': total_enrolled,
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
        })

    # sort descending by perc_attended
    user_stats = sorted(user_stats, key=lambda x: x['perc_attended'], reverse=True)


    context = {
        "total_matches": matches_with_attendance.count(),
        "avg_attendance_percent": round(avg_attendance_percent, 2),
        "user_stats": user_stats,
    }
    return render(request, "stats/dashboard.html", context)
