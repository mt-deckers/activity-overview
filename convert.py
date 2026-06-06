#!/bin/python3

import yaml
import json

with open("data/data.yml") as f:
    yml_data = yaml.safe_load(f)

# build years
# labels
data = {
    "years": set([
        key.split("-")[0] if "-" in key else None for key, value in yml_data.items()
    ]),
}

print(yml_data)
print(data)

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
