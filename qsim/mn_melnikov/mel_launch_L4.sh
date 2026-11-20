#!/bin/bash
# mel_launch_L4.sh -- stage 2, part 1 (PREREG S2-A1, cabccc9): L4 by the stage-1 pipeline, gates included, at 128 bits.
# Detached at nice 10; guarded by capd/horseshoe/b15_run_guard.py (suffix mel_launch_L4.sh).
cd /Users/sumit/Github/quantum/qsim/mn_melnikov; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python; L=launch.log
echo "$(date '+%F %T') L4 start pid $$; mel_gen.py sha256 $(shasum -a 256 mel_gen.py | cut -c1-16); mel_cert.py sha256 $(shasum -a 256 mel_cert.py | cut -c1-16)" >> $L
echo "=== stage 2 L4 $(date '+%F %T') ===" >> run.out
$PY -u mel_cert.py --only L4 >> run.out 2>&1; echo "$(date '+%F %T') L4 exit $?" >> $L
echo "$(date '+%F %T') L4 DONE" >> $L
