#!/bin/bash

docker build -t workout-extractor .

docker run --rm \
  -v /opt/bin/data_archive/data/workout/reps.ods:/input/reps.ods \
  -v $(pwd)/output:/output \
  workout-extractor \
  --sheet 2023 --range A1:D1 \
  --sheet 2024 --range A1:D12 \
  --sheet 2025 --range A1:D12 \
  --sheet 2026 --range A1:D12 \
  --file /input/reps.ods \
  --out /output/data.json

if [ $? -eq 0 ]; then
cat << EOF
SUCCESS!!!!
start local server via:
python3 -m http.server 54587

Watch the project here:
https://github.com/mt-deckers/activity-overview

Check the deployments here:
https://github.com/mt-deckers/activity-overview/deployments

See the latest deployment here:
https://mt-deckers.github.io/activity-overview/
EOF

fi
