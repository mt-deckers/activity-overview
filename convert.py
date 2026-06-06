#!/bin/python3

import yaml
import json

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
    },
}

# walk through monthly data
for key, value in yml_data.items():
    if "-" in key:
        year_key = key.split("-")[0]
        for activity in ['walked', 'ran', 'cycled']:
            # pre-fill
            if year_key not in data['yearly'][activity]:
                data['yearly'][activity][year_key] = 0

            # increment data
            data['yearly'][activity][year_key] += value[activity] or 0

print(yml_data)
print("===")
print(data)

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
