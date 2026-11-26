#!/bin/zsh
# B15e A6 Mac mini side: every 30 min pull the Air's ckpt/ and out/ into b15d/kerr_e_air/incoming/. A checkpoint replaces
# good/<chunk>.ckpt only if every COMPLETE EP line ends with " #" and the count of complete EP records has not gone down
# (a partial last line, i.e. a write in progress, is tolerated). Otherwise the last good copy is kept. Log: pull.log
B=/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15d/kerr_e_air; mkdir -p $B/incoming $B/good; L=$B/pull.log
log() { echo "$(date '+%F %T') $*" >> $L; }
while :; do
  if rsync -a --timeout=60 air:GitHub/quantum-air/ckpt/ $B/incoming/ckpt/ 2>>$L && rsync -a --timeout=60 air:GitHub/quantum-air/out/ $B/incoming/out/ 2>>$L; then
    for f in $B/incoming/ckpt/*.ckpt(N); do t=${f:t:r}
      bad=$(awk 'NR>1 && prev ~ /^EP / && prev !~ / #$/ {b++} {prev=$0} END{print b+0}' $f); n=$(grep -c ' #$' $f); o=$(grep -c ' #$' $B/good/$t.ckpt 2>/dev/null || echo 0)
      if (( bad == 0 && n >= o )); then cp -p $f $B/good/$t.ckpt; cp -p $B/incoming/out/$t.out $B/good/$t.out 2>/dev/null; log "$t good: $n EP records"; else log "$t KEPT previous ($o records): pulled copy has $bad incomplete inner EP lines, $n records"; fi
    done
  else log "pull FAILED (Air asleep or unreachable); last good copies kept"; fi
  sleep 1800
done
