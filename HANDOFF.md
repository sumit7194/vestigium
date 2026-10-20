# Handoff: 2026-10-16 (chaos-proof phase 2 in progress)

## Running now (both detached with parent PID 1, so they survive a Claude restart), 2026-10-20 evening

1. **B15, the strong Kerr control** (constructor stage).
   - `qsim/capd/horseshoe/b15_kerr.py`, PID 24176, log `qsim/capd/horseshoe_results/kerr/b15_kerr.out`.
   - Step 1 is done: the saddle has λ_u = 62.62. Step 2 (manifold arcs, then crossings) is running, and may take hours.
   - Result: `horseshoe_results/kerr/b15_kerr.json`.
   - Not checkpointed. After a reboot, rerun the script; step 1 costs about 9 min.
2. **The MN CAPD smoke test.** One tiny box at F5-R UPO 2, with `hs_cover_v6` (built from 4c6b8b9's source).
   - PID 41078 under /usr/bin/time (PID 41075). Spec, output and timing are in
     `qsim/capd/horseshoe_results/mn_smoke/`.
   - This is the first F3 data point; an earlier attached copy ran for more than 63 CPU-min without finishing.
   - It is used ONLY to estimate time (B16: no check is changed for time).

**Next after these:**
- the B15 outcome, sent to the Bridge;
- the F3 profile (MN vs Kerr), for planning only;
- the MN F5-R constructor run (frozen B14), seeded from the A-K20 UPOs 2 and 4;
- the rigorous MN coverings under B16: no time cap, ≤ 4 cores on weekdays, daily progress records.

## HH-SECONDARY COMPLETE (2026-10-19): PASS, sealed at 5a21dde. Nothing is running.

- **Outcome:** `qsim/capd/horseshoe/HH_SECONDARY_OUTCOME.md`. All 6 required coverings are certified, and
  h ≥ 0.28120 (ρ is the plastic number).
- **Seal:** sent to the Bridge as hashes only. The embargo is ON until V14 Q2.
- **Next:**
  1. R3 Kerr and the MN chain. These wait on the user's review of A-K20, which the Bridge drafted (89bea2b).
  2. The constructor is frozen at 1da283c and is reused unchanged.

## HH-PRIMARY COMPLETE (2026-10-18)

- **Sealed at ca819cf.** The outcome is in `qsim/capd/horseshoe/HH_PRIMARY_OUTCOME.md`.
- **The seal went to the Bridge as hashes only.** My embargo `HH-outcomes-for-V14` (tools/EMBARGOES.json) stays ON
  until the Bridge reports that V14's Q2 decisions are committed. Then lift it, recording the commit, and send the
  numbers.
- **Next phase-2 items:**
  1. HH-SECONDARY: write the frozen h-set constructor.
  2. The R3 Kerr control: needs the exact gate for the B10 field and a per-piece time cap.
  3. A-K20 from the Bridge and tabula.

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
