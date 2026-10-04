#!/bin/zsh
# Resume after the 2026-10-04 reboot (user: "resume the run"). Strictly sequential, ≤3 threads; runs beside the
# A7 row-1 re-replay (2 procs), so the total stays ≤5.
#   1. row 4: v1 replay of the SAVED v2 certificate (N=100; N=140 per A7 term 4 if tail-limited)
#   2. row 5: A6 re-run (search + replay), as registered
#   3. TS v2 stage, as registered
Q=/Users/sumit/Github/quantum/qsim; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
cd $Q
echo "resume chain start $(date)" >> $Q/overnight_chain.log
$PY -u $Q/mr_v2_a7.py FINISH 4 >> $Q/mr_v2_mneq_a6.txt 2>&1; echo "EXIT $? (row 4 finish)" >> $Q/mr_v2_mneq_a6.txt
$PY -u $Q/mr_v2_mneq.py --a6 5 >> $Q/mr_v2_mneq_a6.txt 2>&1; echo "EXIT $? (row 5)" >> $Q/mr_v2_mneq_a6.txt
echo "A6 rows done $(date)" >> $Q/overnight_chain.log
$PY -u $Q/mr_v2_ts2.py RUN > $Q/mr_v2_ts2.txt 2>&1; echo "EXIT $?" >> $Q/mr_v2_ts2.txt
echo "TS stage done $(date)" >> $Q/overnight_chain.log
cd /Users/sumit/Github/quantum && git add qsim/overnight_chain.log qsim/mr_v2_mneq_a6.txt qsim/mr_v2_ts2.txt 2>/dev/null; git commit -q -m "resume chain: logs

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin main
