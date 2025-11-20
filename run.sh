#!/bin/bash
cd "$(dirname "$0")" && echo "📁 Changed dir to $(pwd)" || {
	echo "❌ ERROR: Could not change dir or no dir provided"
	exit 1
}

function create_and_append_dump() {
	cd /opt/bin/sub_projects/ods_export
	pwd
	cp /opt/bin/data/workout/reps.ods /opt/bin/sub_projects/ods_export/app
	./run.sh app/reps.ods --sheet=km --range=$1 --no-header --output="data_dump.csv"
	cat data_dump.csv >>data.csv
	sudo rm data_dump.csv
}

echo -n "" >data.csv
create_and_append_dump "A4:D15"
create_and_append_dump "A17:D28"

echo "parsing and precompiling data"

python3 - <<END
import csv
from collections import defaultdict
from datetime import datetime
import json

# Read CSV
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    rows = list(reader)

# Prepare accumulators
totals = {"walked": 0, "ran": 0, "cycled": 0}
yearly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})
monthly = defaultdict(lambda: {"walked": 0, "ran": 0, "cycled": 0})

for r in rows:
    # Parse date
    try:
        dt = datetime.strptime(r[0], "%Y-%m-%d")  # adjust format if needed
    except:
        continue  # skip bad rows

    # Parse floats
    walked = float(r[1].replace(",", ".") or 0)
    ran    = float(r[2].replace(",", ".") or 0)
    cycled = float(r[3].replace(",", ".") or 0)

    # Totals
    totals["walked"] += walked
    totals["ran"] += ran
    totals["cycled"] += cycled

    # Yearly aggregation
    y = dt.year
    yearly[y]["walked"] += walked
    yearly[y]["ran"] += ran
    yearly[y]["cycled"] += cycled

    # Monthly aggregation
    ym = dt.strftime("%Y-%m")
    monthly[ym]["walked"] += walked
    monthly[ym]["ran"] += ran
    monthly[ym]["cycled"] += cycled

# Output JSON
output = {
    "totals": totals,
    "yearly": dict(yearly),
    "monthly": dict(monthly),
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)
END

echo "now cp the data back (wtf is this???)"
cp ./data.json /opt/bin/sub_projects/activity_overview/

echo "starting local server"
python3 -m http.server 54587
