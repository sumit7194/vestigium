# PAUSED (2026-11-27 00:30)

PAUSE of the 5 Air kerr_e chunks (N2N3 8602, N3N4 8615, N4N5 8628, N5N0 8641, N5N1 8654) at 00:30:00 Air time, SIGSTOP each verified by PID and argv; air_guard 8663 HELD by SIGSTOP (its memory-resume path cannot SIGCONT them). Sumit decision via the personal Bridge: the negative control waits for the MN target. Nothing killed; reversible. pull_air keeps pulling: a paused chunk has no DONE, so promote_air never promotes it, and its record count only stays level, so it is never KEPT or REFUSED. Their 30 d alarms (2026-12-26 12:59:19) keep counting while paused; SIGALRM pending on a stopped process would end it at once on resume after that date (exit 124, only the piece in progress lost; EP checkpoints are the safety net). N1N2 32284 (Mac mini) keeps running. 4a cancelled; twin_a/kerr_a on hold.

Resume (only on Sumit's word via the personal Bridge): SIGCONT the 5 chunks by verified PID, then SIGCONT air_guard 8663, and log it in the Air launch.log, b15d/run.log and here.

# N1N2 on the Mac mini PAUSED too (2026-11-27 00:36:11)

PAUSE (SIGSTOP, verified PID and argv) kerr_e/N1N2 PID 32284 and HOLD (SIGSTOP) its kerr_guard 32294 first, so the guard's green-pressure/disk resume path cannot SIGCONT it: Sumit decision via the personal Bridge (by §6.3 it may need a rerun with the MN constructor anyway; its core goes back to the pool). Nothing killed; reversible. 3 EP records in ckpt/kerr/N1N2.ckpt; the piece in progress is held in memory. Its 30 d alarm (2026-12-26 11:29:59) keeps counting; a resume after that ends it at once (exit 124), losing only the piece in progress.

Resume (only on Sumit's word via the personal Bridge): kill -CONT 32284, then kill -CONT 32294, each after checking its argv; log it in b15d/run.log.

# ENDED by the MN pilot STOP (2026-11-27 00:46:06)

All 6 paused kerr_e chunks (Air: N2N3 8602, N3N4 8615, N4N5 8628, N5N0 8641, N5N1 8654; Mac mini: N1N2 32284) and their held guards (air_guard 8663, kerr_guard 32294) were ended by SIGTERM then SIGCONT, each verified by PID and argv, on Sumit's decision via the personal Bridge.

**Reason:** MN pilot step 0 = STOP (d9f9ad9). Without the MN target the Kerr negative control has no use (§6.3: the control follows the target), and resuming would have hit the 2026-12-26 alarm anyway.

**Kept:** every checkpoint and EP record (Air ckpt/ on the Air and pulled to kerr_e_air/incoming/ and good/; ckpt/kerr/N1N2.ckpt on the Mac mini). Only the pieces in progress were lost. N0N0 and N0N1 (finished 2026-11-24) stand as recorded. pull_air.sh 69773 ended too. Nothing deleted.
