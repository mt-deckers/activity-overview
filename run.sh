#!/bin/bash

docker build -t workout-extractor .

docker run --rm -v "$PWD":/data workout-extractor \
    --file /data/reps.ods \
    --sheet 2025 --range A1:D12 \
    --sheet 2024 --range A1:D12 \
    --sheet 2023 --range A1:D1 \
    --out /data/data.json

