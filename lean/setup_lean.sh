#!/bin/zsh
# Lean 4 + Mathlib setup for the glue-lemma track, with a disk guard (stop if free < 4 GB, per user).
set -u
cd /Users/sumit/Github/quantum/lean
LOG=/Users/sumit/Github/quantum/lean/setup_lean.log
free_gb() { df -g / | tail -1 | awk '{print $4}'; }
echo "start $(date)  free=$(free_gb) GB" > $LOG
(
  set -e
  if [ ! -d ZiglinCert ]; then
    lake +leanprover-community/mathlib4:lean-toolchain new ZiglinCert math >> $LOG 2>&1
  fi
  cd ZiglinCert
  echo "project created $(date) free=$(df -g / | tail -1 | awk '{print $4}') GB" >> $LOG
  lake exe cache get >> $LOG 2>&1
  echo "cache fetched $(date) free=$(df -g / | tail -1 | awk '{print $4}') GB" >> $LOG
  lake build >> $LOG 2>&1
  echo "BUILD_DONE $(date)" >> $LOG
) &
WORK=$!
while kill -0 $WORK 2>/dev/null; do
  F=$(free_gb)
  if [ "$F" -lt 4 ]; then
    echo "DISK GUARD: free=$F GB < 4 GB -- killing setup (pid $WORK and children) $(date)" >> $LOG
    pkill -P $WORK; kill $WORK
    exit 2
  fi
  sleep 5
done
wait $WORK; RC=$?
echo "END rc=$RC $(date) free=$(free_gb) GB" >> $LOG
