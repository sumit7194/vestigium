#!/bin/bash
# b15c_launch.sh -- B15c constructor stage (registered B15c a126a6b + B15c-1 7ca093d), in the registered order:
# T1, then the diagnostic arm ONLY if T1 stopped at refinement, then T2 (sealed run list with the planted rejects), then T3.
# The driver refuses to run without controls_PASS.json for its own sha256. Run detached at nice 10 (tools/detach.sh);
# guarded by b15_run_guard.py on THIS script's PID (cap 1024 MB, suffix b15c_launch.sh). Log: kerr/b15c/launch.log.
HS=/Users/sumit/Github/quantum/qsim/capd/horseshoe; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
O=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15c; L=$O/launch.log; cd $HS
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
log(){ echo "$(date '+%F %T') $*" >> $L; }
log "start: pid $$, pgid $(ps -o pgid= -p $$ | tr -d ' '), driver sha256 $(shasum -a 256 b15_steps34.py | cut -c1-16)"
$PY -u b15_steps34.py constructor T1; rc=$?; log "T1 exit $rc"; [ $rc -eq 0 ] || { log "STOPPED after T1 (exit $rc)"; exit 1; }
if $PY -c "import json,sys; sys.exit(0 if json.load(open('$O/T1.json'))['records'][0].get('stop')=='step 3: refinement failed' else 1)"; then
  $PY -u b15_steps34.py constructor ARM; rc=$?; log "ARM exit $rc"; [ $rc -eq 0 ] || { log "STOPPED after ARM"; exit 1; }
else log "ARM not run (T1 did not stop at refinement)"; fi
for t in T2 T3; do $PY -u b15_steps34.py constructor $t; rc=$?; log "$t exit $rc"; [ $rc -eq 0 ] || { log "STOPPED after $t"; exit 1; }; done
log "DONE"
