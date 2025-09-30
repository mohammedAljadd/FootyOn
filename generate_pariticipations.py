# python generate_pariticipations.py && cd footyon/ &&  python manage.py loaddata participations_fixture.json

import json
import random
from datetime import datetime, timedelta

# Load existing fixtures
with open('footyon/accounts/fixtures/users_fixture.json', 'r', encoding='utf-8') as f:
    users = json.load(f)

with open('footyon/matches/fixtures/matches_fixture.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

# Extract user IDs
user_ids = [user['pk'] for user in users]

# Current date for reference
today = datetime.now()

participations = []
participation_id = 1

# Separate past and future matches
past_matches = []
future_matches = []

for match in matches:
    match_date = datetime.strptime(match['fields']['date'], '%Y-%m-%d')
    if match_date < today:
        past_matches.append(match)
    else:
        future_matches.append(match)

# Select half of future matches to fill
num_future_to_fill = len(future_matches) // 2
future_matches_to_fill = random.sample(future_matches, num_future_to_fill)

# Combine matches to process
matches_to_fill = past_matches + future_matches_to_fill

# Track which matches will have n-1 players (2-3 matches)
matches_with_n_minus_1 = random.sample(matches_to_fill, min(3, len(matches_to_fill)))

print(f"Processing {len(matches_to_fill)} matches:")
print(f"  - {len(past_matches)} past matches")
print(f"  - {len(future_matches_to_fill)} future matches")
print(f"  - {len(matches_with_n_minus_1)} matches will have n-1 players\n")

for match in matches_to_fill:
    match_id = match['pk']
    match_date_str = match['fields']['date']
    match_time_str = match['fields']['time']
    match_created_at = datetime.strptime(match['fields']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    max_players = match['fields']['max_players']
    
    # Combine date and time to get full match datetime
    match_datetime = datetime.strptime(f"{match_date_str} {match_time_str}", '%Y-%m-%d %H:%M:%S')
    
    is_past_match = match_datetime < today
    
    # Decide if this match should have n-1 players
    if match in matches_with_n_minus_1:
        num_players = max_players - 1
    else:
        num_players = max_players
    
    # Select random users for this match
    selected_users = random.sample(user_ids, num_players + random.randint(1, 4))  # Extra for "left" status
    
    # Decide how many will have "left" status (0-3)
    num_left = random.randint(0, min(3, len(selected_users) - num_players))
    
    # Decide how many "joined" players will be removed (0-2)
    num_removed = random.randint(0, min(2, num_players))
    
    # Track users in different categories
    joined_users = selected_users[:num_players]
    left_users = selected_users[num_players:num_players + num_left]
    
    # For removed users, we need to add replacements
    removed_users = []
    replacement_users = []
    if num_removed > 0:
        removed_users = random.sample(joined_users, num_removed)
        # Get replacement users (not already selected)
        available_for_replacement = [uid for uid in user_ids if uid not in selected_users]
        replacement_users = random.sample(available_for_replacement, num_removed)
        
        # Add replacement users to selected_users and joined_users
        selected_users.extend(replacement_users)
        joined_users.extend(replacement_users)
    
    # For past matches: decide attendance (present/no-show)
    if is_past_match:
        # 70-90% show up, rest are no-shows
        show_up_rate = random.uniform(0.70, 0.90)
        num_present = int(len(joined_users) * show_up_rate)
        present_users = random.sample(joined_users, num_present)
        no_show_users = [u for u in joined_users if u not in present_users]
    else:
        present_users = []
        no_show_users = []
    
    # Create participations for joined users
    for user_id in joined_users:
        # Status time: random time between match creation and match date (or today for future matches)
        time_window_start = match_created_at
        time_window_end = min(match_datetime, today) if is_past_match else today
        
        days_diff = (time_window_end - time_window_start).days
        if days_diff > 0:
            random_days = random.randint(0, days_diff)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            status_time = time_window_start + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        else:
            status_time = time_window_start
        
        # Ensure status_time is in the past
        if status_time > today:
            status_time = today - timedelta(hours=random.randint(1, 48))
        
        # Check if this user was removed
        was_removed = user_id in removed_users
        removed_time = None
        
        if was_removed:
            # Removed time is after they joined but before match (and must be in past)
            max_days_until_removal = (min(match_datetime, today) - status_time).days
            if max_days_until_removal > 0:
                removed_time = status_time + timedelta(days=random.randint(1, max_days_until_removal))
            else:
                removed_time = status_time + timedelta(hours=random.randint(1, 12))
            
            # Ensure removed_time is in the past
            if removed_time > today:
                removed_time = today - timedelta(hours=random.randint(1, 24))
        
        # Check attendance for past matches
        is_present = user_id in present_users if is_past_match else False
        is_no_show = user_id in no_show_users if is_past_match else False
        no_show_reason = None
        
        if is_no_show:
            no_show_reason = random.choice(['excused', 'not_excused', 'last_minute'])
        
        participation = {
            "model": "participation.participation",
            "pk": participation_id,
            "fields": {
                "user": user_id,
                "match": match_id,
                "status": "joined",
                "status_time": status_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                "removed": was_removed,
                "removed_time": removed_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z" if removed_time else None,
                "is_no_show": is_no_show,
                "no_show_reason": no_show_reason,
                "is_present": is_present
            }
        }
        participations.append(participation)
        participation_id += 1
    
    # Create participations for left users
    for user_id in left_users:
        # Decide if this is a "last minute" leave (within 59 minutes of match start)
        is_last_minute = random.random() < 0.3  # 30% chance
        
        if is_last_minute and is_past_match:
            # Left within 59 minutes before match
            minutes_before = random.randint(1, 59)
            left_time = match_datetime - timedelta(minutes=minutes_before)
            
            # Joined earlier (at least 1 day before)
            days_before_join = random.randint(1, max(1, (match_datetime - match_created_at).days))
            join_time = match_datetime - timedelta(days=days_before_join)
        else:
            # Joined first (normal timing)
            time_window = (match_datetime - match_created_at).days
            if time_window > 0:
                join_time = match_created_at + timedelta(days=random.randint(0, time_window // 2))
            else:
                join_time = match_created_at
            
            # Then left (after joining, before match, but not last minute)
            time_after_join = match_datetime - join_time
            days_after = random.randint(1, max(1, time_after_join.days))
            left_time = join_time + timedelta(days=days_after)
            
            # Ensure not within 59 minutes of match
            if (match_datetime - left_time).total_seconds() < 3600:  # less than 1 hour
                left_time = match_datetime - timedelta(hours=random.randint(2, 24))
        
        # Ensure left_time is in the past
        if left_time > today:
            left_time = today - timedelta(hours=random.randint(1, 24))
        
        # For past matches with last-minute leaves, mark as no-show with last_minute reason
        is_no_show_last_minute = is_last_minute and is_past_match
        
        participation = {
            "model": "participation.participation",
            "pk": participation_id,
            "fields": {
                "user": user_id,
                "match": match_id,
                "status": "left",
                "status_time": left_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                "removed": False,
                "removed_time": None,
                "is_no_show": is_no_show_last_minute,
                "no_show_reason": "last_minute" if is_no_show_last_minute else None,
                "is_present": False
            }
        }
        participations.append(participation)
        participation_id += 1

# Write to JSON file
with open('footyon/participation/fixtures/participations_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(participations, f, ensure_ascii=False, indent=2)

print(f"\nGenerated {len(participations)} participations")
print(f"File saved as: footyon/participation/fixtures/participations_fixture.json")
print("\nTo load into Django:")
print("python manage.py loaddata participations_fixture.json")

# Statistics
num_joined = sum(1 for p in participations if p['fields']['status'] == 'joined')
num_left = sum(1 for p in participations if p['fields']['status'] == 'left')
num_removed = sum(1 for p in participations if p['fields']['removed'])
num_present = sum(1 for p in participations if p['fields']['is_present'])
num_no_show = sum(1 for p in participations if p['fields']['is_no_show'])

print(f"\nStatistics:")
print(f"  - Joined: {num_joined}")
print(f"  - Left: {num_left}")
print(f"  - Removed: {num_removed}")
print(f"  - Present (past matches): {num_present}")
print(f"  - No-show (past matches): {num_no_show}")