#!/bin/bash

## Limit the scan's memory usage to 100MB
ulimit -m 102400

## Set scan type
SCAN_TYPE="$1"

# Set the directories to scan
WEEKLY_SCAN_PATHS=("/")
DAILY_SCAN_PATHS=("/home" "/var" "/bin" "/sbin" "/etc" "/opt")

CLAMAV_QUARANTINE_DIR="/opt/clamav/quarantine"
CLAMAV_LOG_DIR="/var/log/clamav"

# Set the backup directory path
LOG_BACKUP_DIR="$CLAMAV_LOG_DIR/backup"

# Set the log and report file paths
LOG_FILE="$CLAMAV_LOG_DIR/$(date +%Y-%m-%d)/clamscan.log"
REPORT_FILE="$CLAMAV_LOG_DIR/$(date +%Y-%m-%d)/clamscan.report"

# Create the log and report directories if they don't exist
mkdir -pv "$(dirname "$LOG_FILE")"
mkdir -pv "$(dirname "$REPORT_FILE")"
mkdir -pv "$CLAMAV_QUARANTINE_DIR"

function scan_path() {
    _path="$1"
    echo "Scanning $1"

    ## --recursive: Scan subdirectories
    ## --infected: Take action on infected files
    ## --move: Move infected files to a quarantine directory
    clamscan \
        --recursive \
        --infected \
        --move="$CLAMAV_QUARANTINE_DIR" \
        "$1" \
        | tee "$LOG_FILE" \
        | grep *"FOUND" >> "$REPORT_FILE"

    return $?
}

echo "Performing $SCAN_TYPE scan"

case "$SCAN_TYPE" in
    "weekly")
        for p in "${WEEKLY_SCAN_PATHS[@]}"; do
            scan_path $p
        done
    ;;
    "daily")
        for p in "${DAILY_SCAN_PATHS[@]}"; do
            scan_path $p
        done
    ;;
    "*")
        echo "Invalid scan type: $SCAN_TYPE"
        exit 1
    ;;
esac

exit $?
