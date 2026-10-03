#!/bin/zsh
# Overnight chain (bridge-approved sequencing): wait for the frozen MN equatorial v2 runner (pid passed as $1),
# then A6 re-runs of every row whose search aborted on a transport failure, then the TS v2 stage. Strictly sequential.
Q=/Users/sumit/Github/quantum/qsim; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
cd $Q
while kill -0 $1 2>/dev/null; do sleep 30; done
echo "frozen MN runner done $(date)" >> $Q/overnight_chain.log
ROWS=$($PY -c "
import json; d=json.load(open('$Q/mr_v2_mneq.json'))
print(','.join(str(i) for i, r in enumerate(d) if 'transport failed' in str(r.get('why', '')) or 'guard' in r.get('assessment','')))")
echo "A6 re-run rows: [$ROWS] $(date)" >> $Q/overnight_chain.log
if [ -n "$ROWS" ]; then
  $PY -u $Q/mr_v2_mneq.py --a6 $ROWS > $Q/mr_v2_mneq_a6.txt 2>&1; echo "EXIT $?" >> $Q/mr_v2_mneq_a6.txt
fi
echo "A6 re-runs done $(date)" >> $Q/overnight_chain.log
$PY -u $Q/mr_v2_ts2.py RUN > $Q/mr_v2_ts2.txt 2>&1; echo "EXIT $?" >> $Q/mr_v2_ts2.txt
echo "TS stage done $(date)" >> $Q/overnight_chain.log
cd /Users/sumit/Github/quantum && git add qsim/overnight_chain.log qsim/mr_v2_mneq_a6.txt qsim/mr_v2_ts2.txt 2>/dev/null; git commit -q -m "overnight chain: logs

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin main
