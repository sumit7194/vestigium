#!/bin/bash
# status.sh -- one-screen progress of quantum's running jobs (read-only). Usage: ./status.sh
R=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results; G=$R/kerr/b15b_gates
echo "== $(date '+%F %T')  macOS $(sw_vers -productVersion)  load $(sysctl -n vm.loadavg | tr -d '{}')"
echo "== SO runs (MN second-order sets; swing-1 checkpoints ~t 290 / 800, full return t 1018.2)"
for w in 7 6; do
  st=$(grep '^# step' $R/so_mn/run_1e-$w.out | tail -1 | awk '{print $3, $4, $6, $7}')
  cp=$(grep -c '^CHECKPOINT' $R/so_mn/run_1e-$w.out); th=$(grep -c THREW $R/so_mn/run_1e-$w.out)
  den=$( [ $w = 7 ] && echo 10000000 || echo 1000000 ); pid=$(pgrep -f "^./mn_so 1/$den " | head -1)
  printf "   1e-%s: %s | checkpoints %s | THREW %s | %s\n" $w "$st" $cp $th "$( [ -n "$pid" ] && echo "running PID $pid" || echo NOT RUNNING)"
done
echo "== B15b MNFlow reference tasks"
/Users/sumit/Github/quantum/sims/.venv/bin/python - <<PY
import json, glob, collections
t = json.load(open("$G/tasks.json")); g = {r["id"]: r["grinds"] for r in json.load(open("$G/grind_prediction.json"))}
done = {}
for p in glob.glob("$G/mnflow_*.jsonl"):
    for l in open(p):
        try: r = json.loads(l); done[r["id"]] = r
        except Exception: pass
for gate in ("G1", "G4", "G4c", "G3"):
    ts = [x for x in t if x["gate"] == gate]; d = [x for x in ts if x["id"] in done]
    print("   %-4s %3d / %3d done  (grinders %d / %d)" % (gate, len(d), len(ts), sum(g[x["id"]] for x in d), sum(g[x["id"]] for x in ts)))
print("   total %d / %d" % (len(done), len(t)))
PY
echo "== workers (memory FOOTPRINT, compressed pages included; RSS understates it)"; for p in $(pgrep -f "[Pp]ython -u b15b_mnflow_worker"); do printf "   PID %s  %s  %6s MB  up %s\n" $p "$(ps -o command= -p $p | grep -o 'worker.py.*')" "$(footprint -p $p 2>/dev/null | sed -n 's/.*Footprint: \([0-9]*\) MB.*/\1/p' | head -1)" "$(ps -o etime= -p $p | tr -d ' ')"; done
echo "== system: $(memory_pressure | tail -1 | sed 's/System-wide //'); swap $(sysctl -n vm.swapusage | awk '{print $6}') used"
echo "== scheduler"; tail -3 $G/sched.log 2>/dev/null | sed 's/^/   /'
