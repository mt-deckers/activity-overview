#!/usr/bin/env python3
import argparse
import json
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

def get_text(cell):
    ps = cell.getElementsByType(P)
    if not ps:
        return ""
    parts = []
    for p in ps:
        if p.firstChild:
            parts.append(p.firstChild.data)
    return "".join(parts)

def parse_range(r):
    # "A1:D20" → ("A","1") ("D","20")
    start, end = r.split(":")
    colA = ord(start[0].upper()) - 65
    rowA = int(start[1:]) - 1
    colB = ord(end[0].upper()) - 65
    rowB = int(end[1:]) - 1
    return colA, rowA, colB, rowB

def extract_sheet(doc, sheet_name, cell_range):
    colA, rowA, colB, rowB = parse_range(cell_range)

    sheet = None
    for tab in doc.spreadsheet.getElementsByType(Table):
        if tab.getAttribute("name") == sheet_name:
            sheet = tab
            break
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
    for s, r in zip(args.sheet, args.ranges):
        result[s] = extract_sheet(doc, s, r)

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
