#!/bin/zsh
# watch_new.sh REGEX FILE... -- report-only watcher that matches ONLY text written after its own start.
# For each FILE, the byte size at launch is the baseline. Each poll reads only the bytes past the baseline
# (tail -c +offset), so a line written before launch can never match (incident 2026-11-26: two watchers fired on an old
# "STOP" line). Prints "<time> MATCH <file>: <new matching lines>" and exits 0 on the first match.
#   WATCH_EXCLUDE=<regex>   matching new lines that also match this are ignored
#   WATCH_PID=<pid>         exit 0 with "<time> PID <pid> gone" when that process ends
#   WATCH_EVERY=<seconds>   poll interval (default 60)
# A file that shrinks below its baseline is reported once ("TRUNCATED") and re-baselined to 0. A file missing at launch
# has baseline 0. Never starts, signals or stops a process. Written by Claude Opus 5.5 (Quantum-personal), 2026-11-26.
re=$1; shift; typeset -A off
for f in "$@"; do off[$f]=$( [[ -f $f ]] && stat -f %z "$f" || echo 0 ); done
echo "$(date '+%F %T') watch_new start: regex '$re'; baselines: $(for f in "$@"; do printf '%s=%s ' "${f:t}" "${off[$f]}"; done)"
while true; do
  for f in "$@"; do
    [[ -f $f ]] || continue
    sz=$(stat -f %z "$f")
    if (( sz < off[$f] )); then echo "$(date '+%F %T') TRUNCATED $f ($sz < ${off[$f]}); re-baselined to 0"; off[$f]=0; fi
    (( sz > off[$f] )) || continue
    # only COMPLETE lines (up to the last newline) are read and consumed; a half-written line waits for the next poll
    chunk=$(perl -e 'open F, "<", $ARGV[0] or exit; seek F, $ARGV[1], 0; read F, $b, $ARGV[2]; $i = rindex($b, "\n"); print $i + 1, "\n", substr($b, 0, $i + 1)' "$f" ${off[$f]} $(( sz - off[$f] )))
    used=${chunk%%$'\n'*}; body=${chunk#*$'\n'}; (( used > 0 )) || continue
    new=$(print -r -- "$body" | grep -E -- "$re")
    [[ -n $WATCH_EXCLUDE && -n $new ]] && new=$(print -r -- "$new" | grep -Ev -- "$WATCH_EXCLUDE")
    if [[ -n $new ]]; then echo "$(date '+%F %T') MATCH $f:"; print -r -- "$new"; exit 0; fi
    off[$f]=$(( off[$f] + used ))
  done
  [[ -n $WATCH_PID ]] && ! kill -0 $WATCH_PID 2>/dev/null && { echo "$(date '+%F %T') PID $WATCH_PID gone"; exit 0; }
  sleep ${WATCH_EVERY:-60}
done
