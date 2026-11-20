#!/bin/bash
# mel_launch_s2.sh -- stage 2 counted run (PREREG S2-A1 cabccc9 + S2-A2 4d94bd4): t3_cert.py --set full -> T3.json.
# Detached at nice 10; guarded by capd/horseshoe/b15_run_guard.py (suffix mel_launch_s2.sh).
cd /Users/sumit/Github/quantum/qsim/mn_melnikov; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python; L=launch.log
echo "$(date '+%F %T') S2 start pid $$; t3_cert.py sha256 $(shasum -a 256 t3_cert.py | cut -c1-16); mel_gen.py sha256 $(shasum -a 256 mel_gen.py | cut -c1-16)" >> $L
echo "=== stage 2 counted T3 $(date '+%F %T') ===" >> run.out
$PY -u t3_cert.py --set full --out T3.json >> run.out 2>&1; echo "$(date '+%F %T') S2 exit $?" >> $L
echo "$(date '+%F %T') S2 DONE" >> $L
