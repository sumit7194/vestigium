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
if ps -p "$PID" -o command= 2>/dev/null | grep -q status_heartbeat_loop.sh; then
  kill "$PID" && echo "stopped our heartbeat ($PID)"
else
  echo "pidfile names $PID which is not our heartbeat; refusing to signal it"
  rm -f .heartbeat.pid
fi
