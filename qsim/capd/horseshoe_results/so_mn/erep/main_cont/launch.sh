#!/bin/zsh
# main_cont launch (E_REP_PREREG.md Amendment A3). Run ONLY after A3 is REGISTERED and the Melnikov counted run has ended.
set -e
Q=/Users/sumit/Github/quantum; T=$Q/qsim/capd/horseshoe/tests; D=$Q/qsim/capd/horseshoe_results/so_mn/erep/main_cont
R=$Q/qsim/capd/horseshoe_results/so_mn/erep/main_redo; PY=$Q/sims/.venv/bin/python
[[ -e $D/st ]] && { echo "main_cont/st already exists: refusing (no relaunch without the Bridge)"; exit 1; }
[[ $(shasum -a 256 $T/mn_so_erep | cut -c1-64) == 4a48b59ae87427ed9629fd6d6f313004a8293bcbf4fd64b5a13f4245ce7c112b ]] || { echo "binary hash mismatch"; exit 1; }
cp -p $R/st $D/st; cmp $R/st $D/st
echo "start state: main_redo/st sha256 $(shasum -a 256 $R/st | cut -c1-64) copied" > $D/launch.txt
cd $T
export SO_EREP=zsym SO_FIXED_REDO=1 SAVE_FROM=292 SAVE_DT=20
PID=$($Q/tools/detach.sh $D/run.out $T nice -n 10 ./mn_so_erep 1/10000000 $Q/qsim/capd/horseshoe_results/mn_smoke/b17_cp_1e-7.txt $D/st 1018.7)
sleep 3
GPID=$($Q/tools/detach.sh $D/guard.out $T nice -n 10 $PY $Q/qsim/capd/horseshoe/erep_guard.py $PID $D/guard.log 500)
CPID=$($Q/tools/detach.sh $D/cost_watch.out $T nice -n 10 $PY $Q/qsim/capd/horseshoe/erep_cost_watch.py $PID $D/run.out $D/cost_watch.log)
{ echo "registered main_cont run (E_REP_PREREG.md Amendment A3); started $(date '+%Y-%m-%d %H:%M'), PID $PID (nice 10 via detach.sh), cwd $T"
  echo "binary mn_so_erep sha256 4a48b59ae87427ed9629fd6d6f313004a8293bcbf4fd64b5a13f4245ce7c112b; env SO_EREP=zsym SO_FIXED_REDO=1 SAVE_FROM=292 SAVE_DT=20 (CKPT_SEC default)"
  echo "cmd: ./mn_so_erep 1/10000000 .../mn_smoke/b17_cp_1e-7.txt $D/st 1018.7"
  echo "guard PID $GPID (erep_guard.py, cap 500 MB); cost watch PID $CPID (erep_cost_watch.py, COST-STOP > 127.9 s/step over 200 steps)"
  echo "reading: read_result.sh (A3 criteria)"; } >> $D/launch.txt
cat $D/launch.txt; ps -o pid,ppid,pgid,sess,nice,command -p $PID,$GPID,$CPID
