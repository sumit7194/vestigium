# Handoff: 2026-10-16 (chaos-proof phase 2 in progress)

## State on 2026-10-24 night (the Mac is fully ours overnight)

**Running (all detached, ppid 1):**
- The second-order MN runs `tests/mn_so` at 1e-7 and 1e-6 (`horseshoe_results/so_mn/run_1e-{7,6}.out`, state files
  `.state`, saved every 30 min; kill-9 resume is bit-identical). Full return ~27 h. Section checkpoints are saved as
  `.state.pre_sec_*` for `tests/mn_sec`.
- 16 containment reference runs (`so_mn/contain/launch_refs.sh`: 8 points × 2 box sizes, 8 at a time, nice 10).
- B15, kept running by the user's decision.

**Gates GREEN:** toys A–E plus negatives; MN lift; section toy plus negatives; D²f gate (15,360/15,360); restart.

**Next:**
1. Read the swing-1 checkpoints (t ≈ 284–296) of both SO runs.
2. Containment (`tests/b17_containment.py` with the SO run outputs and `so_mn/contain/ref_*`).
3. The sec_down sections (`tests/mn_sec`) for both runs, sent to the Bridge together with the precondition lines.

**B15 decision (user, 2026-10-24 midday):** B15 ends with the macOS-update restart and is NOT relaunched as is. Before
the next run it is to be PORTED TO RUST and optimised. Same rules as everything else: the frozen constructor's logic is
unchanged; the Rust map is gated against the Python map (MNFlow), and also against kerr_p.dylib (the compiled C++
candidate built 2026-10-24, >10^4x faster than Python) as a second implementation; a registered amendment comes
before any counted run. kerr_p_gate.py was running when the restart came, and is to be rerun.

**Earlier B15 plan (2026-10-24 night, superseded by the Rust decision):** let it run. Build and gate a compiled Kerr P/Pinv alongside it (C++ from
the same generated field; same frozen constructor through the adapter; gate: agreement ≤ 1e-10 against the Python P at
sample points including long returns; a registered amendment). Then decide with the user whether to relaunch B15 with
it plus the validated pcache checkpointing.

## State on 2026-10-23 (MN swing work with the Bridge; prereg B17, B17a, B18, B18a registered)

**Running (all detached, ppid 1):**
- B15, PID 24176.
- The B17 positive control at 1e-12: `tests/b17_check`, PID 37351, writing `mn_smoke/b17_control_pos_1e-12_v3.out`.
- The 4 corner containment reference runs: `b17_check_pt` with W0 = 0 and CENTRE_OFFSET; `mn_smoke/b17_contain_{mm,mp,pm,pp}.out`.
- `mn_smoke/launch_midpoints.sh`, which starts the 4 edge-midpoint runs (`b17_contain_{zm,zp,mz,pz}.out`) once 2 corner
  runs are done.

**When they finish:**
- Run `python3 qsim/capd/horseshoe/tests/b17_containment.py mn_smoke/b17_control_pos_1e-12_v3.out
  mn_smoke/b17_contain_*.out`. All 8 points must be contained at all 10 checkpoints.
- Harness validation also needs v3 to pass B17 from 0 to checkpoint 1 (t = 283.885).
- Only then is any fix (QRESEED needle-frame re-seed, moving integration frame) read against B17.

**Findings so far** (pushed, latest 1ff1bc7):
- The 8-D augmented field passes 1e-8 through swing 1 but is ~100–500× fat after it.
- CAPD's default reorganisation hulls the needle. The default policy fails B17 over the full return even at 1e-12
  (u2 362× at Σ).
- The S4 g_φφ check needed B18/B18a. The CTC region reaches x ≈ 1.921, and the UPO's periapsis is at 1.9423.

## State on 2026-10-21 evening (the user is away Fri–Mon; the app will be closed)

**Running:** only B15 (Kerr control, constructor stage). `qsim/capd/horseshoe/b15_kerr.py`, PID 24176, detached
(ppid 1), 1 core.
- Step 1 is done (saddle λ_u = 62.62). Step 2 (W^u arcs) prints nothing until the arc pass ends, so there is no ETA.
- The user said to let it run, with no restart.
- Result: `horseshoe_results/kerr/b15_kerr.json`. Not checkpointed.
- Cores agreed with the Bridge: it takes about 6 for a V14 chain; quantum keeps only B15's 1 while the app is closed.

**The MN smoke test FAILED (planning-only, single box).** Diagnosed with no verdicts; commits de5802a, 23e4869, 0e0d1ce.
- Cause 1, the p_y lift: the radicand evaluated once on the hull inflates p_y about 500×. The fix is a mean-value form
  intersected with it (`tests/mn_diag.cpp`, lift mv). It needs a registered amendment.
- Cause 2, the field's interval form: the interval evaluation over-widens 10–1.7e3× along the orbit, from the β terms
  (Kerr at the same points: 1–50×). The inner swing (x ≈ 1.94, |J| ≈ 2.5e3) amplifies it, so every set blows up at
  t ≈ 290 of the 1019 return.
  - Not fixed by: box size, set type, Taylor order, or momentum rescaling.
  - A point start completes the return.
- Tools: `tests/mn_diag.cpp`, `tests/mn_fieldwidth.cpp`, `tests/cse_attrib.py`, `tests/fieldwidth.py`.
  Results: `horseshoe_results/mn_smoke/`.

**Update 2026-10-21 late: MN swing diagnosis (with the Bridge; commits up to this one; all diagnostic, nothing adopted)**
- 8-D augmented field (mn_codegen8.py, gen/mn_field8.h, tests/mn_diag8.cpp): exact on the manifold, 549 ops, ~6x faster,
  but it ALSO dies at the swing (t = 290.35). Sets stay ~2x the TRUE width until t ~ 285 (tests/width_ratio.py); the
  true image is affine and contracts after the swing (tests/nonlin_hull.py). The excess grows in C*r0 through the swing
  (diag8_decomp); the absolute-product amplifier is only ~20x (tests/abs_product.py), so the per-step seed rad(J) over
  ~1600 tiny steps carries it. Order 30 = order 20 (truncation excluded). Correlated p_y lift (corrpy): dies at 290.21.
- W-scaling runs (diag_W7/W10/W12, ppid 1, end at t = 300): were alive past 290.4-291.2 when last checked; read them.
- Next candidates: C^r jet set (cn2) on the 8-D field (~25 s/step, ~19 h to the swing; needs checkpoints + a tested
  kill-9/resume before ANY unattended run, and the user's OK), and/or fewer larger steps (time reparametrisation).
- b15_kerr_ck.py + pcache.py: checkpointed B15 copy (journal of every finished P/Pinv call; frozen constructor untouched).
  NOT YET VALIDATED: the step-1 test made only one call. Redo the kill-9/resume test on step 2 before relaunching B15.
  The Bridge coordinates the user's restart question (my recommendation: let diagnostics end, restart, relaunch B15 as
  the checkpointed copy once validated).

**Next, when the user is back:**
1. Rewrite the field for interval evaluation in `mn_codegen.py`: simplify the exponent arguments symbolically,
   combine the exponentials, use log-sum-exp, then a centred form.
   - Gates: the codegen enclosure gate; the width ratio along the orbit; mn_diag through t ≈ 290.
   - The Bridge is doing an independent regrouping from v13_field.py as a cross-check.
2. Register the amendments (lift, field form) before any run that counts. Then a new smoke test.
3. Write the launch plan, and get the user's OK, BEFORE any MN covering run.
4. Cores: the user asked on 2026-10-21 for ≥ 3 cores at normal priority (jobs launched from Claude's shell inherit
   nice 5).

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

## 2026-10-24 ~13:35 IST: macOS 27.0.1 restart (the user's update). After the restart:
- Python B15 (PID 24176) is NOT relaunched (the user's decision; B15 moves to the compiled map, B15b/B15b-1 registered).
- SO runs: resume both (they continue from their .state saves; append to the .out files):
  cd qsim/capd/horseshoe/tests; R=../../horseshoe_results
  nohup ./mn_so 1/10000000 $R/mn_smoke/b17_cp_1e-7.txt $R/so_mn/run_1e-7.state 1018.2 >> $R/so_mn/run_1e-7.out 2>&1 &
  nohup ./mn_so 1/1000000  $R/mn_smoke/b17_cp_1e-6.txt $R/so_mn/run_1e-6.state 1018.2 >> $R/so_mn/run_1e-6.out 2>&1 &
- B15b MNFlow reference workers: resume all 4 (they skip finished task ids):
  cd qsim/capd/horseshoe; L=../horseshoe_results/kerr/b15b_gates
  for i in 0 1 2 3; do nohup /Users/sumit/Github/quantum/sims/.venv/bin/python -u b15b_mnflow_worker.py $i 4 >> $L/mnflow_w$i.log 2>&1 & done
- Re-arm the watchers (SO checkpoints; the workers' completion -> b15b_gates_eval.py).
- Next code: the G6 toys and wrapper (design B15B_G6_DESIGN.md + the Bridge's points: the D4 angle factor, vertex/end/gap scans,
  a replica of the arc bookkeeping that must reproduce the arcs bit-for-bit), B15_MAP=rust wiring with provenance in the journal.
- Hold the Command Line Tools update until the SO runs and the B15b gates are done (any rebuild would need its checks redone).
- UPDATE (the user's decision, 2026-10-24): installing the Command Line Tools update together with macOS. After the restart:
  rebuild both Kerr maps with kerr_build.sh (new provenance = toolchain change, recorded); re-run G0, G2, kerr_negctl.py and the
  Bridge's determinism check (G2 set twice, bit-identical) on the new binaries BEFORE they are used; the gate evaluation
  (G1/G3/G4) recomputes the compiled side anyway. CAPD binaries (mn_so, mn_sec, toys) are NOT rebuilt unless needed; if they
  are, redo the toy/section gates and the kill-9 restart bit-identity test first. The SO runs resume on their existing binaries.

## 2026-10-26 ~13:42 IST: the Claude app was force-closed; every nohup'd job died. NOTHING restarted (the user's instruction)
- **Killed:** the fix-test runs (SO_FIXED_REDO, mn_so_fix) at t 289.73 (1e-7) and 289.70 (1e-6), past the old throw
  point. The fix was still clean: maxE 5.3e-9 / 6.2e-6 (W0^3). They resume from so_mn/fix_test/fix_1e-*.state (saved
  13:20 / 13:23), losing about 20 min each. 0.25-grid saves are kept up to t 289.50.
- **Already done:** the DIAG reruns threw as expected at 07:18 / 07:25 (the complete record of the failure).
- **Stopped earlier, by the CRITICAL guard at 12:09** (swap free 281 MB < 300): MNFlow grinder PID 78188, in-progress
  task lost (~1.2 h). G3 stands at 171/200. NOT reported at the time (no watcher armed): disclosed to the user.
- **The lesson** (memory: run-detached-from-app): launch every long job in a NEW SESSION (setsid via perl POSIX, or
  launchctl), not just nohup &, and verify PGID/SID/PPID after launch.
- **To resume (only on the user's word), detached properly**, from qsim/capd/horseshoe/tests:
  SO_FIXED_REDO=1 SO_DIAG_FROM=0 SAVE_FROM=287.75 SAVE_DT=0.25 ./mn_so_fix 1/10000000 ../../horseshoe_results/mn_smoke/b17_cp_1e-7.txt ../../horseshoe_results/so_mn/fix_test/fix_1e-7.state 291.9
  and the same with 1/1000000, b17_cp_1e-6.txt and fix_1e-6.state; plus one MNFlow grinder (b15b_mnflow_worker.py grind 0 1) under b15b_critical_guard.sh.
- **2026-10-26 ~14:00, RESUMED after the macOS restart (the user's OK), all fully detached via tools/detach.sh** (new
  session, PPID 1, SID = PID, verified): mn_so_fix 1e-7 (PID 6178) and 1e-6 (PID 6180), with SO_FIXED_REDO=1,
  GUARD_RATIO=1e-3, DIAG and 0.25-grid saves; one MNFlow grinder (PID 9248) under b15b_critical_guard.sh (PID 9296).
  - A guard bug was found on relaunch: after a boot macOS swap total = 0 read as "free < 300 MB", and the guard stopped
    the grinder within seconds. Fixed: CRITICAL now needs swap total >= 1 GB.
- 2026-10-26 16:50: the reference worker (MNFlow grinder) PAUSED on the user's word (it reached a ~16 GB footprint on one plunge task; its in-progress task is lost). G3 stands at 171/200 + whatever has finished; resume later: b15b_mnflow_worker.py grind 0 1 via tools/detach.sh, plus b15b_critical_guard.sh. The SO fix runs continue (mn_so_fix2, max-norm guard 0.02).
