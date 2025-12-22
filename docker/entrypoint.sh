#!/bin/bash

# Default to root if PUID/PGID not set
PUID=${PUID:-0}
PGID=${PGID:-0}
# Default server to false per user preference (just downloader)
ENABLE_SERVER=${ENABLE_SERVER:-false}

# Create user/group if not root
if [ "$PUID" -ne 0 ]; then
    # Check if group exists
    if ! getent group "$PGID" > /dev/null 2>&1; then
        groupadd -g "$PGID" appgroup
    else
        echo "Group with GID $PGID already exists"
        groupmod -n appgroup $(getent group "$PGID" | cut -d: -f1)
    fi

    # Check if user exists
    if ! id -u "$PUID" > /dev/null 2>&1; then
        useradd -u "$PUID" -g "$PGID" -m appuser
    else
        echo "User with UID $PUID already exists"
        usermod -l appuser -d /home/appuser -m $(getent passwd "$PUID" | cut -d: -f1)
    fi

    # Adjust permissions
    chown -R "$PUID":"$PGID" /app/yield
    chown "$PUID":"$PGID" /var/log/pasjonsfrukt.log

    echo "Running as user appuser (UID: $PUID, GID: $PGID)"
else
    echo "Running as root"
fi

# Start logging in background (for cron)
# We might exec tail later if server is disabled, but we need it running for cron logs if server IS enabled.
# If server is enabled, we use exec server, so this tail needs to be background.
# If server is disabled, we exec tail.
# So let's start it here only if server is enabled? No, tail -f follows file.
# If we exec tail -f, we don't need background tail.

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

if [ "$ENABLE_SERVER" = "true" ]; then
    echo "Starting server..."
    # Background tail for cron logs since we will exec server
    tail -f /var/log/pasjonsfrukt.log &

    if [ "$PUID" -ne 0 ]; then
        exec gosu "$PUID":"$PGID" pasjonsfrukt serve "$@"
    else
        exec pasjonsfrukt serve "$@"
    fi
else
    echo "Server disabled. Keeping container alive and logging..."
    # Exec tail to keep container alive
    exec tail -f /var/log/pasjonsfrukt.log
fi
