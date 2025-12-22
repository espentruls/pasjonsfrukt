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
    # Ensure config dir is writable if mounted
    if [ -d "/config" ]; then
        chown -R "$PUID":"$PGID" /config
    fi

    echo "Running as user appuser (UID: $PUID, GID: $PGID)"
else
    echo "Running as root"
fi

# Config file setup
CONFIG_FILE="/config/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found at $CONFIG_FILE. Checking /app/config.yaml..."
    if [ -f "/app/config.yaml" ]; then
        CONFIG_FILE="/app/config.yaml"
    else
        echo "No config file found. Using defaults/env vars."
        # Create a dummy config if /config is writable, so harvest command doesn't fail
        # Actually pasjonsfrukt requires config file?
        # cli.py defaults to "config.yaml".
        # If we rely on Env Vars, we might still need a dummy yaml to satisfy the loader if it checks file existence.
        # But config.py logic: config_from_stream reads stream.
        # If file missing, typer might complain?
        # Let's assume user provides Env Vars which override empty config.
        # But we need a file to point to.
        if [ -w "/config" ]; then
             echo "Creating dummy config at /config/config.yaml"
             touch /config/config.yaml
             CONFIG_FILE="/config/config.yaml"
             # If PUID set, ensure ownership
             if [ "$PUID" -ne 0 ]; then
                 chown "$PUID":"$PGID" /config/config.yaml
             fi
        fi
    fi
fi

# Crontab setup
CRON_FILE="/etc/cron.d/pasjonsfrukt-crontab"
if [ -f "$CRON_FILE" ]; then
    echo "Using provided crontab at $CRON_FILE"
else
    echo "Using default crontab"
    CRON_FILE="/app/crontab.default"
fi

# Modify default crontab to point to correct config file if using default
if [ "$CRON_FILE" = "/app/crontab.default" ]; then
    # We edit it in place (it's a copy in container)
    sed -i "s|/config/config.yaml|$CONFIG_FILE|g" "$CRON_FILE"
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
# But tail -f can only handle files that exist.
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
        exec gosu "$PUID":"$PGID" pasjonsfrukt serve --config-file "$CONFIG_FILE" "$@"
    else
        exec pasjonsfrukt serve --config-file "$CONFIG_FILE" "$@"
    fi
else
    echo "Server disabled. Keeping container alive and logging..."
    # Exec tail to keep container alive
    exec tail -f "$LOG_FILE"
fi
