import json
from datetime import datetime, timedelta
import random

# Current date as reference
today = datetime.now()

# Location data
locations = [
    {
        "name": "Stade de l'Ouest",
        "embed_url": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d5771.754568025031!2d7.2023399756581945!3d43.67152195124643!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12cdd10c3345b9bd%3A0x8a5dc01882b070a3!2sStade%20de%20l%27Ouest!5e0!3m2!1sen!2sfr!4v1759203079254!5m2!1sen!2sfr" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    },
    {
        "name": "Stade Méarelli",
        "embed_url": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d5771.776071542516!2d7.210152075658169!3d43.671298351260845!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12cdd1050d36302b%3A0x9fcb72d4a4778b66!2sStade%20M%C3%A9arelli!5e0!3m2!1sen!2sfr!4v1759203141389!5m2!1sen!2sfr" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    },
    {
        "name": "Sports Field",
        "embed_url": '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d10493.898219650906!2d7.200583880764323!3d43.67280736030106!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x12cdd17585555555%3A0xadcff84be77756f5!2sSports%20Field!5e0!3m2!1sen!2sfr!4v1759203167192!5m2!1sen!2sfr" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    }
]

# Possible times for matches
match_times = ["18:00:00", "19:00:00", "20:00:00", "21:00:00"]

# Possible max players
max_players_options = [10, 12, 14, 16]

# Days of week
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

matches = []

# Generate 25 past matches (from 60 days ago to yesterday)
past_dates = []
for i in range(60, 0, -1):
    date = today - timedelta(days=i)
    # Only include dates, we'll select 25 random ones
    past_dates.append(date)

# Randomly select 25 dates from the past
selected_past_dates = random.sample(past_dates, 25)
selected_past_dates.sort()

# Generate 5 future matches (from tomorrow to 30 days ahead)
future_dates = []
for i in range(1, 31):
    date = today + timedelta(days=i)
    future_dates.append(date)

# Randomly select 5 dates for future matches
selected_future_dates = random.sample(future_dates, 5)
selected_future_dates.sort()

# Combine all dates
all_dates = selected_past_dates + selected_future_dates

# Generate match fixtures
for idx, match_date in enumerate(all_dates, start=1):
    location = random.choice(locations)
    time = random.choice(match_times)
    max_players = random.choice(max_players_options)
    day_name = days_of_week[match_date.weekday()]
    
    # For created_at, use dates before the match date for past matches
    if match_date < today:
        # Created 1-7 days before the match
        days_before = random.randint(1, 7)
        created_at = match_date - timedelta(days=days_before)
    else:
        # For future matches, created recently (within last 7 days or today)
        days_ago = random.randint(0, min(7, (today - (today - timedelta(days=60))).days))
        created_at = today - timedelta(days=days_ago)
    
    # For updated_at, set it to the same as created_at or slightly after
    updated_at = created_at + timedelta(minutes=random.randint(0, 30))
    
    match = {
        "model": "matches.match",
        "pk": idx,
        "fields": {
            "date": match_date.strftime("%Y-%m-%d"),
            "time": time,
            "day_of_week": day_name,
            "location_name": location["name"],
            "location_google_maps_url": location["embed_url"],
            "location_google_maps_embed_url": location["embed_url"],
            "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "max_players": max_players
        }
    }
    
    matches.append(match)

# Write to JSON file
with open('footyon/matches/fixtures/matches_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f"Generated {len(matches)} matches")
print(f"- 25 past matches (oldest: {selected_past_dates[0].strftime('%Y-%m-%d')}, newest: {selected_past_dates[-1].strftime('%Y-%m-%d')})")
print(f"- 5 future matches (nearest: {selected_future_dates[0].strftime('%Y-%m-%d')}, farthest: {selected_future_dates[-1].strftime('%Y-%m-%d')})")
print(f"Reference date: {today.strftime('%Y-%m-%d')}")
print("\nFile saved as: matches_fixture.json")
print("\nTo load into Django:")
print("python manage.py loaddata matches_fixture.json")