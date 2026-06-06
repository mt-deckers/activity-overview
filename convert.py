#!/bin/python3

import yaml
import json

with open("data/data.yml") as f:
    yml_data = yaml.safe_load(f)

# build years
# labels
data = {
    "years": 123,
}

print(yml_data)

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
