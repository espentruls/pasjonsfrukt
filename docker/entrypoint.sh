#!/bin/bash

# Default to root if PUID/PGID not set
PUID=${PUID:-0}
PGID=${PGID:-0}

# Create user/group if not root
if [ "$PUID" -ne 0 ]; then
    groupadd -g "$PGID" appgroup
    useradd -u "$PUID" -g "$PGID" -m appuser

    # Adjust permissions
    chown -R appuser:appgroup /app/yield
    chown appuser:appgroup /var/log/pasjonsfrukt.log

    echo "Running as user appuser (UID: $PUID, GID: $PGID)"
else
    echo "Running as root"
fi

# Start logging in background
tail -f /var/log/pasjonsfrukt.log &

echo "Installing crontab..."
# Remove existing crontabs
crontab -r >/dev/null 2>&1

if [ "$PUID" -ne 0 ]; then
    # Install crontab for appuser
    crontab -u appuser /etc/cron.d/pasjonsfrukt-crontab
else
    # Install crontab for root
    crontab /etc/cron.d/pasjonsfrukt-crontab
fi
cat /etc/cron.d/pasjonsfrukt-crontab

echo "Starting cron service..."
cron

echo "Starting server..."
if [ "$PUID" -ne 0 ]; then
    exec gosu appuser pasjonsfrukt serve "$@"
else
    exec pasjonsfrukt serve "$@"
fi
