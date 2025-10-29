#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
import pandas as pd

def aggregate_workouts(filename):
    totals = {"walked": 0, "ran": 0, "cycled": 0}
    yearly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})
    monthly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})

    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        rows = list(reader)

    for r in rows:
        if not r or len(r) < 4:
            continue
        try:
            dt = datetime.strptime(r[0], "%Y-%m-%d")
        except ValueError:
            continue

        def parse_num(x): return float(x.replace(",", ".") or 0)

        walked, ran, cycled = parse_num(r[1]), parse_num(r[2]), parse_num(r[3])

        totals["walked"] += walked
        totals["ran"] += ran
        totals["cycled"] += cycled

        y = dt.year
        yearly[y]["walked"] += walked
        yearly[y]["ran"] += ran
        yearly[y]["cycled"] += cycled

        ym = dt.strftime("%Y-%m")
        monthly[ym]["walked"] += walked
        monthly[ym]["ran"] += ran
        monthly[ym]["cycled"] += cycled

    output = {
        "totals": totals,
        "yearly": dict(yearly),
        "monthly": dict(monthly),
    }

    out = "workout_data.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Workout data aggregated → {out}")


def aggregate_body(filename):
    # Detect delimiter
    with open(filename) as f:
        first_line = f.readline()
    sep = "\t" if "\t" in first_line else ","

    df = pd.read_csv(filename, sep=sep)
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Clean numeric columns
    df["Weight"] = df["Weight"].str.replace("kg", "", regex=False).astype(float)
    df["Body_Fat"] = df["Body_Fat"].str.replace("%", "", regex=False).astype(float)
    df["Body_age"] = df["Body_age"].astype(int)

    # Parse datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%H:%M %b.%d %Y", errors="coerce")
    df = df.dropna(subset=["Date"])

    # Monthly averages
    df["Month"] = df["Date"].dt.to_period("M")
    monthly_avg = (
        df.groupby("Month")[["Weight", "Body_Fat", "Body_age"]]
        .mean()
        .reset_index()
    )
    monthly_avg["Month"] = monthly_avg["Month"].astype(str)

    out = "body_data.json"
    monthly_avg.to_json(out, orient="records", indent=2)
    print(f"✅ Body metrics aggregated → {out}")


def main():
    parser = argparse.ArgumentParser(description="Aggregate workout or body metric data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # workouts
    p_work = subparsers.add_parser("workouts", help="Aggregate walked/ran/cycled data.")
    p_work.add_argument("file", help="Input CSV with walked/ran/cycled columns.")

    # body
    p_body = subparsers.add_parser("body", help="Aggregate body metric data.")
    p_body.add_argument("file", help="Input CSV/TSV with Date, Weight, Body Fat, Body age.")

    args = parser.parse_args()

    if args.command == "workouts":
        aggregate_workouts(args.file)
    elif args.command == "body":
        aggregate_body(args.file)


if __name__ == "__main__":
    main()
