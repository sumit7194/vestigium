#!/bin/bash
# b15b_verify_kill.sh PID EXPECTED_ARGS LOG -- stop ONE process only if it is provably my MNFlow worker: owner sumit,
# command line EXACTLY "<python> -u b15b_mnflow_worker.py <EXPECTED_ARGS>" with <python> the venv's resolved interpreter,
# and cwd exactly the horseshoe directory. Logs the verification before the kill. Exit 0 if killed, 1 if refused.
P=$1; EXP=$2; LOG=$3; HS=/Users/sumit/Github/quantum/qsim/capd/horseshoe
cmd=$(ps -o command= -p $P 2>/dev/null); own=$(ps -o user= -p $P 2>/dev/null | tr -d ' '); cwd=$(lsof -a -p $P -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
if [[ "$own" == "sumit" && "$cwd" == "$HS" && "$cmd" =~ ^/opt/homebrew/Cellar/python@3\.13/[^\ ]+/Python\ -u\ b15b_mnflow_worker\.py\ $EXP$ ]]; then
  echo "$(date '+%F %T') VERIFIED PID $P owner=$own cwd=$cwd cmd=[$cmd] -> SIGTERM" >> $LOG; kill $P; exit 0
fi
echo "$(date '+%F %T') REFUSED to stop PID $P: owner=$own cwd=$cwd cmd=[$cmd] (expected args: $EXP)" >> $LOG; exit 1
