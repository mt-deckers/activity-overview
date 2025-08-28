#!/bin/bash
cd "$(dirname "$0")" && echo "📁 Changed dir to $(pwd)" || { echo "❌ ERROR: Could not change dir or no dir provided"; exit 1; }

ods_export /opt/bin/data/workout/reps.ods --sheet=km --range=A17:D28 --no-header --output="data.csv"
