import json
from datetime import datetime, timedelta
import random

# Current date as reference
today = datetime.now()

# Location data - WITH REAL SHORT URLS
locations = [
    {
        "name": "Stade de l'Ouest",
        "short_url": "https://maps.app.goo.gl/EgACLTbrG48rnAJ3A"
    },
    {
        "name": "Stade Méarelli",
        "short_url": "https://maps.app.goo.gl/B1ZWYDjT83m2mAeH8"
    },
    {
        "name": "Sports Field",
        "short_url": "https://maps.app.goo.gl/1cys5tWqXG81J6oH7"
    },
    {
        "name": "Stade Léon Chabert",
        "short_url": "https://maps.app.goo.gl/26ZftP76XgL6LVyq5"
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
            "location_google_maps_short_url": location["short_url"],
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