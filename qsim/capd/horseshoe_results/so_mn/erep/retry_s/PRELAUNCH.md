# Branch-S retry: labelled pre-launch amendment (to RETRY_S_REGISTRATION.md, 9c5be24)

- **Go.** Sumit's go, relayed by the Bridge on 2026-11-24 after the pre-test PASS (2a9c5a8).
- **Timing.** Written and committed before any piece or reference run. No retry number exists yet.
- **Author.** Claude Opus 5.5 (Quantum).

## Pieces
- **Tiling.** The W0 = 1e-7 box (half-width 1e-7 about x0 = 36419361737/10^10, px0 = 60360992808/10^10) is tiled
  exactly by 4 pieces of half-width W0 = 5e-8 = 1/20000000. The piece centres are offset by (du, dp) ∈ {±1/20000000}²:

  | Piece | du | dp |
  |---|---|---|
  | mm | −1/20000000 | −1/20000000 |
  | mp | −1/20000000 | +1/20000000 |
  | pm | +1/20000000 | −1/20000000 |
  | pp | +1/20000000 | +1/20000000 |

- **Binary** `tests/mn_so_piece` (sha256 491fb0a1…, guard passed). It is mn_so.cpp plus `CENTRE_OFFSET="du dp"`, which
  shifts the lift's centre parameters by those exact rationals, the same meaning as b17_check's CENTRE_OFFSET.
- **Identity check** (it must hold before any piece launches). Both binaries run from t = 0 to STOP_AFTER_T = 5.0 under
  the same environment, A3's mn_so_erep (4a48b59a…) and mn_so_piece with CENTRE_OFFSET unset:
  - the final state files must be byte-identical;
  - the logs must be identical with the wall-time fields removed.
  The result is recorded below.
- **Each piece.**
  - Run with `CENTRE_OFFSET="du dp" SO_EREP=zsym SO_FIXED_REDO=1 SAVE_FROM=292 SAVE_DT=100 nice -n 10 ./mn_so_piece
    1/20000000 retry_s/cp/b17_cp_5e-8_<p>.txt retry_s/<p>/st 805.3`, detached, from t = 0.
  - Checkpointed (CKPT_SEC default) and resumable; a restart must print the RESUMED line.
  - Guard: `erep_guard.py --inform`, cap 500 MB (warn and pause only, never kill; the disk floor stops).
  - There is no cost watch. A3's cost baseline does not apply to a piece.

## Per-piece checkpoint files (generated; committed with this amendment)
- **Source.** `tests/b17_checkpoints.py 5e-8 retry_s/cp/b17_cp_5e-8_<p>.json 4 du dp`. The new optional `du dp`
  arguments shift the centre; omitting them leaves the original centre.
- **Checkpoints.** The same 10 checkpoint times as A3 (b17_times.json). u1, u2, nH, the true hull widths (16 boundary
  points of the piece, DOP853 1e-13) and the gains are computed at the piece centre.
- **Disclosure: the regenerator is NOT byte-identical to the stored 1e-7 file.** With no offset, b17_checkpoints.py
  reproduces b17_cp_1e-7.txt only to these maximum relative differences:

  | Field | Max relative difference |
  |---|---|
  | u2 | 1.4e-10 |
  | true widths | 5.7e-12 |
  | gains | 5.7e-11 |
  | u1 | 2.8e-15 |
  | nH, centres, kinds | identical |

  The likely cause is library and numerical changes since 2026-10-23. All 4 piece files come from the same code today,
  so they are mutually consistent. The differences are far below anything K = 5 can resolve.

## C-floor reference runs (8 per piece, 32 in all)
- **Points.** For each piece: its 4 corners and 4 edge midpoints. These are W0 = 0 point runs:
  `CENTRE_OFFSET="du' dp'" ./b17_check_pt 0/1 retry_s/cp/b17_cp_5e-8_<p>.txt > retry_s/refs/ref_<p>_<q>.out`, with
  (du', dp') = piece centre + (±1/20000000 or 0) in each coordinate, the q labels as in A3 (mm mp pm pp zm zp mz pz).
- **Why 32 runs.** The runs project onto that PIECE's covectors, so points shared between pieces are still separate
  runs, one per piece file.
- **Cost.** A3's 1e-7 reference runs took 7169 s each (to 1018.7, including sections): 32 × ~2 h ≈ 64 core-h. RSS is
  small; 300 MB each is declared (measured on the first run and reported).

## Reading
- `retry_s/read_retry.sh`, committed now. Per piece:
  - **controls** — the registered centre-offset line; C-floor containment PASS against that piece's 8 refs;
    HARNESS-ERROR 0; BUG 0;
  - **criteria** — all 8 time checkpoints with t ≤ 805.3 read PASS (K = 5): 283.89, 290.85, 291.89, 295.89, 793.23,
    800.09, 801.23 and 805.23; no THREW.
- **Stricter than A3.** A3 read 5 time checkpoints; the retry needs all 8 in [0, 805.3]. Nothing is loosened.
- **Overall.** PASS only if all 4 pieces pass; INVALID if any control fails; otherwise FAIL.
- **Not measured.** The sections stay deferred: sec_down is saved as a set only. Runs stop at T_end 805.3, so sec_return
  is not reached.

## Cost and peaks (corrected estimate)
- **Per piece.** A3's own record is t 0 → 291.9 in 154 323 s (main_redo) plus 291.9 → 805.3 in 269 748 s (main_cont),
  about 118 h per piece at W0 = 1e-7. This is an upper estimate: the pre-test's quarter piece used far fewer S4 leaves.
- **Pieces in total.** 4 × ≤ 118 h ≈ ≤ 470 core-h. It is not the ~300 core-h I said earlier; that figure is withdrawn.
- **References.** ~64 core-h.
- **Total.** ≤ ~535 core-h. Wall time is about 5 days with the 4 pieces in parallel.
- **Memory.** Each piece's peak is like A3's (213 MB at t 805): about 0.25 GB per piece, 0.5 GB declared.
- **Disk.** States are about 28 MB by t 800. SAVE_DT 100 gives about 6 saves per piece, under 1 GB in all.

## Identity check result (2026-11-25, before any piece launch): PASS
- **Runs.** mn_so_erep and mn_so_piece (CENTRE_OFFSET unset), each from t = 0 to STOP_AFTER_T 5.0, ending at step 40,
  t = 5.0458615691.
- **Result.** The final state files are byte-identical (`cmp`). The logs are identical once the wall fields are removed.
- **Wall time.** 2000 s and 2007 s, about 50 s/step on a fully loaded box, against about 17 s/step in A3's own early
  steps. The 118 h per-piece estimate assumes A3's conditions; a loaded box makes it longer.
- **Outputs.** `retry_s/identity/{old,new}/run.out`. The state files are not committed.
