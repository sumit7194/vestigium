# B15d DRAFT (2026-11-21): the rigorous stage on Kerr, with fixed sets on the arm's chain

**Status: DRAFT for the Bridge's review. Nothing has run.** Proposed by the Bridge after B15c (B15C_RESULT.md: B15
prediction NOT TESTED; no chain reached hs_cover). Drafted by Claude Opus 5.5 (session "Quantum").

**What it tests.** Rigorous hs_cover on integrable Kerr data, in two respects:
- **Soundness:** it must never certify a false covering. F7 applies unchanged: any ρ > 1 STOPS the MN claim.
- **Decidability:** whether hs_cover can decide coverings at all across the long Kerr homoclinic swing (out to r = 46.8M).

It is explicitly a test of the rigorous stage, not of the frozen constructor. The chain comes from the UNFROZEN
diagnostic arm, and the sets are fixed here instead of chosen by the sampled ladder.

## 1. The chain
- **Source.** The arm's refined orbit (horseshoe_results/kerr/b15c/ARM.json, committed 73230b5):
  - X_0 … X_6 (m = 6) and U_j, the propagated W^u tangents;
  - the saddle z with e_u and e_s.
- It lies on the separatrix level set: |Q(X_j) − Q_s| ≤ 2.8e−10 relative.

## 2. A finding that shapes the sets: the B14 frames are numerically singular on Kerr
- Along the arm's chain, the B14 frame (U_j, S_j) has |sin∠(U_j, S_j)| equal to:

  | j | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | sin∠(U_j, S_j) | 1.9e−3 | 5.3e−7 | 3.7e−10 | 2.6e−10 | 6.0e−11 | 5.7e−8 | 2.2e−4 |

- This is integrability itself: W^u = W^s, so the two tangents are parallel up to noise.
- With |U| = a = 0.01, the transverse extent of N_2 … N_4 is ~1e−12. That is below the registered 1e−10
  rationalisation, so the exact sets would be artefacts of rounding.
- **B14 frames are therefore NOT proposed for B15d.** They are recorded as a finding (it also bears on B15c's reading:
  sampled covers on such slivers are uninformative).

## 3. Sets (fixed now)
**Frames:**
- **N0:** B14's own frame at the saddle, (a0 e_u, (b0/a0)·a0·e_s). It is well conditioned, sin∠(e_u, e_s) = 0.031.
- **Chain sets, an orthonormal frame:** U_j as above (unit), and **S_j^⊥ = U_j rotated by +90°**. So
  N_j = (X_j, a·U_j, (b/a)·a·S_j^⊥).

**Sizes:** HH-SECONDARY's ladder entry (a0, a, b0/a0, b/a) = (0.03, 0.01, 0.5, 0.5), fixed. There is no ladder.

**Chain:** the B14 rule (hs_construct_hh_chain2.py) applied to these frames and sizes. It is the contiguous run
j₁…j₂ ⊂ {1 … m−1} of orbit points whose sets are disjoint from N0 and from each other.
- If no such run exists, B15d stops at "no chain". It is recorded as NOT TESTED, with no fallback.

**Coverings (B14):**
- required: N0⇒N0, N0⇒N_{j₁}, N_j⇒N_{j+1} and N_{j₂}⇒N0;
- optional: N_{j₂}⇒N_{j₁}.

**Exact sets:**
- rationals rounded to 1e−10, as in hh2;
- S8 must hold exactly, or B15d stops at "S8" (NOT TESTED);
- a singular exact frame stops it at "singular frame".

**What the orthonormal frame means physically:**
- Along S^⊥ the sets cross the separatrix level set. On one side lie the bounded orbits; the other side includes
  orbits that plunge, which hs_cover's S4 domain check fails closed.
- So UNDECIDED pieces are expected. A certified failure needs only one certified leaf or orientation contradiction (the
  B15c-1 rule).

## 4. The rigorous run
- **Spec, as B15c §4:**
  - `system mn` at the B15 level (k 39, α −5/8, β 0, E 49/50, L 445/2);
  - prec 128, order 20, iter 1;
  - caps 65536 4096, depth 16 12, `cover x y 16 16 64`;
  - checkpoints; S4 and S9 on; no piececap (B16).
- **Classes:** the B15c / B15c-1 classifier, unchanged (CERTIFIED / CERTIFIED-FAIL / UNDECIDED / HARNESS-ERROR). All
  required and optional coverings run, even after a CERTIFIED-FAIL, so that decidability is measured.
- **Gates and controls before the counted coverings** (B15c §4 and §6.3, unchanged):
  - **gate GB:** the fresh guarded hs_cover build reproduces the R1 generic Rössler COVER lines and HH-SECONDARY's N0⇒N0
    line exactly;
  - **control 3's rigorous twin:** HH-SECONDARY's CERTIFIED sets with U ↔ S, and with U rotated 90° (W2 fallback if
    singular), must each be CERTIFIED-FAIL in ≥ 1 required covering. UNDECIDED means "control not decided", and B15d
    waits.

## 5. Prediction and reading (registered before the run)
- **Prediction:** NOT ρ > 1, and CERTIFIED-FAIL in at least one required covering.
- **Readings:**
  - **ρ > 1:** F7 STOP. This would be a soundness failure of the rigorous stage, or a physics error, and is treated as the
    STOP rule requires.
  - **CERTIFIED-FAIL** in ≥ 1 required covering: **the B15 prediction is supported, by a rigorous test on Kerr.** It is
    reported as "B15d: rigorous stage certified a failure on integrable Kerr data (unfrozen-derived chain)". It is not a
    test of the frozen constructor.
  - **UNDECIDED** on every required covering: **"tool limit on Kerr"**. This is NOT support. It is reported with the
    per-covering leaf and fail counts, the piece failure reasons (S4/S9/enclosure), and the return times. That
    decidability record is a direct input to the MN covering plans.
- **The headline gives** per covering: class, leaves, fails, certified fails, orient_certified_fail, return time, replay
  steps and wall time.

## 6. Resources and order
- **Order:** gate GB, then the HH twin (2 coverings × 2 variants; HH's coverings took 17–80 min each in hh2), then
  B15d's coverings: L + 2 required for a chain of length L (3 to 7), plus 1 optional.
- **Compute:** at most 4 hs_cover processes at once, nice 10, one guard each (RSS cap 1 GB, disk < 5 GB at once). Wall
  time for Kerr returns is unknown; B16 sets no cap. Everything is checkpointed and detached.
- **This draft carries the slot request** for up to 4 cores, staggered with the other sisters as the Bridge decides.
- **Expected disk:** small (hh2's checkpoints were 268 KB in total).
