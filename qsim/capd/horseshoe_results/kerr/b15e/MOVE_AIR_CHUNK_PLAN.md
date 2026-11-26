# Plan 4a: move one Air kerr_e chunk to the Mac mini (PLAN ONLY, not executed)

Written 2026-11-27 by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request, after the cost projection (KERR_E_PROJECTION_2026-11-27.md, 6966fe3). Ending a running chunk deliberately needs Sumit's word, relayed by the Bridge. Nothing in this file runs without that word.

## Which chunk

The slowest Air chunk moves: N2N3 or N3N4. Neither had an EP record after 11.4 h.

The rule is applied at the time of the move:
1. The chunk with the fewest EP records moves.
2. If two are tied, the one whose current piece started most recently moves, because it has the least work to lose.
3. If the records by then show that another chunk is clearly slower, that one moves, and the change is stated in the go request.

## Core

The chunk takes a Quantum core on the Mac mini only when one is free within the Quantum cap of 7. That means after the A8 set ends and a retry piece (2836, 2838, 4180 or 4182) finishes.

The A8 test core is already promised: when the A8 set ends, the paused W2 ref 27732 and its worker 38321 resume on it. twin_a's launch also needs cores. If the move and twin_a want the same core, I ask the Bridge first.

The Mac mini fleet stays at 9 or fewer, and the job runs at nice 10.

## Identity: same binary, already tested on both machines

The moved chunk resumes on the Mac mini with the same static binary it runs on the Air: hs_cover_b15e2s, sha256 df234aa23e7e0692… The sha256 was checked on both machines on 2026-11-27.

A6 identity stage (i) on the Mac mini M4 and stage (ii) on the Air M1 both PASSED (279bf22):
- T1 4/4 byte-identical;
- T3 byte-identical (128 EP records);
- T4: SIGTERM at 32 records, then a restart byte-identical (EDGES RELOADED 32);
- T5 must-fire;
- T6/T6b.

So the EP records hold the same bits whichever machine wrote them.

Optional extra check before the move, about 1 core-hour or less (one Mac-mini core, nice 15): a cross-machine resume. The Air's A6 T4 checkpoint (32 records), resumed on the Mac mini, must give output byte-identical to the A6 T3 output.

## Steps, after the go

1. **Time the stop.** Watch the chunk's Air checkpoint with tools/watch_new.sh, reading over ssh. When a new EP record lands (complete, ending in ` #`), the next steps follow within minutes. The loss is then minutes of the next piece, not hours. If no record lands within the time set in the go, the stop goes ahead anyway, and the loss is the piece in progress (about 6–11 h of Air time).
2. **Stop on the Air.**
   - Confirm the PID from its command line (bin/hs_cover_b15e2s plus specs/<chunk>.spec), then `kill -STOP`.
   - Copy the checkpoint, then `kill -TERM`.
   - Confirm the process is gone and that its out file has no WATCHDOG TIMEOUT. The rc can't be captured, because the process is not my child, so I say so.
   - The caffeinate process for that PID ends by itself (`-w`).
   - Log it in the Air's launch.log.
3. **Move and verify the checkpoint.**
   - Copy it with scp to b15d/ckpt/kerr/<chunk>.ckpt. If that file already exists, the step is REFUSED, using mv -n semantics.
   - The sha256 must be equal on both ends.
   - Every line must be an EP or EF line keyed by this chunk's tag (<Ni>><Nj>/E/…), each EP line ending in ` #`, with no torn last line.
   - The EP count must match the Air copy, and the keys must run 0..k-1 on side 0 (then side 1) with no gaps.
4. **Spec.** Copy the Air spec and change only the checkpoint line to the Mac-mini path. The diff must be exactly that one line. Record the old and new sha256, as in A5 and A7.
5. **Launch on the Mac mini**, detached (tools/detach.sh, setsid), with the A5 launch pattern:
   - `HS_WATCHDOG_S=2592000 nice -n 10 stdbuf -oL hs_cover_b15e2s <spec>`, plus a kerr_guard.
   - The moved chunk gets a fresh 30-day timer, the parser maximum on b15e2s. At the Mac mini's ~4 h per piece, 128 pieces is about 21 d, inside that timer, so it needs no timer raise unless its rate drops.
6. **Verify the resume.**
   - The output's "EDGES RELOADED k" must equal the moved EP count.
   - The next EP key written must be index k.
   - The process must show nice 10, state R.
   - Log it in b15d/run.log and the fleet log.
7. **Pulls.** pull_air.sh would otherwise keep pulling the moved chunk's Air checkpoint, now frozen. That chunk is marked moved in kerr_e_air/ (a note plus a pull.log line), so promote_air.sh never treats the Air copy as final. The Air's frozen checkpoint is moved, not deleted, into a moved_to_mini/ folder on the Air.

## What it changes

- The moved chunk's computation and records are unchanged, since it is the same binary and the same spec except the checkpoint path. Only the piece in progress at the stop is recomputed.
- The 4 remaining Air chunks run 4 processes on 4 performance cores, plus whatever else is on the Air.
- Air budget: Quantum drops from 5 to 4. The Mac mini's Quantum count rises by 1, within the cap of 7.
