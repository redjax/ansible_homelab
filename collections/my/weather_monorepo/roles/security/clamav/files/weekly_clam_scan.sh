#!/bin/bash
SCAN_SCRIPT="/opt/clamav/scans/clam_scan.sh"

if [ ! -f "$SCAN_SCRIPT" ]; then
  echo "[ERROR] Could not find scan script at path: $SCAN_SCRIPT"
  exit 1
fi

echo "Running weekly scan."
"$SCAN_SCRIPT" weekly
