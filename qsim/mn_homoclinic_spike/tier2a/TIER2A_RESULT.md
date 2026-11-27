# Tier 2a result: AGREE. The MN field was re-derived independently from the published metric, and it matches the S2 header and the Melnikov module

Run 2026-11-27, comparison at about 22:45 IST. Registration: TIER2A_PREREG.md (0d35da2 + dd0f190). The harness was frozen
before the independent module was seen (34416e6). Written by Claude Opus 5.5 (office "Quantum"). Compute: about 6 core-s.

## Verdict: AGREE (every registered rule is met)
- **The independent side** is indep/mn_indep.py, sha256 7a76e05c…, frozen 22:32:03 IST.
  - It was written by a fresh subagent that had not seen mn_codegen.
  - Its source is Gair, Li & Mandel, PRD 77 024035, arXiv:0708.0628v2 §II, eqs. (2)–(5), read in the PDF and in the
    LaTeX source.
  - It uses mpmath only, with no CAS. The t–φ block is inverted as an exact 2 × 2 inverse, and the derivatives come
    from mpmath.diff.
- **Its self-checks all pass** (indep/selfcheck_output.txt):
  - Boyer–Lindquist Kerr at β = 0, at 12 points: worst 5.5e−60;
  - the asymptotics give M = 5, J = 15, ω → 0;
  - the mass quadrupole M₂ − M₂(Kerr) = −k³β, measured from the axis Ernst potential (M₂ = −46.92 at β = 0.03);
  - the vacuum Einstein equations hold, with residuals ≤ 6e−61 at β = 0, 0.03 and 0.5.

| Comparison (97 points) | worst |indep − ref| / S_c | outside tolerance (1e−20) |
|---|---|---|
| S2 header gen/mn_field.h (4c1c7b57), β = 0: H, V, f0–f3 | 3.8e−46 | 0 |
| S2 header, β = +3/100 | 4.4e−46 | 0 |
| S2 header, β = −3/100 | 3.3e−46 | 0 |
| mel_gen.H0 (β = 0) | 9.5e−56 | 0 |
| mel_gen.Hb (∂/∂β at 0; Step A's L2 source) | 7.4e−56 | 0 |
| **must-fail mf1:** sab header (3β² G term dropped), β = 3/100 | 4.7e−7 (H) … 7.3e−5 (f2) | 87–97 per component: **FIRED** |
| **must-fail mf2:** L → 1.001L | 1.8e−3 … 6.6e−2 | 87–97: **FIRED** |

- The agreement sits at the header's own MPFR-160 floor (about 1e−47).
- The must-fail signals are about 39 orders of magnitude larger.
- V is (correctly) blind to the sabotage, because the G term enters only g_xx and g_yy.

## Findings
1. **A typo in the source, resolved the same way on both sides, separately.**
   - The agent found that GLM eq. (3h), as typeset, puts the "−2" inside the ℓ-sum (subtracting 6β). It applied the
     −2 once, because only that reading makes γ′ vanish on the axis and at infinity.
   - Our mn_codegen writes 2β Σ(… − 2) + 8β, which is the same thing: −12β + 8β = −4β = 2β·(−2).
   - The agreement confirms that the S2 and Melnikov fields use the physically correct reading. The literal reading
     would rescale g_xx and g_yy by e^{−8β}.
2. **Rotation sense and gauge:** α = −1/3 (eq. 5 with χ = +0.6) and S₁ = +15. These are our conventions; no
   relabelling was needed (no CONVENTION FINDING).

## Disclosures
- **The isolation was by instruction.** The agent reports that it opened no repository file outside tier2a/indep/.
  The full list is in its report and copied below.
- **It saw two things automatically.** Its session context included the git status and recent commit messages. These
  name "gen/mn_field.h" and say that the must-fail case drops "the 3β² G term". The agent says it did not act on this
  and took the β² term from eq. (3h). No field expressions were in that context.
- **Manko & Novikov 1992** could not be obtained (paywalled), so GLM 2008 is the only source.
- **The files it opened:**
  - its own indep/ directory;
  - the arXiv PDF and LaTeX e-print, in the session's tool-results and scratch;
  - mpmath source lines quoted by two of its own tracebacks (venv; not opened).

## Consequence
- **(H1) is discharged for S2 and for Step A.** "The MN field was re-derived independently from the published metric
  (Gair–Li–Mandel 2008) by a non-author, and agrees with the field both proofs used, to its 160-bit precision, at 97
  orbit points and three β values."
- **What remains single-implementation:** the flow and derivative enclosures (CAPD; Tier 2b, not done) and the
  Melnikov integrals (Arb; certified, single implementation).
