#!/bin/bash

echo "workout data"
./app.py workouts /opt/bin/data/workout/reps.ods

echo "body data"
# what in the wincrap?
WINDOWS_USER=$(cd /mnt/c && cmd.exe /c "echo %USERNAME%" | tr -d '\r')
SOURCE_FILE="$(ls /mnt/c/Users/$WINDOWS_USER/Downloads/Fitdays*)"
echo "Reading: $SOURCE_FILE"
./app.py body "$SOURCE_FILE"

#echo "starting local server"
#python -m http.server 54587
