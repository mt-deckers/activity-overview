#!/bin/python3

import yaml
import json

ACTIVITIES = ['walked', 'ran', 'cycled', 'swam']


def build_data(yml_data):
    """Transform the raw data.yml mapping into the chart-ready structure.

    Swim is carried through as raw hours (no pace/km conversion); the other
    activities are kilometres.
    """
    data = {
        "months": sorted(yml_data.keys()),
        "monthly": {
            activity: [value.get(activity) or None for key, value in yml_data.items()]
            for activity in ACTIVITIES
        },
        "years": sorted(
            set(
                [
                    key.split("-")[0] if "-" in key else None
                    for key, value in yml_data.items()
                ]
            )
        ),
        "yearly": {activity: {} for activity in ACTIVITIES},
    }

    # walk through monthly data
    for key, value in yml_data.items():
        if "-" in key:
            year_key = key.split("-")[0]
            for activity in ACTIVITIES:
                # pre-fill
                if year_key not in data['yearly'][activity]:
                    data['yearly'][activity][year_key] = 0

                # increment data
                data['yearly'][activity][year_key] += value.get(activity) or 0

    return data


def main():
    with open("data.yml") as f:
        yml_data = yaml.safe_load(f)

    data = build_data(yml_data)

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
