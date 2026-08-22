#!/bin/bash
# Stop OUR heartbeat by PID from our own pidfile -- never `pkill -f <word>`.
# PROTOCOL 6e: a process-name pattern is not a private namespace on a shared
# machine. `pkill -f keepalive` matches six processes across four sessions, and
# is the most likely cause of the bridge's writer dying four times in one day.
# Identity is verified before signalling: a recycled PID is as dangerous to kill
# as it is to trust.
cd "$(dirname "$0")"
[ -f .heartbeat.pid ] || { echo "no pidfile; nothing of ours to stop"; exit 0; }
PID=$(cat .heartbeat.pid)
if ps -p "$PID" -o command= 2>/dev/null | grep -q vestigium_wr_9f2a4c.sh; then
  # MUST NOT be `kill && echo` alone: a check that is silent on failure is
  # indistinguishable from one that is silent on success. That exact shape cost
  # the bridge a phantom announcement -- `ls file && echo written` printed
  # nothing when ls failed and they read the absence of an error as success.
  if kill "$PID"; then
    echo "stopped our heartbeat ($PID)"
  else
    echo "FAILED to signal $PID -- heartbeat may still be running" >&2
    exit 1
  fi
else
  echo "pidfile names $PID which is not our heartbeat; refusing to signal it"
  rm -f .heartbeat.pid
fi
