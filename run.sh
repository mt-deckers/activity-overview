#!/bin/bash
cd "$(dirname "$0")" && echo "📁 Changed dir to $(pwd)" || {
	echo "❌ ERROR: Could not change dir or no dir provided"
	exit 1
}


echo "parsing and precompiling data"
./app.py workout fitdays.csv

echo "body data"
./app.py body fitdays.csv

#echo "starting local server"
#python -m http.server 54587
