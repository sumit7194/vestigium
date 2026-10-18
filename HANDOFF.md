# Handoff: 2026-10-16 (chaos-proof phase 2 in progress)

## Running now (detached with nohup): HH re-run `hh1b` (B13), started 2026-10-17 about 19:55

- **What it is:** a re-run of M1⟹M2 and M3⟹M4. The reboot around 13:20 killed the hh1a runs of these two after about
  13 CPU-hours each, with no results.
- **The runner:** `HS_BIN=qsim/capd/horseshoe/hs_cover_ck python qsim/capd/horseshoe/hs_run.py hh1b`, PID 72462.
  Code at 816fdfb. It runs 4 chunk processes at nice 19, using 4 cores and very little memory.
- **Log:** `qsim/capd/horseshoe_results/hh1b_run.out`.
- **Progress:** count the `^P ` lines in `qsim/capd/horseshoe_results/ckpt/*.ckpt`. Each chunk has 128 top-level
  pieces.
- **Merged results land in** `hh1b_M1M2.json` and `hh1b_M3M4.json`, with the per-chunk JSONs beside them.
- **IF THE MACHINE REBOOTS:** rerun the SAME command. The checkpoints reload the finished pieces.
- **Update, 2026-10-18 12:30.** Three hh1b chunks had finished and are sealed (691d5d8). The slow M3⟹M4 chunk c1
  was re-split (B13 addendum) and now runs as
  `HS_BIN=qsim/capd/horseshoe/hs_cover_ck python qsim/capd/horseshoe/hs_run.py hh1b2`, runner PID 85312, with 3
  processes. Its log is `hh1b2_run.out`. After a reboot, rerun **hh1b2** (not hh1b): the seeded checkpoints are
  reused. It writes the merged `hh1b_M1M2.json` and `hh1b_M3M4.json` at the end.
- **When it lands:**
  1. Commit the results.
  2. Send the Bridge ONLY the commit hash and the sha256 of the JSONs. The HH blind is still in force.
  3. Write the HH outcome both ways: under the original 48 core-hour budget, and under B13.
- **Process slip:** on 2026-10-17 I used a pattern-based `pkill`, matching my own scratch path only, on a test
  process. The rule is explicit PIDs only. No other process was affected.

## Pending side task: the TS public snapshot (the Bridge asked for it; local only, nothing pushed)

- **Location:** `/Users/sumit/Github/snapshots/ts2-mn-integrability/quantum/` (295 files, MANIFEST.md). The Bridge
  agreed the scan and gave its rulings: keep files byte-identical, and keep the absolute paths.
- **REQUIRED before anything goes public:** once HH frees the cores, copy the snapshot to a fresh scratch directory.
  In that copy, run `cargo build --release` in native/iahub, then run:
  - `snapshot_tools/rerun_v2_row.py ts2 4`;
  - `snapshot_tools/rerun_one_row.py ts2 4`.
  Compare both against the shipped JSONs, then report the outcome and the diff to the Bridge.
- **The TS metric inputs** are now shipped at `snapshots/ts2-mn-integrability/ansatz_inputs/` (the user approved).
  `rerun_v2_row.py` reads them from `../ansatz_inputs/`; no symlink is needed.
- **Snapshot test, part 1, the v2 run: PASS (2026-10-17).** The run was a fresh copy (`cargo build` inside it) of
  `rerun_v2_row.py ts2 4`. 67/67 fields are identical to the shipped `qsim/mr_v2_ts2_row4.json`, apart from
  `seconds`.
- **Snapshot test, part 2, the CAPD replay: PASS (2026-10-17).**
  - The first try failed with BUILD-FAILED: the assembly had dropped the executable bits, so check_proof_object.sh
    gave "permission denied".
  - Fix: the assembly now preserves modes, and the snapshot is rebuilt with the same content sha256s.
  - Re-run from a fresh copy: REPLAYED, with 5/5 consistency checks. The result is bit-identical to the shipped JSON
    except `bridge_file` and `seconds`.
  - The Bridge has been told.
- **The part-1 PASS has been sent to the Bridge.** HH status to the Bridge stays at core-hours only.
- **Four fable_briefs prompts were drafted for the user's separate sessions** (not run here):
  `/Users/sumit/Github/fable_briefs/quantum/PROMPT_{1..4}_*.md`, with read-only inputs under `inputs/`.


## CAPD upstream posts: FROZEN (Bridge-approved at ed91fee, 2026-10-17)

`qsim/capd/upstream_posts/` is 1 comment and 4 issues, for the user to post. Do NOT edit these files. If anything
needs to change, tell the Bridge first.

**POSTED by the user (2026-10-17):** CAPDGroup/CAPD issues #29 (log NaN), #30 (sin cost), #31 (arm64 ctest) and #32
(MPFR API), plus a comment on #27. The Bridge verified the posted text against ed91fee. If maintainers reply, tell the
Bridge before drafting any response; the user answers.

## Phase-2 state (all committed and pushed)

- **Pre-registration:** `PREREG_chaos_horseshoe_phase2.md`, AGREED with amendments B1–B10. The OUTCOME log is at
  the end of that file.
- **T0:** done; see `qsim/capd/horseshoe/T0_HYPOTHESES.md`.
- **R1, the Rössler control:** PASS; see `qsim/capd/horseshoe/R1_ROSSLER.md`.
- **HH first pass (the registered run):** (b) holds for 7/7 coverings. (a) is not certified at the first rung (16×16
  boxes). W-AZ1 and W-AZ2 are already rejected by certified failures.
- **Next steps:**
  1. HH-SECONDARY: my own h-sets, through the frozen constructor, which is not yet written.
  2. Kerr (R3). It needs the B10 regularised field, its exact-equality gate, and a per-piece time cap.
  3. A-K20, from the Bridge and tabula: which point, (E, L_z) and seeds.
- **K20 context.** At χ≈0.9, q=0.95 (F5-R) there is a naked singular B=0 ring that bounds the published inner sea.
  B9 excludes it from D. A horseshoe there would describe the regular causal exterior only. p2 on the MR level
  (1,0,4) is the clean target.

## Earlier handoff (2026-10-13; its TS 4 item is resolved: REPLAYED, cross-path AGREE)

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
