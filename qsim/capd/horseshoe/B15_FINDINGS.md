# B15 (Kerr, rust map) counted run and G6: FINDINGS

Written by Claude Opus 5.5 (session "Quantum"), 2026-11-20, from the run's own records. Nothing below has been
re-tuned; it reads the registered outputs. The Bridge rules on the next step.

## The run
- **Launcher:** b15_launch.sh, PID 78628, detached, nice 10. It ran from 08:39:52 to 22:33:04.
  - Steps 1–2 (b15_kerr_ck.py, B15_MAP=rust, kerr_rs sha256 42ea6c3c…): 1076 s, exit 0.
  - G6 (b15b_g6_run.py): about 13.6 h, exit 0. Peak tree footprint 2134 MB.
- **Guard (b15_run_guard.py):** first armed at 2048 MB; earlier re-armed at 4096. At 19:58 it was re-armed at 6144 MB
  (a new guard first, then the old one retired by verified PID), per the Bridge's memory relaxation from Sumit. The
  guard never tripped. The full record is in b15_rust_guard.log.
- **Outputs:**
  - b15_kerr_rust.json, b15_rust.journal, b15_rust_arcs.npz, b15_rust_plunges.jsonl, b15_rust_run.out,
    b15_rust_launch.log.
  - b15_g6.json is 931 MB, sha256 00ffe9a6dc3a8e49ccf2ce2c54631fb02e011e1c78e6fdce1fb90b68c792b75b. It is kept on disk and
    gitignored, because it exceeds the git host limit.
  - b15_g6_summary.json comes from b15_g6_summary.py, a read-only streaming tally of b15_g6.json.

## Constructor verdict (steps 1–2)
- **Step 1:** saddle z = (1.84118843978127, 0), λ_u = 62.6203, λ_s = 0.0159693. D2 is robust: λ_u enclosed in
  [62.62026849, 62.62026867].
- **Step 2:**
  - 10081 crossings;
  - 147 with angle ≥ 0.01 (range up to 0.04586);
  - 9625 red flags;
  - 7942 plunges, each certified (P5: 7942 records, the same as the journal's 7942 None results).
- **The constructor's verdict:** "candidate connections: steps 3-4 required (prediction: rigorous coverings give no
  ρ > 1)".
- **B15b-2 scope note:** the registered prediction is NOT CONFIRMED because of an implementation scope limit (steps
  3-4 are not implemented). This is not a negative result.

## G6 verdict: UNRESOLVED (registered rule)
- **Completeness:**
  - complete = true;
  - replica bit-identical;
  - journal misses 0;
  - chord segments 0;
  - the D4/D6/D7 counts equal the run's (10081 / 147 / 9625).
- **Every crossing was thin at the run tolerance.** D1 already notes "tol < 10 e_map", so all 10081 were recomputed at
  1e-14.
  - **6023 crossings are still thin at 1e-14, so UNRESOLVED.** None of them is an accept: all are rejects or red-flag
    decisions below 0.01.
  - 2150 crossings carry the flag "error unmeasured (a return beyond the G4 range)".
- **Near-miss scan (the Bridge's choice 3):**
  - 1,639,912 segment pairs could become a crossing at the red-flag level. All were recomputed at 1e-14.
  - **203,299 are still thin, so UNRESOLVED.**
  - 238 near-misses EXIST at 1e-14, with angles 8.3e-7 to 4.6e-6. **211 of them are red flags the run did not
    record.** None is an accept.
- **D3 / P5:** 7942 plunge records against 7942 None results. The minimum y-slack is 1.07e-4; no R-slack value is
  recorded.
- **Note carried from the Bridge:** the 1e-14 error is a self-convergence ESTIMATE (1e-14 vs 1e-13, × 3), not a bound.

## The accepts: all 147 survive as robust (a constructor finding)
- **D8 = CONNECTION** with n_accept 147 and n_chord_accept 0. D8's thin = true comes from the thin REJECTS in its
  input list, not from the accepts.
- **Each of the 147 accepts** was thin at the run tolerance, and each is:
  - accepted again at 1e-14;
  - NOT thin at 1e-14;
  - not on a chord.
- **Angles:** 0.010017 to 0.04586. The smallest margin above 0.01 is 1.70e-5; the largest change in an angle between
  the run and 1e-14 is 7.6e-9, about 2000× below that margin.
- **Error measurement:** 81 of the 147 have measured errors. The other 66 lie beyond the G4 range ("error unmeasured"),
  so their robustness rests on an extrapolated error.
- **Crossing indices** run from 4091 to 8913.
- **What this says:** at the registered floating-point margin standard (an ESTIMATE, not a bound), the constructor's
  candidate connections are not artefacts of a thin decision. They are candidates for steps 3–4, which remain
  unimplemented. Nothing here is a rigorous covering, and nothing says whether ρ > 1.

## What the registered rule gives
- Step 2's outcome under G6 is **UNRESOLVED**: 6023 thin crossing decisions and 203,299 thin near-miss decisions. It
  is not decided either way.
- That holds even though the accept/CONNECTION side is robust. The unresolved decisions are all rejects or red flags,
  which bear on the B15 prediction about red flags; they do not bear on whether a connection exists.
- Whether the prereg wants step 2 read per decision type, or as one outcome, is for the Bridge. I have not re-read it
  to suit the result.
