#!/usr/bin/env python3
import argparse
import json
import os
from collections import defaultdict
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mär": "03", "Mar": "03",
    "Apr": "04", "Mai": "05", "Jun": "06", "Jul": "07",
    "Aug": "08", "Sep": "09", "Okt": "10", "Oct": "10",
    "Nov": "11", "Dez": "12", "Dec": "12"
}

def parse_month_label(label):
    parts = label.split()
    if len(parts) != 2:
        return label
    month_str, year_str = parts
    month_num = MONTH_MAP.get(month_str, "01")
    return f"{year_str}-{month_num}"

def get_text(cell):
    ps = cell.getElementsByType(P)
    if not ps:
        return ""
    return "".join([p.firstChild.data if p.firstChild else "" for p in ps])

def parse_range(r):
    start, end = r.split(":")
    colA = ord(start[0].upper()) - 65
    rowA = int(start[1:]) - 1
    colB = ord(end[0].upper()) - 65
    rowB = int(end[1:]) - 1
    return colA, rowA, colB, rowB

def extract_sheet(doc, sheet_name, cell_range):
    colA, rowA, colB, rowB = parse_range(cell_range)
    sheet = next((t for t in doc.spreadsheet.getElementsByType(Table) if t.getAttribute("name")==sheet_name), None)
    if not sheet:
        raise ValueError(f"Sheet {sheet_name} not found")
    rows = sheet.getElementsByType(TableRow)
    out = []
    for r_i in range(rowA, min(rowB+1, len(rows))):
        row = rows[r_i]
        cells = row.getElementsByType(TableCell)
        row_vals = []
        for c_i in range(colA, colB+1):
            if c_i < len(cells):
                row_vals.append(get_text(cells[c_i]))
            else:
                row_vals.append("")
        out.append(row_vals)
    return out

def build_stats(entries, output_path="/app/data/data.json"):
    totals = defaultdict(float)
    yearly = defaultdict(lambda: defaultdict(float))
    monthly = defaultdict(lambda: defaultdict(float))
    for row in entries:
        date = row["date"]
        year = date[:4]
        month = date[:7]
        for key in ("walked","ran","cycled"):
            val = float(row.get(key,0.0))
            totals[key] += val
            yearly[year][key] += val
            monthly[month][key] += val
    data = {
        "totals": dict(totals),
        "yearly": {y: dict(v) for y,v in yearly.items()},
        "monthly": {m: dict(v) for m,v in monthly.items()}
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path,"w") as f:
        json.dump(data,f,indent=2)
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--sheet", action="append", required=True)
    parser.add_argument("--range", dest="ranges", action="append", required=True)
    parser.add_argument("--out", default="data.json")
    args = parser.parse_args()

    if len(args.sheet) != len(args.ranges):
        raise SystemExit("Same number of --sheet and --range required.")

    doc = load(args.file)
    result = {}
    for s,r in zip(args.sheet,args.ranges):
        result[s] = extract_sheet(doc,s,r)

    entries = []
    for sheet_name, rows in result.items():
        for row in rows:
            if not row or not row[0]:
                continue
            entry = {
                "date": parse_month_label(row[0]),
                "walked": float(row[1].replace(",",".") if len(row)>1 and row[1] else 0),
                "ran": float(row[2].replace(",",".") if len(row)>2 and row[2] else 0),
                "cycled": float(row[3].replace(",",".") if len(row)>3 and row[3] else 0)
            }
            entries.append(entry)

    build_stats(entries, args.out)

if __name__=="__main__":
    main()
