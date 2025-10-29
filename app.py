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
    import numpy as np

    # Detect delimiter
    with open(filename) as f:
        first_line = f.readline().strip()
    sep = "\t" if "\t" in first_line else ","

    # Try reading with header first; fallback to no header
    try:
        df = pd.read_csv(filename, sep=sep)
        if not set(df.columns).intersection({"Date", "Weight", "Body Fat", "Body_Fat"}):
            raise ValueError
    except Exception:
        df = pd.read_csv(filename, sep=sep, header=None,
                         names=["Date", "Weight", "Body_Fat", "Body_age"])

    # Normalize column names
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Clean numeric values
    def clean(col, unit=None):
        s = df[col].astype(str).replace("--", np.nan)
        if unit:
            s = s.str.replace(unit, "", regex=False)
        return s.astype(float)

    df["Weight"] = clean("Weight", "kg")
    if "Body_Fat" in df.columns:
        df["Body_Fat"] = clean("Body_Fat", "%")
    else:
        df["Body_Fat"] = np.nan
    if "Body_age" in df.columns:
        df["Body_age"] = clean("Body_age")
    else:
        df["Body_age"] = np.nan

    # Parse datetime
    df["Date"] = pd.to_datetime(df["Date"], format="%H:%M %b.%d %Y", errors="coerce")
    df = df.dropna(subset=["Date"])

    # Daily averages (handle duplicates)
    df["Day"] = df["Date"].dt.date
    daily = df.groupby("Day")[["Weight", "Body_Fat", "Body_age"]].mean().reset_index()

    # ✅ FIX: convert to datetime before to_period
    daily["Month"] = pd.to_datetime(daily["Day"].astype(str)).dt.to_period("M")

    # Monthly averages
    monthly_avg = (
        daily.groupby("Month")[["Weight", "Body_Fat", "Body_age"]]
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

    # workouts (ODS)
    p_work = subparsers.add_parser("workouts", help="Aggregate walked/ran/cycled data from ODS.")
    p_work.add_argument("file", help="Input ODS file with workout data.")
    p_work.add_argument("--sheet", default="km", help="Sheet name to read (default: km).")
    p_work.add_argument("--range", default=None, help="Cell range like A4:D15 (optional).")

    # body (CSV/TSV)
    p_body = subparsers.add_parser("body", help="Aggregate body metric data from CSV/TSV.")
    p_body.add_argument("file", help="Input CSV/TSV with Date, Weight, Body Fat, Body age.")

    args = parser.parse_args()

    if args.command == "workouts":
        from your_module import aggregate_workouts_ods  # import your function
        result = aggregate_workouts_ods(args.file, sheet=args.sheet, cell_range=args.range)
        print(json.dumps(result, indent=2))
    elif args.command == "body":
        aggregate_body(args.file)

if __name__ == "__main__":
    main()
