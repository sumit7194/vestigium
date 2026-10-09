# Pre-registration — Lean-verified certificate arithmetic (item 2), 2026-10-10

**Committed before any export code or Lean code for this stage.** User decision, relayed by the bridge: GO, with
the words *"we should always do such checks, dont worry about time"*. The bridge endorsed the division-free design
on 2026-10-10.

## What changes, in one line

Today **Lean** checks the logic (L6_gl2 / L6_not_virtually_abelian: hypotheses ⇒ G⁰ not virtually abelian) and
**Arb** checks the numbers (the certificate inequalities, on balls). After this stage, **the certificate
inequalities themselves are decided by the Lean kernel**, from exported exact rational boxes. The only numerical
step left outside Lean is "the box contains the true monodromy matrix" (the ODE enclosure).

## Scope: every certificate behind a committed OBSTRUCTION or CORROBORATED verdict

| family | verdict record | certificates | GL(2) boxes (v2) | SL(2)-route boxes (v1) |
|---|---|---|---|---|
| MN axial | PREREG_mn_axis_certified_monodromy (2ce8b41, A5) and the v2 VREPRO ladder rows | 4 rows | 4 (VREPRO) | 4 (the A5 verdict certificates) |
| MN equatorial v2 | PREREG_mn_equatorial_v2 FINAL (5da26fe) | 6 rows | 6 | 6 (N=100 for rows 0, 2, 3; N=140 for rows 1, 4, 5, as certified) |
| TS δ=2 v2 | PREREG_ts2_v2 (00cc44a) | 6 rows | 6 | 6 (N=100) |
| TS chaos levels | PREREG_ts2_chaos_levels (1b8c3f5) | 8 rows | 8 | 8 (N=100; N=140 for rows 6, 7, as certified) |
| **total** | | **24 rows** | **24** | **24** |

The TS 2b′ route is algebraic (Kovacic) and is not in scope.

## Regeneration and the export gate

The certificate JSONs store trace midrads, not matrix entries. So each certifying loop is **recomputed with the
same frozen code, geometry, precision and Taylor order**, and the products g, h are exported.
- **Gate (bit-for-bit):** the recomputed tr²/det(g), tr²/det(h) and tr[g,h] (or tr g, tr h, tr[g,h] for v1) must
  reproduce the **recorded midrad strings exactly**.
- If any differs, that certificate is **not exported**, and the stage reports a determinism failure for it.
  Nothing is re-tuned.

**Export format (exact).** Each entry of g and h is an Arb complex ball (re ± r, im ± r).
- Its real and imaginary rectangles are exported as **exact dyadic rationals**: lo = mid − rad and hi = mid + rad,
  each written as an integer pair (m, e) meaning m·2^e.
- These are computed in integer arithmetic from Arb's exact (mantissa, exponent) for the midpoint and the radius.
  The rectangle therefore contains the ball exactly, with no rounding.
- One JSON per certificate, `lean_export/<family>_<row>_<v1|v2>.json`. The JSON is turned mechanically into a
  Lean file of ℚ literals.
- **A Python cross-check, committed:** the rationals are read back into Arb, and the original ball must be
  contained in the rectangle.

## Lean side (in `lean/ZiglinCert`)

- **Rational boxes.** `QBox` (lo, hi : ℚ) with membership via the cast ℚ → ℝ; `CBox` (re, im : QBox). There are
  interval operations add, sub, neg, mul (min/max of the four products) and complex multiplication and conjugation
  built from them. Each comes with a **soundness lemma** (x ∈ A, y ∈ B ⇒ x op y ∈ A op B).
- **Division-free criteria** (bridge-endorsed), evaluated on boxes:
  - **(I) for each of G and H:** Im(tr²·conj det) ≠ 0, OR Re(tr²·conj det) < 0, OR Re(tr²·conj det) > 4|det|².
    Lemma: **each disjunct alone implies det ≠ 0**, and the disjunction ⇔ ¬InRealSegment(tr²/det, 0, 4).
  - **(II)** tr(G·H·adj G·adj H) − 2·det G·det H ≠ 0. Lemma: given det ≠ 0, (II) ⇔ (G H G⁻¹ H⁻¹).trace ≠ 2.
- **Bridging theorem.** If `check BG BH = true`, then for EVERY pair G ∈ BG, H ∈ BH: G and H are invertible and the
  L6_gl2 conclusion holds for the units they define. That is: for every k ≥ 1, no subgroup of finite relative
  index in ⟨G^k, H^k⟩ is abelian.
- The same check is used for the v1 boxes. The true v1 matrices have det = 1, but the box check does not assume
  it; it is strictly stronger than the SL(2) form.
- **Decision procedure:** kernel `decide` on the Boolean `check`. **No `native_decide`, no `sorry`.**
  `#print axioms` for every certificate theorem must show only propext, Classical.choice, Quot.sound.
- If kernel evaluation of some certificate is infeasible (time or memory), that certificate is reported
  **"not kernel-checked"**. There is no fallback to native_decide without a new decision.

## Controls (each must be shown to FIRE)

1. **Perturbation poison.** For one real certificate, widen one entry's box until tr²/det(G) can reach the real
   segment [0, 4]. `check` must return **false**. The same for a box whose commutator range reaches 2.
2. **Integrable control.** Kerr-WP monodromy boxes for two loops (TS chaos stage control level, v2 pipeline).
   Kerr's G⁰ is abelian, so `check` must return **false** (the commutator is 2, up to the enclosure).
3. **Lean soundness spot-check.** For one certificate, the Lean box evaluation of tr[g,h] must contain the Arb
   midpoint. This is reported, not a gate.

## Verdict wording

Per certificate:
- **LEAN-CHECKED:** "the Lean kernel verifies that every pair of 2×2 complex matrices in the exported boxes
  satisfies the L6_gl2 hypotheses, hence its conclusion";
- or **not kernel-checked** (reason);
- or **export gate failed** (reason).

**Still OUTSIDE Lean, stated with every result:**
- that the box encloses the true monodromy matrix: the Arb/Taylor ODE enclosure, the tail bounds, and the Rust
  (v2) and Python (v1) integrators;
- the NVE derivation from the metric (symbolic);
- the cited Morales–Ramis / Ziglin theorem and the finite-index fact (G⁰ ⊆ G of finite index);
- the export code, which is mitigated by the committed read-back cross-check.

## Resources and order

- ≤ 3 threads, guarded and detached, coordinating with ansatz's scans.
- Order: cheapest first. TS (minutes), then MN axial (about 1–2 min each), then the MN equatorial v2 certifying
  loops, then the MN equatorial v1 replays (N=100 about 3 h each; N=140 3–6 h each, a 12 h guard).
- Each certificate's export is committed as soon as it passes its gate, so a reboot loses at most one run.
- Lean uses the existing toolchain; the disk guard is 4 GB.

## Setup correspondence: is the run testing the claim it will be quoted for?

**Claim to be quoted:** "the numerical certificate inequalities behind the MN and TS obstruction verdicts are
verified by the Lean kernel."

**Condition tested:** Lean decides the division-free criteria on boxes **regenerated** by the frozen code, gated by
bit-for-bit reproduction of the recorded traces. This matches the claim **for exactly the certificates whose gate
passes.** A certificate that fails its gate is reported as such and is not covered.

**Gap:** the boxes are only as trustworthy as the enclosure that produced them, and that stays outside Lean, by
design and stated.

## DISCLOSURE (2026-10-10): export gate failures on tschaos rows 1 and 4, diagnosis, and an exporter fix (post-failure)

**What failed.** For tschaos rows 1 and 4 (v1 and v2), the regenerated certificates were valid (`certificate_ok`)
and agreed with the record at every midpoint digit, but **radii differed in the 4th significant digit**, for example
1.5275e−26 vs 1.5276e−26. Per the gate, **nothing was exported for them.**

**Diagnosis, demonstrated rather than assumed.**
1. `locate_a6` is bitwise deterministic within a process: 4 repeated runs agree exactly.
2. The regeneration reproduces itself exactly across fresh processes.
3. **Hash seed is not the cause:** the compiled forms are identical under PYTHONHASHSEED = 0…3.
4. **The cause is hidden global state.** `locate_a6` refines roots with `mp.findroot`, which uses the process-global
   `mpmath.mp.dps`. The recorded TS chaos-levels run (`mr_ts2_chaos.run_row`) located its singular points AFTER
   `gates()` had set `mp.mp.dps = 60`. The exporter ran at the default dps = 15. **With dps = 60 set first, the row-1
   regeneration matches the record BIT-FOR-BIT.**

**Fix (exporter only; the gate is unchanged and still bit-for-bit).** For the tschaos family, the exporter
reproduces the recorded process state (`mpmath.mp.dps = 60` before locating). This replicates the recorded
computation; no parameter was chosen to make the gate pass.
- It is labelled **post-failure**, because it was found through a gate failure.
- Rows 1 and 4 are re-exported under it at the end of the batch. Other families' recorded runs never ran
  `gates()` before locating, so the default precision is the right state for them, and they pass as they are.

**Recorded as a reproducibility hazard of the frozen pipeline** (not a rigour issue): the singular-point list,
which only steers step sizes, depends on mpmath's global precision as left by earlier code in the same process.
Every enclosure stays valid whatever the list is. Only bit-for-bit reproduction depends on it.
