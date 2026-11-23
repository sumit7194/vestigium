# OnlyKerr: machine-checked glue for the "Only Kerr" argument

Written by Claude Opus 5.5 (session "Quantum") on 2026-11-21, at the Bridge's request for Sumit.

This adds a Lean 4 file, `Glue.lean`, checked against Mathlib. It re-runs **no numerics**. Certified numeric facts enter only
as one clearly named hypothesis. Lean checks the exact algebra and the logic that joins the pieces.

## Build
- **Command:** `lake build OnlyKerr`, in `lean/ZiglinCert` (toolchain leanprover/lean4:v4.35.0-rc3, Mathlib v4.35.0-rc3).
  Run with LEAN_NUM_THREADS=2 at nice 10.
- **Log:** `lake_build.log`. It shows exit 0 and a peak memory footprint of about 170 MB.
  - Narrowed imports keep RSS at about 2.7 GB for a standalone `lean` run.
  - The warnings in the log are Mathlib style lints only: line length, and doc-string placement.
- **No sorry.** `Axioms.lean` prints the axioms behind all 16 main theorems. Each depends only on Lean's standard
  `propext`, `Classical.choice` and `Quot.sound`: no `sorryAx`, no custom axioms, no `native_decide`.

## What is machine-checked (exact, no hypotheses beyond those stated)
| Item | Theorem | Statement |
|---|---|---|
| 1a | `elim_identity` | With z = 1+iy, D = z²+a², S = y²+1−a², f0 = (z²−2z+a²)/D, c0 = −H/D, G1 = E²(f0²+c0²) − f0 and t = 1/E²: D²·G1/E² = (1−t)S² + 2tS + H² + 2iytS. For real a, y, E ≠ 0, complex H and D ≠ 0. |
| 1b | `curzon_tr_h1`, `curzon_tr_h2`, `curzon_tr_comm` | Take M0 = [[1,1],[0,1]], M_a = [[u, −(1+u²)/τ],[τ, −u]], g_k = M0ᵏ M_a M0⁻ᵏ (k = 0,1,2), h1 = g0 g1 and h2 = g0 g2. Then: tr h1 = −2−τ², tr h2 = −2−4τ², and tr(h1 h2 h1⁻¹ h2⁻¹) − 2 = −4τ⁶. This holds over any field, for τ ≠ 0. The file also proves that M0i = M0⁻¹, that det M_a = det h1 = det h2 = 1, and that the inverse used is the true inverse. |
| 2 | `glue_min_pos`, `glue_re_pos`, `re_pos`, `G1_ne_zero` | For a ∈ (0,1), real y, t ∈ (0,1] and complex H satisfying `CertCases`: min(S², 2S) + H_r² − H_i² > 0, and Re[(1−t)S² + 2tS + H² + 2iytS] > 0. Chained with 1a (t = 1/E², E² ≥ 1, D ≠ 0): Re(D²G1/E²) > 0, hence **G1 ≠ 0**. Also checked: the convexity step (1−t)S² + 2tS ≥ min(S², 2S), S > 0 for a < 1, and S ≥ 1 when \|y\| ≥ a. |
| 2 | `rescale_case1`, `rescale_case2b`, `rescale_case2a` | The certificates are stated for H~ = H/a and H~_θ = H/(a√(1+s)), which are positive real rescalings. Each certified inequality is equivalent to the same statement about H: Re((H/c)²) > 0 ⇔ Re(H²) > 0; \|Im(H/c)\| < Re(H/c) ⇔ \|Im H\| < Re H; \|Im(H/a)\| < 1 ⇔ \|Im H\| < a. |
| 3a | `k5_3a` | For integer m with \|m\| ≥ 2: 3m²/(3m²−4) ≤ 3/2. |
| 3b | `k5_3b`, `k5_3b'` | For complex η with \|η\| ≤ 1/15: \|2η + η²\| ≤ 31/225. Also (3/2)(31/225) = 31/150. |
| 3c | `k5_3c` | r = 323/2400 satisfies (1/2)(31/150 + r²) ≤ r, and r < 1 (the invariant-ball condition). |
| 3d | `k5_3d` | exp(π√2 (1 − 323/2400)) > 46. Proved from Mathlib's π > 3.141592, e > 2.7182818283 and exp y ≥ 1 + y + y²/2. The margin in the exponent is about 3e−5, and the result has margin about 0.5 (46.50 > 46). The true value is about 46.756. |

## What enters as a HYPOTHESIS (not proved in Lean)
- **`CertCases a y H`** stands in for the T19 interval certificates. [Corrected 2026-11-23, after the Bridge's
  faithfulness read; the earlier wording said "at each (a, y)" and "cover every (k, y)".] H depends on a, y, k, E and
  s = 30/7 − k (θ = 1/(1+s)). For every a ∈ (0,1), every k < 30/7, every E > 1 and every real y, the value H at those
  parameters satisfies at least one of the following. `CertCases` itself drops the k and region labels: it is the
  bare disjunction, which is a weaker hypothesis than the labelled cases.
  - Case 1 (k ≤ 0, any y): Re(H²) > 0;
  - Case 2b (0 < k < 30/7, \|y\| < a): Re H > \|Im H\|;
  - Case 2a (0 < k < 30/7, \|y\| ≥ a): \|Im H\| < a.
- **Two facts are trusted to the certificates and their own audit, not to Lean:**
  - that the three cases cover every k < 30/7 and every real y (k < 30/7 is the theorem's allowed range, from Neon
    T14's U_a separation; k ≥ 30/7 is outside the claim, not a gap);
  - that each certified inequality holds on its region.
- **Item 3** is pure arithmetic, with nothing assumed.

## Not covered
- The interval certificates themselves.
- The physics derivation of H, f0 and c0 from the metric.
- The analytic steps of the Only-Kerr theorem outside these identities and inequalities.

## Note (history, not Lean)
The original K5 multiplier bound "> 28" was false at \|m\| = 2 (the value is 27.9988). The referee caught it (T24), and
the T28 repair uses r = 323/2400. `k5_3d` checks the repaired bound.

## Corrections and additions (2026-11-23, after the Bridge's faithfulness read, Layer 1)
Read: TheBridge/fleet/lean_reads/OnlyKerr_faithfulness_2026-11-23.md. No proof gap and no hidden axiom were found;
the corrections below are wording only.
- **Which rescaling each case uses.** T19 writes H = a√(1+s)·H~_θ with θ = 1/(1+s), so H/a = θ^(-1/2)·H~_θ.
  - Case 1 and Case 2b are certified on H~_θ itself, so they transfer with c = a√(1+s) > 0 (`rescale_case1`,
    `rescale_case2b`, valid for any c > 0).
  - Case 2a is certified as θ^(-1/2)·|Im H~_θ| < 1, which is exactly |Im(H/a)| < 1, so it transfers with c = a
    (`rescale_case2a`).
  - The identity H = a√(1+s)·H~_θ is T19's definition, implemented in the Bridge's V26-K harness. Lean takes H as
    given and does not derive it. Chaining a certificate into `CertCases` is done by hand.
- **Provenance of the certificates.** They were produced by Neon T19 (Gemini, 2026-11-21; Neon marked them unverified). They were verified
  independently by the Bridge, V26 Addendum K (TheBridge/falsification/V26_single_centre_lower_axis/FINDINGS.md):
  - K0, K1, K3A, K3B, K4 and K5 PASS.
  - The Case-2a check K2 FAILED as registered (enclosure blow-up). The labelled amendment K2′ PASSED with a thin
    margin (certified maximum ≤ 0.99937 < 1).
  - The tails and the inherited holomorphy were read by hand, not certified.
  - Quantum (this file's author) did not check T19; `Glue.lean` only assumes it.
- **`hD` is not a restriction.** D = (1+iy)² + a² = (1 − y² + a²) + 2iy vanishes only if y = 0 and 1 + a² = 0,
  which is impossible for real a. So `hD : D ≠ 0` holds for all real a and y.
- **Memory.** "Peak memory footprint about 170 MB" was the wrong figure. `lake_build.log` shows a maximum resident
  set size of 2,448,539,648 bytes (about 2.45 GB).
- **The build log is a cached replay.** The `lake_build.log` here replayed cached results. A fresh elaboration ran on 2026-11-23
  (`lean_export/build_nonempty_2026-11-23.log`).
- **Axiom audit extended.** `Axioms.lean` now also prints the axioms of `M0_inv`, `g1_conj` and `g2_conj`. In the fresh build, all
  19 depend only on [propext, Classical.choice, Quot.sound].
- **Comment left unchanged.** The doc comment above `CertCases` in `Glue.lean` still says "The certificates cover
  every (k, y)". Read it as "every k < 30/7 and every real y". It was left unedited so that the read file keeps its
  hash.
