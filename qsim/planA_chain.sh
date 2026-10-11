#!/bin/zsh
# Detached chain: wait for plan-A V2+V3 to finish, then launch V1 (restart-safe; nohup, ppid 1).
Q=/Users/sumit/Github/quantum/qsim; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
cd $Q
until grep -q "V23 DONE\|Traceback" chl_planA_V23.txt; do sleep 60; done
$PY -u chl_planA_V1.py 2 >> chl_planA_V1.txt 2>&1
