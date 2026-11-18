#!/bin/bash
# lean_build_all_seq.sh -- the combined `lake build` of Certs/All.lean (the Bridge, 2026-11-18: after ansatz's T-SWITCH'
# ends, ~23:45; measure the peak; stop if swap > 2 GB SUSTAINED 600 s). Modules not yet built are built ONE AT A TIME
# (single Lean checks peaked at ~2.8 GB), then All. A watcher samples every 30 s the footprint of all lean/lake processes
# under this script and the swap; it stops the build by signalling this script's OWN process group (created by setsid in tools/detach.sh; no pattern kill) on 600 s of swap > 2 GB
# or disk < 5 GB. Log: lean_export/lake_build_all.log.
START="$1"; L=/Users/sumit/Github/quantum/lean_export/lake_build_all.log; cd /Users/sumit/Github/quantum/lean/ZiglinCert
log(){ echo "$(date '+%F %T') $*" >> $L; }
while [ "$(date +%H%M)" -lt "$START" ]; do sleep 30; done
log "start (pgid $(ps -o pgid= -p $$ | tr -d ' ')); swap $(sysctl -n vm.swapusage | awk '{print $6}'), pressure $(sysctl -n kern.memorystatus_vm_pressure_level)"
PG=$(ps -o pgid= -p $$ | tr -d ' ')
( peak=0; bad=0
  while kill -0 $$ 2>/dev/null; do
    fp=0; for p in $(pgrep -g $PG 'lean|lake'); do f=$(footprint -p $p 2>/dev/null | grep -m1 -o 'Footprint: [0-9.]* [MKG]B' | awk '{v=$2; if($3=="GB")v*=1024; if($3=="KB")v/=1024; print int(v)}'); fp=$((fp+${f:-0})); done
    [ $fp -gt $peak ] && peak=$fp; echo $peak > /tmp/lean_build_peak_$PG
    sw=$(sysctl -n vm.swapusage | awk '{print $6}' | tr -d M | cut -d. -f1); dk=$(df -g / | tail -1 | awk '{print $4}')
    if [ "$sw" -gt 2048 ]; then bad=$((bad+30)); else bad=0; fi
    if [ $bad -ge 600 ] || [ "$dk" -lt 5 ]; then log "STOP: swap ${sw} MB sustained ${bad} s or disk ${dk} GB; killing this script's own process group $PG (setsid by detach.sh; no pattern kill)"; kill -TERM -- -$PG; exit; fi
    sleep 30; done ) &
for f in ZiglinCert/Certs/mnlat_*.lean; do m=ZiglinCert.Certs.$(basename $f .lean); t0=$(date +%s)
  lake build $m >> $L.detail 2>&1; rc=$?; log "$m rc=$rc $(( $(date +%s)-t0 )) s peak-so-far $(cat /tmp/lean_build_peak_$PG 2>/dev/null) MB"; done
t0=$(date +%s); lake build ZiglinCert.Certs.All >> $L.detail 2>&1; rc=$?
log "ZiglinCert.Certs.All rc=$rc $(( $(date +%s)-t0 )) s; peak footprint of lean/lake $(cat /tmp/lean_build_peak_$PG) MB"; log "DONE rc=$rc"
