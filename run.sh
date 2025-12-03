#!/bin/bash

#docker build -t workout-extractor .

docker run --rm \
  -v /opt/bin/data/workout/reps.ods:/input/reps.ods \
  -v $(pwd)/output:/output \
  workout-extractor \
  --file /input/reps.ods \
  --out /output/data.json \
  --sheet 2025 --range A1:D12 \
  --sheet 2024 --range A1:D12 \
  --sheet 2023 --range A1:D1
