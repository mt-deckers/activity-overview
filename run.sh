#!/bin/bash
cd "$(dirname "$0")" && echo "📁 Changed dir to $(pwd)" || { echo "❌ ERROR: Could not change dir or no dir provided"; exit 1; }

function create_and_append_dump() {
	ods_export /opt/bin/data/workout/reps.ods --sheet=km --range=$1 --no-header --output="data_dump.csv"
	cat data_dump.csv >> data.csv
	rm data_dump.csv
}

echo -n "" > data.csv
create_and_append_dump "A4:D15"
create_and_append_dump "A17:D28"

echo "starting local server"
python -m http.server 54587
