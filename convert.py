#!/bin/python3

import yaml
import json

SWIM_PACE_PER_100M = "3:10"  # min:sec per 100m


def _pace_to_seconds(pace):
    minutes, seconds = pace.split(":")
    return int(minutes) * 60 + int(seconds)


def swim_hours_to_km(hours, pace=SWIM_PACE_PER_100M):
    if not hours:
        return 0
    pace_seconds = _pace_to_seconds(pace)
    return hours * 3600 / pace_seconds * 100 / 1000


with open("data.yml") as f:
    yml_data = yaml.safe_load(f)

# build years
# labels
data = {
    "months": sorted(yml_data.keys()),
    "monthly": {
        "walked": [value["walked"] or None for key, value in yml_data.items()],
        "ran": [value["ran"] or None for key, value in yml_data.items()],
        "cycled": [value["cycled"] or None for key, value in yml_data.items()],
        "swam": [swim_hours_to_km(value.get("swam")) or None for key, value in yml_data.items()],
    },
    "years": sorted(
        set(
            [
                key.split("-")[0] if "-" in key else None
                for key, value in yml_data.items()
            ]
        )
    ),
    "yearly": {
        "walked": {},
        "ran": {},
        "cycled": {},
        "swam": {},
    },
}

# walk through monthly data
for key, value in yml_data.items():
    if "-" in key:
        year_key = key.split("-")[0]
        for activity in ['walked', 'ran', 'cycled', 'swam']:
            # pre-fill
            if year_key not in data['yearly'][activity]:
                data['yearly'][activity][year_key] = 0

            # increment data
            if activity == 'swam':
                amount = swim_hours_to_km(value.get('swam'))
            else:
                amount = value[activity] or 0
            data['yearly'][activity][year_key] += amount

print(yml_data)
print("===")
print(data)

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
