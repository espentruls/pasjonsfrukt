#!/bin/bash

# Default to root if PUID/PGID not set
PUID=${PUID:-0}
PGID=${PGID:-0}
# Default server to true (RSS hosting enabled)
ENABLE_SERVER=${ENABLE_SERVER:-true}

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
    # Ensure config dir is writable if mounted
    if [ -d "/config" ]; then
        chown -R "$PUID":"$PGID" /config
    fi

    echo "Running as user appuser (UID: $PUID, GID: $PGID)"
else
    echo "Running as root"
fi

# Determine config file arguments
CONFIG_ARGS=""
CONFIG_FILE="/config/config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    echo "Found config file at $CONFIG_FILE"
    CONFIG_ARGS="--config-file $CONFIG_FILE"
elif [ -f "/app/config.yaml" ]; then
    echo "Found config file at /app/config.yaml"
    CONFIG_ARGS="--config-file /app/config.yaml"
else
    echo "No config file found. Using Environment Variables."
fi

# Crontab setup
CRON_FILE="/etc/cron.d/pasjonsfrukt-crontab"
if [ -f "$CRON_FILE" ]; then
    echo "Using provided crontab at $CRON_FILE"
else
    echo "Using default crontab"
    CRON_FILE="/app/crontab.default"
fi

# Update default crontab with correct config args if needed
if [ "$CRON_FILE" = "/app/crontab.default" ]; then
    # We replace the command in the default crontab
    # Default is: ... pasjonsfrukt harvest --config-file /config/config.yaml ...
    # We need to replace it with actual args or remove it if empty.

    if [ -z "$CONFIG_ARGS" ]; then
        sed -i "s| --config-file /config/config.yaml||g" "$CRON_FILE"
    else
        sed -i "s| --config-file /config/config.yaml| $CONFIG_ARGS|g" "$CRON_FILE"
    fi
fi

echo "Installing crontab from $CRON_FILE..."
# Remove existing crontabs
crontab -r >/dev/null 2>&1

if [ "$PUID" -ne 0 ]; then
    # Install crontab for appuser
    crontab -u appuser "$CRON_FILE"
else
    # Install crontab for root
    crontab "$CRON_FILE"
fi
cat "$CRON_FILE"

echo "Starting cron service..."
cron

# Log tailing
LOG_FILE="/var/log/pasjonsfrukt.log"
# If we are using /config/pasjonsfrukt.log (from default crontab), we should tail that too?
if [ -f "/config/pasjonsfrukt.log" ]; then
    LOG_FILE="/config/pasjonsfrukt.log"
fi

# Create log file if not exists to allow tailing
touch "$LOG_FILE"
if [ "$PUID" -ne 0 ]; then
    chown "$PUID":"$PGID" "$LOG_FILE"
fi

if [ "$ENABLE_SERVER" = "true" ]; then
    echo "Starting server..."
    # Background tail
    tail -f "$LOG_FILE" &

    if [ "$PUID" -ne 0 ]; then
        exec gosu "$PUID":"$PGID" pasjonsfrukt serve $CONFIG_ARGS "$@"
    else
        exec pasjonsfrukt serve $CONFIG_ARGS "$@"
    fi
else
    echo "Server disabled. Keeping container alive and logging..."
    # Exec tail to keep container alive
    exec tail -f "$LOG_FILE"
fi
