#!/bin/sh
# POSIX-safe script to generate a picture, display it, log everything, and reboot if successful
# Recommended crontab:
# 0 6,11,16,21 * * * /root/PaperPiAI/scripts/generate_and_display.sh

PROJECT_DIR="/root/PaperPiAI"
LOCKFILE="/tmp/generate_and_display.lock"
LOGFILE="/tmp/generate_and_display.log"

# Ensure log file exists
touch "$LOGFILE" || { echo "Cannot create log file $LOGFILE"; exit 1; }

# Acquire lock and run everything in a sub-shell
flock -n "$LOCKFILE" sh -c '
DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo "$DATE - Starting generation" >> '"$LOGFILE"'

cd '"$PROJECT_DIR"' || { echo "$DATE - Cannot cd to '"$PROJECT_DIR"'" >> '"$LOGFILE"'; exit 1; }

# Generate the picture
if ./venv/bin/python src/generate_picture.py --width=480 --height=800 --prompts ./prompts/rss.json --steps 20 ./output/ >> '"$LOGFILE"' 2>&1; then
    DATE=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$DATE - Picture generated successfully" >> '"$LOGFILE"'

    # Display the picture
    if ./venv/bin/python src/display_picture.py output/output.png >> '"$LOGFILE"' 2>&1; then
        DATE=$(date "+%Y-%m-%d %H:%M:%S")
        echo "$DATE - Picture displayed successfully" >> '"$LOGFILE"'
        echo "$DATE - Rebooting now" >> '"$LOGFILE"'
        /sbin/reboot
    else
        DATE=$(date "+%Y-%m-%d %H:%M:%S")
        echo "$DATE - Error displaying the picture" >> '"$LOGFILE"'
        exit 1
    fi
else
    DATE=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$DATE - Error generating the picture" >> '"$LOGFILE"'
    exit 1
fi
'
