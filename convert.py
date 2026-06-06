#!/bin/python3

import yaml
import json

with open("data.yml") as f:
    yml_data = yaml.safe_load(f)

# build years
# labels
data = {
    "years": sorted(
        set(
            [
                key.split("-")[0] if "-" in key else None
                for key, value in yml_data.items()
            ]
        )
    ),
    "months": sorted(yml_data.keys()),
    "monthly": {
        "walked": [value["walked"] for key, value in yml_data.items()],
        "ran": [value["ran"] for key, value in yml_data.items()],
        "cycled": [value["cycled"] for key, value in yml_data.items()]
    },
}

print(yml_data)
print("===")
print(data)

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
