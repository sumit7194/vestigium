#!/bin/bash
# Tick the heartbeat every 60s. stale_after_s=300 gives peers a 5x margin, so a
# few missed ticks reads as "recent" and a real death reads as stale within
# minutes. Each tick RE-MEASURES (PROTOCOL 6b) -- this loop cannot bump a
# timestamp without recomputing the content, because it has no way to.
cd /Users/sumit/Github/quantum
# Publish OUR pid ($$ of this long-lived loop, not of a tick) so the status can
# carry a liveness token that a reader can ps. Removed on exit so a clean stop
# leaves no token behind claiming a heartbeat that is gone.
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
