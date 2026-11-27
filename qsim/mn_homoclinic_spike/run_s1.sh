#!/bin/zsh
# S1 serial runner: G-norm, the beta = 0 control, then the 6 registered beta values, then the reading. One core, nice 10.
cd ${0:A:h}; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
echo "start $(date '+%F %T')"
$PY s1.py gnorm
for b in 0 1e-4 3e-4 1e-3 3e-3 1e-2 3e-2; do echo "== beta $b $(date '+%T')"; $PY s1.py beta $b; done
echo "== READ $(date '+%T')"; $PY s1.py read
echo "end $(date '+%F %T')"
