FROM python:3.12-slim

# Install system deps required by odfpy (zip/unzip)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir odfpy

# Copy your extractor script
WORKDIR /app
COPY extract_workouts.py /app/extract_workouts.py

# Default entrypoint
ENTRYPOINT ["python3", "/app/extract_workouts.py"]
