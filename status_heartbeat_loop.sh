#!/bin/bash
# Tick the heartbeat every 60s. stale_after_s=300 gives peers a 5x margin, so a
# few missed ticks reads as "recent" and a real death reads as stale within
# minutes. Each tick RE-MEASURES (PROTOCOL 6b) -- this loop cannot bump a
# timestamp without recomputing the content, because it has no way to.
cd /Users/sumit/Github/quantum
while true; do
  python3 status_heartbeat.py >/dev/null 2>>heartbeat.err || true
  sleep 60
done
