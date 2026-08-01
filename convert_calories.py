#!/bin/python3
"""Transform a local, sensitive active-calories export into an abstracted,
committable heatmap dataset.

The raw CSV (activity_calories-export.csv, gitignored) holds real daily calorie
numbers. We never commit those: each day is reduced to a color (a lossy, cold->hot
abstraction of intensity) plus a `highlight` flag for the >1400 "mega" days.
"""

import csv
import json

# Four discrete bands (kcal) -> one flat color each. Discrete (not a gradient) keeps
# the calendar calm to read and only reveals the band, never an approximate value.
# Days with no data are not a band: value_to_color returns None and they render blank.
CRUISE_START = 600   # 1..599      under the weather
WORK_START = 900     # 600..899    cruising
MEGA_START = 1401    # 900..1400   putting in work;  >1400  MEGA (animated)

UNDER_COLOR = "#6b7280"   # 1-599     under the weather (gray)
CRUISE_COLOR = "#3b82f6"  # 600-899   cruising (the walking blue = the norm)
WORK_COLOR = "#ef4444"    # 900-1400  putting in work (red)
MEGA_COLOR = "#fde047"    # >1400     MEGA (CSS animation carries the "on fire" feel)


def value_to_color(value):
    """Value (kcal) -> one of four band colors, or None for a no-data day (blank)."""
    if not value or value <= 0:
        return None
    if value >= MEGA_START:
        return MEGA_COLOR
    if value >= WORK_START:
        return WORK_COLOR
    if value >= CRUISE_START:
        return CRUISE_COLOR
    return UNDER_COLOR


def build_data(rows):
    """rows: iterable of (date_str, value). Returns the committable heatmap dict.

    Raw values are consumed here and never stored — only date/color/highlight.
    """
    days = []
    for date, value in rows:
        color = value_to_color(value)
        if color is None:
            continue  # blank day: omit; the grid renders an empty cell
        days.append({
            "date": date,
            "color": color,
            "highlight": value >= MEGA_START,
        })

    days.sort(key=lambda d: d["date"])
    dates = [d["date"] for d in days]
    return {
        "start": dates[0] if dates else None,
        "end": dates[-1] if dates else None,
        "megaCount": sum(1 for d in days if d["highlight"]),
        "days": days,
    }


def read_csv(path):
    """Yield (date, int value) from the export, skipping the header/blank rows."""
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header: activity_calories_date,activity_calories_value
        for row in reader:
            if len(row) < 2 or not row[0].strip():
                continue
            try:
                yield row[0].strip(), int(float(row[1]))
            except ValueError:
                continue  # non-numeric value: skip


def main():
    data = build_data(read_csv("activity_calories-export.csv"))
    with open("calories.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
