#!/bin/bash
# Named to match NO generic tidy-up pattern -- not keepalive/heartbeat/status/
# coord/monitor/loop/pulse. PROTOCOL 6e: `pkill -f <word>` is a broadcast on a
# shared box, and the previous name (status_heartbeat_loop.sh) was matched by
# `pkill -f status`, `-f heartbeat` and `-f loop`. Three sessions' writers were
# being killed by each other's cleanup all day; ours survived on luck alone.
#
# The rename is defence in depth only. It protects against OTHER sessions'
# broad patterns; it does not replace the real rule, which is that WE kill by
# PID from the pidfile and never by name (see stop_heartbeat.sh).
# Tick the heartbeat every 60s. stale_after_s=300 gives peers a 5x margin, so a
# few missed ticks reads as "recent" and a real death reads as stale within
# minutes. Each tick RE-MEASURES (PROTOCOL 6b) -- this loop cannot bump a
# timestamp without recomputing the content, because it has no way to.
cd /Users/sumit/Github/quantum
# Publish OUR pid ($$ of this long-lived loop, not of a tick) so the status can
# carry a liveness token that a reader can ps. Removed on exit so a clean stop
# leaves no token behind claiming a heartbeat that is gone.
# Refuse to start if a verified heartbeat is already running. Duplicate loops
# have bitten twice across sessions (ansatz twice, here once) and the restart
# path after a power cut is exactly where it happens. Verified against ps, not
# just the pidfile's existence, so a stale file from an unclean death does not
# block a legitimate restart.
if [ -f .heartbeat.pid ]; then
  OLD=$(cat .heartbeat.pid 2>/dev/null)
  if [ -n "$OLD" ] && ps -p "$OLD" -o command= 2>/dev/null | grep -q vestigium_wr_9f2a4c.sh; then
    echo "heartbeat already running as $OLD; refusing to start a second" >&2
    exit 0
  fi
  rm -f .heartbeat.pid          # stale file from an unclean death
fi
echo $$ > .heartbeat.pid
# The handler MUST exit. A bare `trap 'rm -f ...' TERM` runs the handler and
# then RESUMES the loop -- which made this heartbeat survive SIGTERM while
# deleting its own pidfile, i.e. unkillable AND unable to advertise itself.
# Two orphaned loops were running before this was caught.
trap 'rm -f .heartbeat.pid; exit 0' INT TERM
trap 'rm -f .heartbeat.pid' EXIT
while true; do
  python3 status_heartbeat.py >/dev/null 2>>heartbeat.err || true
  # `sleep 60` as a FOREGROUND command makes bash defer the trap until it
  # returns, so SIGTERM sat queued for up to a minute and the loop looked
  # unkillable. Backgrounding it and `wait`-ing makes the wait interruptible,
  # so the handler runs immediately.
  sleep 60 &
  wait $!
done
