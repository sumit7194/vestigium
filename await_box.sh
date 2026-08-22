#!/bin/bash
# Wait for the box to genuinely free, then run the s=6 replication.
#
# The start condition is preflight.py itself -- the gate built today, which
# checks every peer's status through the shared reader (fresh, live token,
# not busy) and compares the requirement against BOTH free and available
# memory. Reusing it means the launch decision and the manual decision are the
# same decision, rather than two that can drift.
#
# Logs to a file, never /dev/null: the bridge lost an hour of evidence three
# times today by discarding stderr, and this run is 2-6 hours.
cd /Users/sumit/Github/quantum
NEED=8
LOG=s6_run.log
WAIT=await.log
: > "$WAIT"
echo "$(date '+%H:%M:%S') waiting for the box; need ${NEED} GB and all peers idle" >> "$WAIT"

while true; do
  if python3 preflight.py "$NEED" >> "$WAIT" 2>&1; then
    echo "$(date '+%H:%M:%S') CLEAR -- starting s=6" >> "$WAIT"
    # unbuffered so the per-l lines and heartbeat reach the log as they happen,
    # not when a 4 KB block fills -- the failure that made the bridge's tracker
    # look dead for 26 minutes.
    nohup python3 -u qsim/corner_s6.py > "$LOG" 2>&1 &
    echo "$(date '+%H:%M:%S') launched pid $!" >> "$WAIT"
    exit 0
  fi
  echo "$(date '+%H:%M:%S') held" >> "$WAIT"
  sleep 120
done
