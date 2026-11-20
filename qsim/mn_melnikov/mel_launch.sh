#!/bin/bash
# mel_launch.sh -- stage 1 of PREREG.md (REGISTERED a8695e2 + 2aec7f9): gates, then L2 / L1 for the MN target, then the Kerr
# controls and the sabotage, at 128 bits. Detached at nice 10; guarded by capd/horseshoe/b15_run_guard.py (suffix mel_launch.sh).
cd /Users/sumit/Github/quantum/qsim/mn_melnikov; PY=/Users/sumit/Github/quantum/sims/.venv/bin/python; L=launch.log
echo "$(date '+%F %T') start pid $$; mel_gen.py sha256 $(shasum -a 256 mel_gen.py | cut -c1-16)" >> $L
$PY -u mel_cert.py --only L2; echo "$(date '+%F %T') L2 stage exit $?" >> $L
$PY -u mel_cert.py --only controls; echo "$(date '+%F %T') controls exit $?" >> $L
echo "$(date '+%F %T') DONE" >> $L
