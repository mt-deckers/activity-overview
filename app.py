#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
import pandas as pd

def aggregate_workouts_ods(ods_file, sheet="km", cell_range=None):
    """
    Aggregate walked/ran/cycled directly from an ODS file/sheet and optional range.
    """
    # Read the sheet
    df = pd.read_excel(ods_file, sheet_name=sheet, engine="odf", header=None)

    # Optionally slice a range (A1:D10 style)
    if cell_range:
        # Convert Excel-style range to integer indices
        import re
        col_map = {chr(i+65): i for i in range(26)}
        m = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", cell_range)
        if m:
            c1, r1, c2, r2 = m.groups()
            df = df.iloc[int(r1)-1:int(r2), col_map[c1]:col_map[c2]+1]

    # Expect columns: Date, Walked, Ran, Cycled
    df.columns = ["Date", "Walked", "Ran", "Cycled"]

    totals = {"walked": 0, "ran": 0, "cycled": 0}
    yearly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})
    monthly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})

    for _, row in df.iterrows():
        try:
            dt = pd.to_datetime(row["Date"])
        except Exception:
            continue
        def parse(x): return float(str(x).replace(",", ".") or 0)
        walked, ran, cycled = parse(row["Walked"]), parse(row["Ran"]), parse(row["Cycled"])

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

    return output  # in-memory, no file saved


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
        result = aggregate_workouts_ods(args.file, sheet=args.sheet, cell_range=args.range)
        print(json.dumps(result, indent=2))
    elif args.command == "body":
        aggregate_body(args.file)

if __name__ == "__main__":
    main()
