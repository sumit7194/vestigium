# Handoff: 2026-10-13 (the app closes until about Friday)

## What is still running (detached; it survives the app closing)

**One job: TS row 4 on the CAPD ORIGINAL path, for the cross-path pair only.** TS 4 is already REPLAYED on the A5
path. This run adds nothing to the certificate tally.

- **Processes:**

  | process | PID | parent |
  |---|---|---|
  | chain script `qsim/capd/replay_ts4_orig_resume.sh` | 69951 | 1 (detached) |
  | Python runner | 52069 | 69951 |
  | CAPD binary `tests/gen/replay_ts2_4_primary_o30_p256` | 52149 | 52069 |

- **Settings:** nice +19, 1 core, with A3 per-segment checkpoints.
- **Watchdog:** a 24 h watchdog trip just relaunches the run with the same input, and it resumes from its checkpoint.
  There are up to 8 attempts.
- **Expected time:** more than 30 h of CPU, because the loops are tiny (r = 0.045). At handoff it was on loop 1,
  segment 4 of 18, after 4.3 h.
- **Where the result lands:**
  - verdict and checks: `qsim/capd/replay_results/ts2_4_primary_o30_p256.json`
  - progress: `qsim/capd/tests/gen/ts2_4_primary_o30_p256.err`
  - per-attempt log: `qsim/capd/replay_ts4_orig_resume.out`
- **When it lands:**
  1. Run `sims/.venv/bin/python qsim/capd/replay_crosspath.py` to add TS 4 to the cross-path table.
  2. Append the result to the OUTCOME section in `qsim/capd/MR_REPLAY.md`.
  3. Commit, and tell the bridge.
  - If it never finishes, the table entry stays "TS 4: no original-path pair (24 h watchdog, resource)".
- **Checking on it:**
  - `tail -3 qsim/capd/tests/gen/ts2_4_primary_o30_p256.err`
  - `cat qsim/capd/replay_ts4_orig_resume.out`

Nothing else of quantum's is running.

## What is done (all committed and pushed)

- **CAPD third replay of the Morales–Ramis certificates: ALL 24 REPLAYED** (14 TS, 6 MN equatorial, 4 MN axial),
  Arb-free (CAPD/MPFR only), with 0 contradictions.
  - Every row overlaps v2's and v1's values and, entry by entry, v2's exact Lean-export G/H boxes.
  - The fields are the bridge's, gated exactly against this repo's.
  - The cross-path table agrees on every row compared; 5 homotopic secondaries PASS; repeated runs are
    bit-identical.
  - Everything, including amendments A1–A8 and all caveats, is in `qsim/capd/MR_REPLAY.md` (OUTCOME at the end,
    2799ede).
- **Lean:** 52/52 certificates kernel-checked, and the final `lake build ZiglinCert.Certs.All` succeeded (axioms
  only propext, Classical.choice, Quot.sound).
- **CAPD trust checks:**
  - differential check vs Arb (PASS);
  - NaN safeguard;
  - ODE controls (PASS);
  - files: `qsim/capd/DIFFCHECK.md`, `NAN_SAFEGUARD.md`, `ODE_CONTROLS.md`.
- **Sub-45 Plan A:** V1 PASS, and the re-audit finds that every C12 verdict STANDS (`PREREG_cuspis_sub45_check.md`).

## Open items: all wait for the user

- **Sub-45 plan C:** deferred by the bridge, to be decided by the user later.
- **Chaos-proof phase 2** (Hénon–Heiles / Kerr controls, then the proof): undecided.
- **The CAPD upstream report draft** (`qsim/capd/UPSTREAM_REPORT_DRAFT.md`) is for the user to send. Note the
  vendor-defect disclosure hold: nothing about that defect goes public.
- **Git history for the vendor-defect details** (commits 829ec37 and 17af42f): how to handle it is the user's
  decision. The current tree is already redacted.
- **Parked research threads:** MN/TS outreach, A8, the corner systematic, H3 (see the memory note on open threads).

(The previous handoff note, from 2026-09-05, is in git history at commit 01cd193.)
