import json
from datetime import datetime, timedelta
import random

# Current date as reference
today = datetime.now()

# Location data with real short URLs
locations = [
    {"name": "Stade de l'Ouest", "short_url": "https://maps.app.goo.gl/EgACLTbrG48rnAJ3A"},
    {"name": "Stade Méarelli", "short_url": "https://maps.app.goo.gl/B1ZWYDjT83m2mAeH8"},
    {"name": "Sports Field", "short_url": "https://maps.app.goo.gl/1cys5tWqXG81J6oH7"},
    {"name": "Stade Léon Chabert", "short_url": "https://maps.app.goo.gl/26ZftP76XgL6LVyq5"},
    {"name": "Stade du Ray ", "short_url": "https://maps.app.goo.gl/9mvKTt7HohyBTj4c8"},
]

# Possible times for matches
match_times = ["08:00:00", "17:00:00", "17:30:00", "18:00:00", "10:00:00"]

# Possible max players
max_players_options = [10, 12, 14, 16]

# Days of week
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# -----------------------------
# 1️⃣ Generate Stadiums Fixture
# -----------------------------
stadiums_fixture = []
for idx, loc in enumerate(locations, start=1):
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    stadiums_fixture.append({
        "model": "matches.stadium",
        "pk": idx,
        "fields": {
            "name": loc["name"],
            "google_maps_embed_url": loc["short_url"],  # or convert to embed HTML if desired
            "created_at": now_str,
            "updated_at": now_str
        }
    })

with open('footyon/matches/fixtures/stadiums_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(stadiums_fixture, f, ensure_ascii=False, indent=2)

print(f"Generated {len(stadiums_fixture)} stadiums")

# -----------------------------
# 2️⃣ Generate Matches Fixture
# -----------------------------

matches_fixture = []

# Generate 60 past matches (from 120 days ago to yesterday)
past_dates = [today - timedelta(days=i) for i in range(120, 0, -1)]
selected_past_dates = sorted(random.sample(past_dates, 60))

# Generate 7 future matches (from tomorrow to 30 days ahead)
future_dates = [today + timedelta(days=i) for i in range(1, 31)]
selected_future_dates = sorted(random.sample(future_dates, 7))

# Combine all dates
all_dates = selected_past_dates + selected_future_dates

for idx, match_date in enumerate(all_dates, start=1):
    # Random stadium
    stadium_idx = random.randint(0, len(locations) - 1)
    stadium_pk = stadium_idx + 1  # pk corresponds to stadium fixture
    time = random.choice(match_times)
    max_players = random.choice(max_players_options)
    day_name = days_of_week[match_date.weekday()]

    # created_at
    if match_date < today:
        days_before = random.randint(1, 7)
        created_at = match_date - timedelta(days=days_before)
    else:
        days_ago = random.randint(0, 7)
        created_at = today - timedelta(days=days_ago)

    # updated_at
    updated_at = created_at + timedelta(minutes=random.randint(0, 30))

    match = {
        "model": "matches.match",
        "pk": idx,
        "fields": {
            "date": match_date.strftime("%Y-%m-%d"),
            "time": time,
            "day_of_week": day_name,
            "stadium": stadium_pk,
            "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "max_players": max_players
        }
    }

    matches_fixture.append(match)

with open('footyon/matches/fixtures/matches_fixture.json', 'w', encoding='utf-8') as f:
    json.dump(matches_fixture, f, ensure_ascii=False, indent=2)

print(f"Generated {len(matches_fixture)} matches")
print(f"- 60 past matches (oldest: {selected_past_dates[0].strftime('%Y-%m-%d')}, newest: {selected_past_dates[-1].strftime('%Y-%m-%d')})")
print(f"- 7 future matches (nearest: {selected_future_dates[0].strftime('%Y-%m-%d')}, farthest: {selected_future_dates[-1].strftime('%Y-%m-%d')})")
print(f"Reference date: {today.strftime('%Y-%m-%d')}")
print("\nTo load into Django:")
print("python manage.py loaddata stadiums_fixture.json")
print("python manage.py loaddata matches_fixture.json")