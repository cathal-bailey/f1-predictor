#!/usr/bin/env python3
"""
Fetch 2026 race data for Streamlit upload.
Creates CSV matching test_fe.csv format with estimated features.
"""
import json
import urllib.request
import pandas as pd

BASE_URL = "http://api.jolpi.ca/ergast/f1"

def fetch(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    print(f"Fetching {url}")
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

# Load 2023 driver averages as fallback
test_2023 = pd.read_csv('data/processed/race_driver_records_test_fe.csv')
driver_baselines = test_2023.groupby('driver_name').agg({
    'driver_podium_pct_y2': 'mean',
    'driver_avg_pos_y2': 'mean',
    'driver_podium_pct_y3': 'mean',
    'driver_avg_pos_dry_3y': 'mean',
    'driver_avg_pos_wet_3y': 'mean'
}).to_dict('index')

constructor_baselines = test_2023.groupby('name_constructor').agg({
    'constructor_races_y1': 'mean',
    'constructor_podium_pct_y2': 'mean',
    'constructor_podium_pct_y3': 'mean'
}).to_dict('index')

rows = []

# Get races
races = fetch("2026.json")['MRData']['RaceTable']['Races']
print(f"Found {len(races)} races")

for race in races:
    round_num = int(race['round'])
    race_name = race['raceName']

    # Try to get results
    try:
        results = fetch(f"2026/{round_num}/results.json")['MRData']['RaceTable']['Races'][0]['Results']
        print(f"  {race_name}: {len(results)} results")
    except:
        print(f"  {race_name}: no results yet, skipping")
        continue

    # Try to get qualifying
    try:
        quali = fetch(f"2026/{round_num}/qualifying.json")['MRData']['RaceTable']['Races'][0]['QualifyingResults']
        quali_map = {q['Driver']['driverId']: int(q['position']) for q in quali}
    except:
        quali_map = {}

    for r in results:
        driver_ref = r['Driver']['driverId']
        driver_name = f"{r['Driver']['givenName']} {r['Driver']['familyName']}"
        constructor_name = r['Constructor']['name']

        # Get baseline features or use defaults
        driver_base = driver_baselines.get(driver_name, {})
        constr_base = constructor_baselines.get(constructor_name, {})

        rows.append({
            'year': 2026,
            'round': round_num,
            'grid_position': quali_map.get(driver_ref, 20),
            'driver_podium_pct_y2': driver_base.get('driver_podium_pct_y2', 0.1),
            'driver_avg_pos_y2': driver_base.get('driver_avg_pos_y2', 10),
            'driver_podium_pct_y3': driver_base.get('driver_podium_pct_y3', 0.1),
            'constructor_races_y1': constr_base.get('constructor_races_y1', 20),
            'constructor_podium_pct_y2': constr_base.get('constructor_podium_pct_y2', 0.15),
            'constructor_podium_pct_y3': constr_base.get('constructor_podium_pct_y3', 0.15),
            'driver_avg_pos_dry_3y': driver_base.get('driver_avg_pos_dry_3y', 10),
            'driver_avg_pos_wet_3y': driver_base.get('driver_avg_pos_wet_3y', 10),
            'driver_name': driver_name,
            'name': race_name,
            'is_podium': 1 if int(r.get('position', 99)) <= 3 else 0
        })

df = pd.DataFrame(rows)
df.to_csv('2026_races_for_streamlit.csv', index=False)
print(f"\n✓ Saved 2026_races_for_streamlit.csv ({len(df)} records)")
print("Upload this file in Streamlit (uncheck 'Use data provided')")
