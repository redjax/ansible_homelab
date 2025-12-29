#!/bin/bash
SCAN_SCRIPT="/opt/clamav/scans/clam_scan.sh"

if [ ! -f "$SCAN_SCRIPT" ]; then
  echo "[ERROR] Could not find scan script at path: $SCAN_SCRIPT"
  exit 1
fi

echo "Running daily scan."
"$SCAN_SCRIPT" daily
