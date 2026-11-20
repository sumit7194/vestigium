#!/bin/bash
# b15_launch.sh -- the counted B15 run with the compiled map (Sumit's OK, 2026-11-20; B15_LAUNCH_PLAN.md as reviewed by the
# Bridge): b15_kerr_ck.py with B15_MAP=rust, then the G6 driver b15b_g6_run.py on its records. Run detached at nice 10
# (tools/detach.sh); guarded by b15_run_guard.py on THIS script's PID. Log: horseshoe_results/kerr/b15_rust_launch.log.
HS=/Users/sumit/Github/quantum/qsim/capd/horseshoe; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
L=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15_rust_launch.log; cd $HS
log(){ echo "$(date '+%F %T') $*" >> $L; }
log "start: pid $$, pgid $(ps -o pgid= -p $$ | tr -d ' '), lib sha256 $(shasum -a 256 kerr_rs/target/release/libkerr_rs.dylib | cut -c1-16)"
B15_MAP=rust $PY -u b15_kerr_ck.py; rc=$?; log "b15_kerr_ck.py exit $rc"
if [ $rc -eq 0 ]; then $PY -u b15b_g6_run.py; rc2=$?; log "b15b_g6_run.py exit $rc2"; else log "G6 NOT run (the run did not exit 0)"; fi
log "DONE"
