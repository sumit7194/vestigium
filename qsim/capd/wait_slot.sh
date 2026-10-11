#!/bin/zsh
# Run a command once fewer than 5 CPU-busy processes remain in MY job trees (thread budget).
# Roots: the Lean export batch (1509), the Plan A chain (35084), the TS replay queue (86555).
# Usage: wait_slot.sh cmd...
busy() {
  ps -A -o pid=,ppid=,%cpu= | python3 -c '
import sys
roots={1509,35084,86555}; rows=[l.split() for l in sys.stdin]
par={int(p):int(q) for p,q,c in rows}; cpu={int(p):float(c) for p,q,c in rows}
def mine(p):
    while p>1:
        if p in roots: return True
        p=par.get(p,1)
    return False
print(sum(1 for p in cpu if cpu[p]>50 and mine(p)))'
}
until [ $(busy) -lt 5 ]; do sleep 60; done
echo "slot free $(date): $*"; "$@"
