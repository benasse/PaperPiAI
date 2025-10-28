
#!/bin/bash
# Script to generate a picture and display it
# Ensures only one instance runs at a time using flock

# 0 */6 * * * /root/PaperPiAI/scripts/generate_and_display.sh >> /tmp/generate_and_display.log 2>&1

LOCKFILE="/tmp/generate_and_display.lock"

(
    # Try to acquire a lock, exit if another instance is running
    flock -n 200 || { echo "Another instance is already running, exiting."; exit 1; }

    echo "Starting generation at $(date)"

    # Change to the project directory
    cd "/root/PaperPiAI" || exit 1

    # Generate the picture
    ./venv/bin/python src/generate_picture.py --width=480 --height=800 --prompts ./prompts/rss.json --steps 20 ./output/

    # Display the generated picture
    ./venv/bin/python src/display_picture.py output/output.png

    echo "Generation finished at $(date)"

    # Reboot
    reboot

) 200>"$LOCKFILE"
