# Report

*Rule IX: every experiment gets an entry. If it is not here, it did not happen.*

Required fields per entry:

    ## EXP-NNN  <short title>
    **Goal**            what problem is this solving
    **Hypothesis**      why should this approach work
    **Method**          the mathematics, with notation defined before use (M2)
    **Implementation**  files and lines changed
    **Results**         table: method, instance, metric, delta
    **Analysis**        why it worked or did not; what it reveals
    **Grade**           verified / partially verified / unverified
    **Next steps**      what to try based on this

---

## EXP-001  Prior-art sweep, verification of TASK.md, and measurement of the disagreement

**Date** 2026-09-04. **Status** complete; no derivation started (per instruction).

**Goal** (1) Establish what is known about the near-universality of a(θ)/C_T, with verified
citations; (2) decide outcome F (already explained?); (3) verify every factual claim in TASK.md;
(4) measure the size, sign and angle-dependence of the inter-theory deviations, with error bars.

**Hypothesis** None to test; this is the M1 gate. The working expectation going in was TASK.md's:
a collapse across five theory classes, a nearly-saturated bound, no explanation. Two of those
three survive unchanged; the third ("five theory classes") does not.

**Method** Citation verification against the arXiv API and full texts (ar5iv/arXiv HTML) for every
paper used; see `references.md` (30 entries, 17 read in full). Numerical: my own evaluation of the
Einstein-gravity corner function from [HT07] eqs (5.1)-(5.5) and of the SSA bound [BWK16] eq (II.2),
both validated against independent published spot values before use; the ECG family from
[BCV21] eq (293); free-field values taken from [CHL09] Table 1 and [HHCWM16] Tables 1-4 (never
inferred). Notation (M2): θ ∈ (0,π) the opening angle; a(θ) the coefficient of −log(H/δ) per
corner in the von Neumann entropy; a_n(θ) the Rényi analogue; σ, σ', σ'', σ^{(p)} the coefficients
of (θ−π)^2, (θ−π)^4, (θ−π)^6, (θ−π)^{2p+2} in the smooth-limit expansion; κ the coefficient of 1/θ
as θ→0; C_T the stress-tensor two-point normalisation in the Osborn-Petkou convention used by
[BMW15], for which C_T = 3/(32π²) per real scalar and 3/(16π²) per two-component Dirac fermion;
t_4 the parity-even stress-tensor three-point parameter, −4 ≤ t_4 ≤ 4.

**Implementation**
- `scripts/exp001_measure.py`: holographic curve (via the substitution z = g₀t that removes the
  width-g₀ peak; g₀ → 0 is the smooth limit, g₀ → ∞ the sharp one), the bound, the free-field
  tables, the `../quantum` comparison. Controls: σ/C_T → π²/24 (rel. err. 1e-5 at θ = π−10⁻³),
  κ/C_T → π²Γ(3/4)⁴/6 (rel. err. 3e-7), a_E(π/2)/C_T = 1.2220 and a_E(3π/4)/C_T = 0.2642 vs
  [BWK16] Table 1 (1.222, 0.264), and the [CHL09]-normalised s_H(π/2) = 0.02321, s_H(3π/4) =
  0.005019, κ_H = 0.0705 vs their 0.02321, 0.005019, 0.0704. All passed before any number below
  was read off.
- `scripts/exp001_coefficients.py`: order-by-order decomposition, O(N) normalisation, Rényi-2 data.
- `scripts/exp001_ecg.py`: ECG curve at all angles; controls σ_ECG/σ_E = 1−3μ and
  κ_ECG/κ_E = 1−123μ/20 reproduced to 6 digits at both ends of the allowed μ range; the
  σ-κ trial function and its slope.
- Outputs frozen in `scripts/exp001_output.txt`. Verified bibliography in `references.md`.

**Results**

*R1. What is known (chronology, all verified).* Free scalar a(θ) as the solution of nonlinear ODEs,
values at π/4, π/2, 3π/4, and κ ≈ 0.039 per real scalar [CH07]. Holographic (Einstein) f(Ω) in
closed parametric form, convexity/monotonicity from SSA, κ_E ∝ Γ(3/4)⁴ [HT07]. Dirac fermion
[CHL09], whose Table 1 and text already record the near-collapse *before normalisation by C_T*:
"maximal relative difference between the scalar and Dirac case of 9%", holographic-vs-Dirac
"only 2.5%", both maximal at θ → 0, and the theorem-level statement that the σ's of the complex
scalar and the Dirac fermion coincide (both 1/128). [BMW15] added the C_T normalisation, the
numbers 13% (scalar) / 2.5% (fermion) for the maximal deviation from holography, the O(N)
points at π/2, the conjecture σ/C_T = π²/24, and the observation that the deviation ratio is
monotonically decreasing in θ. [BM15] showed that R², f(R) and generalised-Lovelock corrections in
AdS₄ multiply a(θ) and C_T by the *same* constant, so a(θ)/C_T is *identically* the Einstein
function for that family. [Miao15] proved σ/C_T = π²/24 for general perturbative higher-curvature
duals and showed κ/C_T is not universal and that the Einstein curve is not a lower bound. [FLP16]
proved σ = π²C_T/24 for all 3d CFTs (second-order shape dependence of S_EE is non-locally ∝ C_T);
[BMMS16] gave the defect-CFT (displacement-operator) form of the same statement. [EH15] proved
σ_scalar = 1/256, σ_fermion = 1/128 exactly and that σ_n/C_T is *not* universal for n ≠ 1.
[BWK16] derived a(θ) ≥ 𝔞_min(θ) = (π²C_T/3) log[1/sin(θ/2)] from the SSA-plus-Lorentz inequality
a'' ≥ −a'/sinθ of [CHL09]; showed σ' is not a function of C_T and t_4 alone; gave the exact
Einstein σ^{(p)}/C_T through p = 5; and observed σ^{(p)} → 2κ/π^{2p+3} (radius of convergence π).
[HHCWM16] gave lattice and field-theory values at seven angles for boson and fermion, α = 1..4, the
exact σ' for free fields, an improved ansatz, and "near collapse" across α. [WWS17]: at N = ∞ the
Wilson-Fisher corner function is *exactly* N times the free-scalar one (the geometry-induced
mass does not affect the n → 1 limit in the infinite plane), so the WF/free-scalar agreement is
trivial at leading order in 1/N. [BCV21]: cubic curvature terms are the first that change the
*shape*; for Einsteinian cubic gravity across the full t_4-allowed coupling range the curve stays
within about 1% of Einstein and lies *below* it for t_4 > 0; the σ-κ trial function reproduces
every known curve to ≤ 1.2%. [LSZM24], [NCRCLM26]: precise QMC corner coefficients for O(3) and
Ising, but for the *second Rényi* entropy.

*R2. Outcome F: NOT resolved in the literature.* Every source treats the near-universality as an
observation. [BWK16]: "Little is known about a(θ) beyond [the θ→π] limit." [BCV21] (2021) still
calls it "the observation/conjecture of [BMW15]". Searches through September 2026 (terms:
corner entanglement universality explanation, modular Hamiltonian, bootstrap, strip coefficient
bound, Chern-Simons matter corners, fuzzy sphere corners) found no paper claiming a mechanism.
Grade: **verified** to the extent a negative literature result can be.

*R3. TASK.md claims, checked.*
| claim in TASK.md | verdict |
|---|---|
| a(π/2) ≥ (π² ln2/6) C_T is a proven bound | **verified** [BWK16] eq (II.4); general form 𝔞_min(θ) = (π²C_T/3) log[1/sin(θ/2)]; it is the equality case of a'' ≥ −a'/sinθ, and it is *not* the corner function of any CFT (diverges only logarithmically) |
| "all known theories nearly saturate it" | **partially verified**: true only near π/2 and above. Excess over the bound at π/2: Einstein 7.2%, ECG 6.9–7.5%, fermion 7.5%, scalar 9.2%, WF 14 ± 9%. At 26.6° the bound is 4.84 against true values 7.5–8.2 (36–41% below). At π the bound is saturated by construction. |
| "a family of higher-curvature holographic models" collapses | **wrong as evidence**: for the [BM15] family the ratio is *identically* Einstein's (both a and C_T rescale by the same factor); this is not an independent theory landing on the curve. The only family with a different shape is cubic gravity [BCV21], where the allowed range gives ±0.9% at 26.6°, ±0.3% at π/2. |
| free scalar, free fermion, holography agree "nearly" | **verified and quantified** (R4): scalar +12.7% at θ→0 falling to +0.4% at 135°; fermion +2.5% → +0.05%. |
| Wilson-Fisher O(N), N = 1,2,3, collapse | **partially verified only**: one angle (π/2), error ±8–10%, values quoted as 1.36(14), 1.3(1), 1.3(1) by [BMW15]/[BWK16]. The underlying a₁(π/2) for Ising is not printed in the cited source [KHSM13] (whose in-text order-26 value 0.0140 would give 1.56); the ratio is therefore taken on the authority of [BMW15]. See R6 for why this data carries no information about the collapse. |
| θ→π limit a ≃ σ(π−θ)², σ = π²C_T/24 | **verified** (theorem, [FLP16]; holographic proof [Miao15]) |
| θ→0 limit a ≃ κ/θ | **verified**; κ = 0.0397 (real scalar), 0.0722 (Dirac) [CHL09] Table 1; κ_E/C_T = π²Γ(3/4)⁴/6 = 3.7092 |
| "exact values for the free scalar and free fermion where they exist" | exact closed forms exist only for σ (1/256, 1/128) [EH15] and σ' ((20+3π²)/(9216π²) per complex scalar, (16+3π²)/(9216π²) per Dirac) [HHCWM16]; a(π/2) etc. are 4-digit numerics from the ODE system; κ is an integral of the 2d entropic c-function [CH07] |
| Tier-2 constraints (positivity, monotonicity, convexity, reflection) | **established with sources**: reflection a(2π−θ) = a(θ) (purity, [CH07]); a ≥ 0, a' ≤ 0, a'' ≥ 0 on [0,π] (SSA, [HT07] eq 3.1); a'' ≥ −a'/sinθ (SSA + Lorentz, [CHL09], as quoted in [BWK16] eq II.1); det{∂^{j+k+2}a_n} ≥ 0 (reflection positivity, [CH12], derived for integer n and assumed for n = 1); σ^{(p)} ≥ 0 for p ≤ 4 and σ'/C_T ≥ π²/576 [BWK16] |
| Tier 3: `../quantum` supplies a(60°), a(90°), a(120°) | **unusable as a referee at the required precision**: vs the exact real-scalar values, a(90°) is 1.9% (s=1) / 1.3% (s=6) low; a(60°) = 0.02423 is ≈8% low (expected ≈0.0264 from the scalar/holographic ratio); a(120°) = 0.003896 is **below the rigorous bound** 𝔞_min(120°) = 0.004495 by 13%. Why the check fired: the bound is a theorem for any CFT with finite C_T and the lattice is a real scalar, so the extraction (`qsim/corner_angles.py`: hexagons R ≤ 14, triangles l ≤ 28, N = 160, m = 0.01, 3- and 4-parameter fits) is what is wrong, not the bound. Not modified (read-only); flagged in TODO. |

*R4. The disagreement, measured.* a(θ)/C_T at the angles where free-field values exist. Free-field
column shows the [HHCWM16] field-theory ansatz value with, in brackets, the spread to their lattice
value (the only available error estimate; ≈1.3% at 26.6°, ≤0.6% elsewhere). Einstein, ECG and the
bound are exact (≤1e-8). Deviations are relative to Einstein.

| θ | Einstein | bound | ECG t₄=+4 | ECG t₄=−4 | Dirac fermion | real scalar |
|---|---|---|---|---|---|---|
| 26.57° | 7.575 | 4.839 | 7.510 (−0.86%) | 7.642 (+0.87%) | 7.685 [±0.7%] (+1.5%) | 8.212 [±1.3%] (+8.4%) |
| 45° | 4.037 | 3.160 | 4.009 (−0.69%) | 4.065 (+0.69%) | 4.085 [±0.1%] (+1.2%) | 4.264 [±0.1%] (+5.6%) |
| 63.43° | 2.445 | 2.115 | 2.433 (−0.50%) | 2.458 (+0.51%) | 2.475 [±0.4%] (+1.2%) | 2.537 [±0.2%] (+3.8%) |
| 90° | 1.2220 | 1.1402 | 1.2185 (−0.29%) | 1.2255 (+0.29%) | 1.2259 (exact 4-digit) (+0.32%) | 1.2454 (exact 4-digit) (+1.9%) |
| 116.57° | 0.5483 | 0.5321 | 0.5476 (−0.14%) | 0.5491 (+0.14%) | 0.5491 [series = ansatz; lattice +1.6%] (+0.15%) | 0.5527 [0%] (+0.8%) |
| 135° | 0.2642 | 0.2605 | 0.2640 (−0.07%) | 0.2644 (+0.07%) | 0.2643 (exact) (+0.05%) | 0.2653 (exact) (+0.4%) |
| 153.43° | 0.0896 | 0.0892 | 0.0896 | 0.0897 | 0.0897 [series = ansatz; lattice +17%, unreliable] (+0.1%) | 0.0900 [±0.6%] (+0.4%) |
| θ→0 (κ/C_T) | 3.709 | log only | 3.672 (−1.0%) | 3.747 (+1.0%) | 3.8005 (+2.5%) | 4.179 (+12.7%) |

Sign: every known theory lies above Einstein except ECG with t₄ > 0. Ordering at every angle:
scalar > fermion > ECG(t₄=−4) > Einstein = all [BM15] models > ECG(t₄=+4). Note t₄ does *not*
order the deviation: the free scalar (t₄ = +4) is highest and ECG at t₄ = +4 is lowest.

*R5. Order-by-order decomposition* (σ^{(p)}/C_T relative to Einstein; free-field coefficients from
[HHCWM16] Tables 3–4, Einstein from [BWK16] eq V.6):

| p | 0 | 1 | 2 | 3 | 4 | 5 | κ |
|---|---|---|---|---|---|---|---|
| complex scalar | 0 (theorem) | +10.2% | +15.3% | +16.4% | +15.5% | +14.4% | +12.7% |
| Dirac | 0 | +1.35% | +3.8% | +4.6% | +4.1% | +3.3% | +2.5% |
| ECG t₄=±4 | 0 | ∓1.65% | ∓1.9% | | | | ∓1.0% |

The deviation is not concentrated in one coefficient; from p = 1 on it is a roughly constant
percentage, i.e. the non-universal part of a(θ) has, to first approximation, the *same shape* as
the universal part's tail, which is what σ^{(p)} → 2κ/π^{2p+3} says (ratio σ^{(p)}π^{2p+3}/2κ is
within 2% of 1 for p ≥ 2 in all three theories).

*R6. Reduction to one number, and what the interacting data can see.* The two-parameter (σ, κ)
trial function of [BMW15b] (eq 261 of [BCV21]) reproduces the exact Einstein curve to ≤0.9%, the
exact free-field values to ≤0.6% (45°–135°), and per [BCV21] the ECG curves to ≤1.2%. With σ/C_T
fixed by theorem, the entire known family of a(θ)/C_T is therefore a *one-parameter family in
κ/C_T* up to ≈1% shape residuals, and the measured collapse is the statement

    κ/C_T ∈ [3.672, 4.179]   for every theory computed to date (a 13% band),

with Einstein at 3.709, the [BM15] family degenerate with it, ECG spanning ±1% around it, the
fermion at +2.5%, the scalar at +12.7%. The trial-function slope d(a/C_T)/d(κ/C_T) is 1.18 at
26.6°, 0.43 at 45°, **0.048 at 90°**, 0.008 at 120°. A π/2 measurement with the O(N) error bar
(±0.1 on a/C_T) therefore constrains κ/C_T to ±2.1, four times the *entire* band. The θ = π/2
value is pinned between the bound (1.140) and ≈1.25 by σ alone; **the existing interacting-CFT
data (all n = 1 data are at π/2) carry no information about the quantity in which the residual
non-universality lives.** "Wilson-Fisher lands on the curve" is a ±8% statement at the one angle
where all theories are within 2% of each other by construction.

*R7. Rényi n = 2 (side result, outside the n = 1 collapse).* a₂(π/2)/C_T: Ising 0.556 ± 0.028
[NCRCLM26], free real scalar 0.676 (exact 0.02567/4 per corner), O(3) 0.743 ± 0.028 [LSZM24]; the
O(3) honeycomb/square ratio [2s(π/3)+2s(2π/3)]/[4s(π/2)] = 1.17(5) vs 1.3231 for free bosons
[LSZM24]. A 30% spread; consistent with [EH15]'s non-universality of σ_n/C_T for n ≠ 1, and in
tension with the 2013–14 NLCE values 0.62(6)/0.61(6) that [BMW15] tabulated, which [SSSDSM16]
attribute to unusual corrections to scaling in Rényi extractions. The precise modern QMC numbers
are not von Neumann numbers and must not be used to test the n = 1 collapse.

**Analysis**
1. Not solved in the literature; outcome F does not apply. But the problem as posed in TASK.md is
   inflated: of five "theory classes" one is degenerate with Einstein by construction ([BM15]),
   one is trivially free at N = ∞ ([WWS17]) and unmeasured at the relevant angles for finite N,
   leaving three genuinely independent curves (scalar, fermion, Einstein) plus the ±1% ECG band.
2. The quantitative content of the collapse is: (i) σ/C_T universal (theorem); (ii) the shape is
   fixed by (σ, κ) to ≈1% (empirical, five curves, no explanation); (iii) κ/C_T confined to a 13%
   band with Einstein near its bottom (empirical, no explanation, and no bound: [BWK16]'s bound
   gives only κ > 0, and ECG shows κ/C_T < κ_E/C_T^E is allowed). κ is the thin-strip coefficient,
   for free fields (1/π)∫c(t)dt over the 2d entropic c-function [CH07]; so (iii) is a statement
   about strip entanglement per unit C_T, not intrinsically about corners.
3. Any explanation "of type (C_T, t_4)" is refuted by the data in R4/R5: the sign of the deviation
   at fixed t_4 = +4 differs between the free scalar (+12.7%) and ECG (−1.0%). [BWK16] showed the
   weaker linear-ansatz version for σ'. This is an outcome-E-type fact already available: the
   deviations cannot be a function of the stress-tensor 2- and 3-point data alone.
4. Tier 3 of TASK.md cannot do its job with the sibling's numbers (R3, last row). The referee
   values at the required 0.1–1% level are the [CHL09]/[HHCWM16] tables, which are inference-free
   evaluations of the exact free-field expressions, not lattice fits.

**Grade** R1, R2, R4 (Einstein, ECG, bound, CHL values): verified. R4 free-field values at 26.6°–
63.4° and 116.6°–153.4°: partially verified (published field-theory/lattice pairs, ≤1.3% spread, no
independent recomputation here). R3 O(N) row: partially verified (ratios quoted by two papers; the
underlying Ising a₁ not visible in the cited source). R6: verified for the five computed curves;
the "one-parameter family" reading is a description of known data, not a theorem. R7: verified as
quoted; interpretation flagged as Rényi-only.

**Next steps** (none started; awaiting the user's answers to the questions in the session report)
- If the reframed target is accepted: the object to explain/bound is κ/C_T, with ≈1% shape
  residuals as the second-order question. A two-sided bound on κ/C_T would make the collapse a
  corollary (outcome C); the first thing to establish is whether κ has any known bound at all.
- Independent recomputation of the free-field a(θ) from the [CH07]/[CHL09] ODE system at
  arbitrary angles (this repo, own code) to replace the ±1.3% small-angle uncertainty with 4-digit
  values; this is the one computation the reasoning route cannot substitute for, because small
  angles are where the signal lives and no published 4-digit value exists below 45°.
- Interacting theories: the only informative measurement would be a von Neumann (n = 1) corner
  coefficient at θ ≤ π/3 in an O(N) model, or equivalently a strip coefficient κ/C_T for an
  interacting CFT; none exists.

## EXP-002  Obstruction: the residual deviations are not a function of stress-tensor 2- and 3-point data

**Date** 2026-09-04. **Status** complete. Promoted from a remark in EXP-001 at the user's request.

**Goal** Test the class of explanations in which a(θ)/C_T, or its deviation from the Einstein
curve, is determined by the stress-tensor two- and three-point data of the CFT. In a parity-even
3d CFT that data is exactly the pair (C_T, t₄) [BCR18 Sec. 7; BWK16 App. C]; since C_T scales out
of a(θ)/C_T, the class is "a(θ)/C_T = F(θ; t₄) for some function F", with no assumption on F
(linearity was already excluded for σ' by [BWK16] Sec. VI).

**Hypothesis** If the class is viable, two theories with equal t₄ must have equal a(θ)/C_T at
every angle, in particular equal κ/C_T, σ'/C_T, σ''/C_T. Free fields sit at the endpoints t₄ = ±4
of the allowed range and Einsteinian cubic gravity (ECG) spans that range continuously, so the
endpoints can be compared between two theories with different dynamics.

**Method** Inputs and their sources.
- t₄ of free fields: for n_s real scalars and n_f/2 Dirac fermions t₄ = 4(n_s − n_f)/(n_s + n_f)
  [BCR18 footnote 23]; hence real scalar t₄ = +4, Dirac fermion t₄ = −4. Confirmed independently by
  [BWK16] Sec. VI ("the complex scalar has a positive t₄ = 4 … the fermion has a negative t₄ = −4").
  Einstein gravity t₄ = 0 [BWK16 Sec. VI; BCR18 Sec. 7].
- t₄ of ECG: t₄ = −1260 μ f∞² / (1 − 3μ f∞²) [BCR18 eq. 129], from the twist-operator expansion
  h_q/C_T = (π³/24)(q−1) − (π³/11520)(420 + t₄)(q−1)² [BCR18 eq. 128, after Chu–Miao]; the same
  procedure reproduces the standard Gauss–Bonnet t₂ with the correct sign (BCR18 App. A). Restated
  unchanged in [Cano19] eq. 7.129 and in the ECG dictionary table C_T t₄ = −3780 μ f∞ L²/(π³G).
  The allowed range −4 ≤ t₄ ≤ 4 maps to f∞ ∈ [312/313, 318/317], i.e. μ ∈ [−0.00322, +0.00312],
  with t₄ = −4 at μ = +100489/32157432 = +0.0031249 [BCR18 eqs. 130–132].
- ECG corner data: σ = (1−3μ)σ_E, σ' = (1−33μ/4)σ'_E, σ'' = (1−2673μ/296)σ''_E,
  κ = (1−123μ/20)κ_E, C_T = (1−3μ)C_T^E [BCV21 eqs. 226, 295–297], same action and same μ as
  BCR18 (BCV21 eq. 118 is BCR18 eq. 3 up to the overall Euclidean sign). Full curves from my
  integration of BCV21 eq. 293 (`scripts/exp001_ecg.py`), controls passed to 6 digits.
- Free-field and Einstein numbers: EXP-001 R4–R5.

**A sign inconsistency in the sources, and how it is handled.** BCV21's Fig. 1 caption assigns
μ ≃ +0.00312 to t₄ = +4 and μ ≃ −0.00322 to t₄ = −4, and concludes "ECG theories with t₄ ≥ 0
lie below the Einstein gravity one". BCR18 eq. 129, which BCV21 cite as the source of the range,
gives the opposite: μ > 0 ⇔ t₄ < 0, and BCR18 say explicitly that t₄ = +4 "would imply a negative
value of μ". The two papers use the same action and the same C_T(μ), so this is not a convention
difference. I adopt BCR18 (the derivation, validated on Gauss–Bonnet) and flag BCV21's caption as
the inconsistent statement. **The obstruction below holds under either assignment**; only the
sizes of the two pairwise conflicts change, and both are given.

**Results** (units of C_T; deviations relative to Einstein; free-field and Einstein values exact
or 4-digit, ECG exact at first order in μ)

| theory | t₄ | κ/C_T | σ'/C_T | σ''/C_T | a(45°)/C_T | a(90°)/C_T |
|---|---|---|---|---|---|---|
| real scalar | +4 | 4.179 (+12.7%) | 0.028709 (+10.2%) | 2.814e-3 (+15.3%) | 4.264 (+5.6%) | 1.2454 (+1.9%) |
| ECG, μ = −0.00322 | +4 (BCR18) | 3.747 (+1.0%) | 0.026478 (+1.7%) | 2.488e-3 (+1.9%) | 4.065 (+0.7%) | 1.2255 (+0.3%) |
| Einstein, all [BM15] models | 0 | 3.709 (0) | 0.026042 (0) | 2.441e-3 (0) | 4.037 (0) | 1.2220 (0) |
| ECG, μ = +0.00312 | −4 (BCR18) | 3.672 (−1.0%) | 0.025611 (−1.7%) | 2.394e-3 (−1.9%) | 4.009 (−0.7%) | 1.2185 (−0.3%) |
| Dirac fermion | −4 | 3.8005 (+2.5%) | 0.026394 (+1.35%) | 2.533e-3 (+3.8%) | 4.085 (+1.2%) | 1.2259 (+0.3%) |

*Predicted by any F(θ; t₄):* scalar ≡ ECG(t₄=+4) and fermion ≡ ECG(t₄=−4) at every angle;
Einstein = F(θ; 0). If F is monotone in t₄ the five rows must be ordered by t₄.

*Measured:* neither identity holds, and the rows are not ordered by t₄.
1. Same t₄ = +4, different curves: κ/C_T 4.179 vs 3.747 (11.5% apart), σ'/C_T 8.4% apart,
   σ''/C_T 13.1% apart, a(45°) 4.9% apart. Uncertainties on both sides < 0.1%.
2. Same t₄ = −4, different curves: κ/C_T 3.8005 vs 3.672 (3.5% apart), σ'/C_T 3.1% apart,
   σ''/C_T 5.8% apart, a(45°) 1.9% apart.
3. Not monotone: the two t₄ = −4 theories straddle the t₄ = 0 theory (fermion +2.5%, ECG −1.0%),
   and the fermion (t₄ = −4) lies *above* the t₄ = +4 ECG curve (+2.5% vs +1.0%).
4. Under the alternative assignment (BCV21 caption): conflict 1 becomes 4.179 vs 3.672 (13.8%),
   conflict 2 becomes 3.8005 vs 3.747 (1.4% in κ, 0.3% in σ'), and the straddle disappears.
   Conflict 1 alone is two orders of magnitude above the uncertainties, so the obstruction is
   independent of which sign is right.

**Analysis** Any account of the residual non-universality that is a functional of ⟨TT⟩ and ⟨TTT⟩
alone cannot reproduce the measured deviations: it is forced to give the free scalar and one
holographic theory the same curve, and they differ by 11.5% in the sharp-limit ratio. This closes
the most natural "one more stress-tensor datum" extension of the σ theorem, including linear
(BWK16) and arbitrary nonlinear dependence, and including conformal-collider-type arguments that
only see energy-flux data. What survives: four-point stress-tensor data (BWK16's conjecture for σ'),
non-stress-tensor spectral data, or the twist-defect fusion data that control κ directly (EXP-003).
Two further readings of the table: within each family the deviation *does* increase with t₄
(scalar > fermion; ECG(+4) > ECG(−4)), but the scale differs by an order of magnitude between free
fields and holography, so t₄ is at most a within-family ordering parameter; and the free scalar
is the outlier in every column, consistent with its known anomalous Rényi stationarity [LLPS15].

**Grade** verified for the numbers and for the obstruction; the pairing of ECG curves with t₄
signs is *partially verified* (BCR18 derivation adopted over BCV21 caption; the inconsistency is
recorded above and in TODO).

**Next steps** None required for this entry.

## EXP-003  Outcome E: the general entropic constraints on a(θ) do not localise κ/C_T

**Scope, stated first.** "Admissible" below means *satisfies the listed inequalities C1–C6*. It does
not mean "is the corner function of a unitary 3d CFT": the Lifshitz endpoint used in the proof is the
corner function of a z = 2 Lifshitz theory and is not Lorentz invariant. Nothing here claims that a
CFT with κ/C_T = 10⁶ exists. The claim is narrower and stronger: **the constraint set does not
localise κ, so the physical band κ/C_T ∈ [3.672, 4.179] is not a consequence of the constraints.**

**Date** 2026-09-04; rewritten 2026-09-05 (argument spelled out, unboundedness made analytic).
**Status** complete.

**Provenance (M1 on this result).** The representation of the corner function as a Laplace
transform of a positive measure is the "infinite divisibility / conditional positivity" structure
of [CH12], who write (Sec. 5.2) "if we could write g(θ) as a Laplace transform…" for the holographic
case and verify the determinant inequalities for free fields to 6×6. [BWK16] proved in their App. A
that every reflection-positivity inequality "leads to lower bounds, and never to an upper bound", and
posed in their Sec. IX (Discussion), verbatim: "It is further natural to ask whether an upper bound exists for
a(θ), and its expansion coefficients. The holographic correspondence could be helpful in answering this
question." (ar5iv lines 690–692 of arXiv:1511.04077; the question is about a(θ) in general, not a narrower
object). That question is what this entry answers, in the negative and for the full
constraint set (not only reflection positivity). The mass-versus-tail reading, the explicit admissible
functions with arbitrary κ, and the consequence for the collapse are not in the literature I found
(searches on 2026-09-05: "corner function" with "moment problem", "completely monotone",
"infinitely divisible", "Laplace transform"; nothing relevant).

**Notation (M2).** θ ∈ (0, π), ε ≡ π − θ; a(θ) the corner function; σ = π²C_T/24 (theorem, [FLP16]);
κ ≡ lim_{θ→0} θa(θ); 𝔞_min(θ) ≡ (π²C_T/3) log[1/sin(θ/2)] [BWK16 eq. II.2]; a_L(θ) ≡ (θ−π)²/(θ(2π−θ))
[BWK16 Sec. VII; BCV21 eq. 260]; CHL[a] ≡ a'' + a'/sinθ.

**The constraint set 𝒞.** C1 reflection a(2π−θ) = a(θ) [CH07]; C2 a ≥ 0, a' ≤ 0, a'' ≥ 0 on (0,π)
[HT07]; C3 CHL[a] ≥ 0 [CHL09, as BWK16 eq. II.1]; C4 det{∂_θ^{j+k+2}a}_{j,k<M} ≥ 0 for all M, θ
[CH12; proven for integer Rényi index, conjectural at n = 1]; C5 a = σε² + O(ε⁴), σ = π²C_T/24, a
analytic at π with even powers; C6 a ~ κ/θ, κ > 0. Every published bound on a(θ) at n = 1 uses a
subset of these (EXP-001 R2).

**Spectral form.** For analytic a, C4 says the derivative sequence of a'' at every θ is a Hamburger
moment sequence, hence (Bernstein–Widder) a''(θ) = ∫₀^∞ dρ(s) cosh(sε) with ρ ≥ 0 after symmetrising
with C1, and a = ∫ dρ (cosh sε − 1)/s². Then: C1, C2, C4, C6 hold for every ρ ≥ 0 (C6 with κ read
off the tail: ρ ~ 2κ s² e^{−πs}); C5 is the total-mass condition M₀ ≡ ∫dρ = 2σ; C3 is the single
linear inequality CHL[a](ε) = ∫dρ(s) K(s,ε) ≥ 0 with kernel

    K(s, ε) = cosh(sε) − sinh(sε)/(s sin ε).

**Lemma 1 (the kernel has one sign change).** For fixed ε ∈ (0,π), K(s,ε) ≥ 0 ⟺ tanh(sε)/s ≤ sin ε.
The function s ↦ tanh(sε)/s decreases strictly from ε (s→0⁺) to 0, because its derivative has the
sign of sε sech²(sε) − tanh(sε) = (y − sinh y cosh y)/cosh²y < 0 (y = sε > 0). Since sin ε < ε,
there is exactly one s*(ε) > 0 with K < 0 on (0, s*) and K > 0 on (s*, ∞). So C3 penalises spectral
weight at small s and rewards weight at large s; it is the only constraint that is not automatic.

**Lemma 2 (two admissible functions).** (i) 𝔞_min ∈ 𝒞, κ = 0: C3 with equality [BWK16 App. A.1];
ρ_min(s) = (π²C_T/3) s/sinh(πs) > 0 (derived from −log cos(ε/2) = Σ_p (2^{2p}−1)|B_{2p}|(ε/2)^{2p}/(p(2p)!)
and (2^{2p}−1)ζ(2p)/2^{2p} = Σ_{m odd} m^{−2p}, giving M_{2p−2} = ∫s^{2p−2}·s/sinh(πs)). (ii) â_L ≡
(π⁴C_T/24) a_L ∈ 𝒞 with κ/C_T = π⁵/48 = 6.375: ρ_L ∝ s²e^{−πs} > 0 (the Laplace transform of s²e^{−πs}
is exactly 1/θ + 1/(2π−θ) − 2/π ∝ a_L); C3 reduces, with a_L = ε²/(π²−ε²), ∂_ε a_L = 2π²ε/(π²−ε²)²,
∂_ε²a_L = 2π²(π²+3ε²)/(π²−ε²)³, to f(ε) ≡ (π²+3ε²) sin ε − ε(π²−ε²) ≥ 0 on [0,π]. Proof: with
sin x ≥ x − x³/6 (x ≥ 0), f/ε ≥ ε²[(4 − π²/6) − ε²/2] ≥ 0 for ε ≤ 2.17; for ε = π − t, t ∈ [0, 0.97],
f ≥ (π² + 3·2.17²)(0.843 t) − t(π−t)(2π−t) ≥ (20.2 − 19.74) t ≥ 0. ∎ (Consistent with [BWK16] Sec. VII.)

**Theorem (no localisation).** (a) 𝒞 ∩ {σ fixed} is convex (C2–C4 and C6 are positivity/linear
conditions, C5 is affine), and κ is linear on segments. Hence a_λ = (1−λ)𝔞_min + λ â_L ∈ 𝒞 realises
every κ/C_T ∈ (0, 6.375]. (b) κ is unbounded above: let ρ_u ≡ 2κ s² e^{−πs} Θ(s−u), u ≥ 0, with
a_u = κ[e^{−uθ}/θ + e^{−u(2π−θ)}/(2π−θ) − 2e^{−uπ}/π] (closed form of its Laplace transform); its
sharp coefficient is κ for every u, while its mass 2σ_u = 2κ e^{−πu}(u²/π + 2u/π² + 2/π³) → 0. For
C3: at each ε, either u ≥ s*(ε), and then CHL[a_u](ε) = ∫_u^∞ ρ_L K ≥ 0 because K ≥ 0 on [u,∞) by
Lemma 1; or u < s*(ε), and then CHL[a_u](ε) = CHL[a_L](ε) − ∫₀^u ρ_L K ≥ CHL[a_L](ε) ≥ 0 because K ≤ 0
on [0,u] and CHL[a_L] ≥ 0 by Lemma 2(ii). C1, C2, C4, C6 hold since ρ_u ≥ 0. Rescaling to the
universal σ (C5) gives κ/C_T = (π²/24)·κ/σ_u → ∞ as u → ∞. ∎
Numerical check of the same family (`scripts/exp003_spectral.py`, `scripts/exp003_output.txt`):
κ/C_T = 0.004, 3, 10, 100, 10⁴, 10⁶ all pass C1–C6 at 40 angles; the moment positivity of the real
Einstein/scalar/Dirac coefficient sequences passes and a corrupted sequence fails.

**Mechanism.** In the spectral variable, σ is the mass of a positive measure and κ is its e^{−πs} tail.
C1, C2, C4, C6 are consequences of positivity; C5 fixes the mass; C3 is one inequality that is
indifferent to (in fact rewards) weight at large s. A tail functional of positive measures with fixed
mass is unbounded above and can vanish. **Corollary:** no inequality that is itself a consequence of
ρ ≥ 0 — any reflection-positivity-type inequality for a(θ) at n = 1, of any order — can bound κ. A
bound must be a constraint that some positive ρ violates, i.e. it must carry information beyond the
entropic inequalities of the corner function. This is why the problem is open, not merely that it is.

**Assumptions.** C4 at n = 1 is conjectural [CH12]; it is used only to organise the constraints and to
certify C4 for the constructions (which hold by ρ ≥ 0 regardless). Dropping C4 enlarges 𝒞, so the
theorem stands without it. Completeness of C1–C6 is the literature statement of EXP-001 R2.

**Grade** verified (analytic throughout; Lemma 2(ii)'s elementary inequality proved by standard
bounds; the numerical family is a check, not part of the proof).

## EXP-004  Direct numerical solution of the Casini–Huerta–Leitao system for the free-field corner functions at finite angle

**Date** 2026-09-04 (in progress; this entry is updated as results land). **Status** solver built and
validated on four exact controls; large-angle Rényi-2 values obtained; arbitrary-precision production
runs for the full angle range under way.

**Goal** Replace the ±1.3% published free-field values below 45° [HHCWM16] with 4-digit values at
arbitrary angles, for the real scalar (Rényi-2 as control, then von Neumann) and the Dirac fermion.
This is the computation the user authorised after the analytic route stalled (EXP-003): the residual
non-universality lives at small angles, where no published value is better than ≈1%.

**Why reasoning alone was insufficient** Every published free-field a(θ) below 45° is a Taylor
series about θ = π truncated at order 14–16 (radius of convergence π, so 8% short at 26.6°) plus
lattice points at the ≈1% level. The exact expressions of [CH07]/[CHL09] were never integrated
at finite angle; the authors expanded them in series ("an economic way to numerically integrate
the equations is to expand … in Taylor series around x = π", [CHL09] Sec. 4). Nothing analytic
reaches the sharp-angle regime.

**Method (M2).** x ≡ θ; δ ≡ π − x; M ≡ 2d mass on the unit sphere; a ≡ twist parameter; the 2d
Green-function trace on the cut sphere is tr G_S(x, M, a) = 8π a(1−a) F(x, M, a) with
F = ∫_x^π H_a(y, M) dy, and H solves the six-variable nonlinear ODE system with five algebraic
constraints of [CHL09] App. B eqs (73)–(83), boundary values (84)–(89) at x = π. Observables:
- Rényi-2, real scalar [CH07 eq. 40]: s₂(x) = 2 ∫_{1/2}^∞ dM M√(M²−¼) F(x, M, ½).
- Entanglement entropy, complex scalar [CHL09 eq. 61]: s_S(x) = ∫₀^∞ dt 2/cosh²(πt) ∫ dM M√(M²−¼)
  tr G_S(x, M, ½−it); real scalar = ½ of this.
- Dirac fermion [CHL09 eqs. 59–60]: s_D(x) = ∫₀^∞ dt /(2 sinh²πt) ∫_{−∞}^{∞} dm m tr G_D|odd, with
  tr G_D|odd = 2m tr G_S − 16π a(1−a) m (4β₁X₁cos(x/2) − bB₁sin²x)/(M(4β₁² − b²sin²x)), a = −it,
  M² = ¼ + m².
Mass variable p = √(M²−¼), so M√(M²−¼) dM = p² dp; Gauss–Legendre grids in p and t.
x = π is a regular singular point. The solution is started from a power series in δ whose
coefficients are found by least squares on the coefficient equations (leading orders derived by
hand: β₁¹β₂¹ = [a(a−1)+M²(1+b₀c₀)]/(4M²), β₁¹c₀ = b₀β₂¹, u¹ = Mc₀β₁¹, H¹ = 1/(16πa(1−a)) +
M(β₁¹X₂⁰ + β₂¹X₁⁰)); the local expansion has a genuine two-fold sign ambiguity in β¹, and only one
branch gives an H¹(M) that decays in M (the other does not, so its mass integral cannot exist).
Parities in δ, checked numerically: H, u, β₁, β₂, B₁₂ odd; X₁, X₂, b, c, B₁, B₂ even.

**Precision analysis (the finding that shaped the implementation).** The physical solution near
x = π has H ≈ e^{−2πM} relative to the O(1) variables and then grows like e^{2M(π−x)} as the
corner sharpens; any absolute error ε in the O(1) variables (b, c, X, u) seeds that same growing
mode, so the relative garbage in F is ε·e^{2πM}. Double precision therefore resolves the signal only
for M ≲ 4, while the mass integrand at small angles decays only slowly: measured rates
dlnF/dM ≈ 5.5, 3.9, 2.2, 1.6, 1.2, 0.83 per unit M at θ = 135°, 90°, 45°, 26.6°, 15°, 5°. Hence
double precision gives 4 digits only for θ ≳ 60°, and sharp angles need masses up to ≈15 with
≈25 + 3M decimal digits and a series start accurate to e^{−2πM}·10⁻¹⁰ in absolute terms
(N ≈ 1.6M + 8 terms from δ₀ = 0.01/M). Implemented in mpmath with a 32nd-order
Gragg–Bulirsch–Stoer integrator, parallel over (M, t) nodes.

**Implementation** `scripts/exp004_ch_solver.py` (double precision: series start by
Levenberg–Marquardt, DOP853 integration, algebraic constraints solved at every step with a
deterministic root branch), `scripts/exp004_mp.py` (arbitrary precision: parity-reduced
Gauss–Newton series start warm-started from the double solution, Bulirsch–Stoer with adaptive
macro-step, complex a), `scripts/exp004_prod.py` (parallel driver, per-node JSON checkpoints,
modes renyi2 / ee / dirac), `scripts/exp004_run.py` and `scripts/exp004_controls.py` (double
runs), logs and node files under `scripts/`.

**Controls (all passed before any new number was read off).**
| control | source of the known value | result |
|---|---|---|
| σ₂ (real scalar) = 1/(48π²) = 2.110857993e-3 | [BMW15] App. B, [HHCWM16] Table 3 | 2.110857993e-3 (ratio 1.0000000) |
| σ₂′ = (5+π²)/(960π⁴) | [HHCWM16] Table 3 (exact) | ratio 1.000000 |
| σ₂″, σ₂‴ | [HHCWM16] Table 3 (high precision) | ratios 1.000000, 1.000000 |
| s₂(90°) real scalar | 0.0064 [CH07 via KHSM13]; 0.0130/2 [HHCWM16] | 0.006487 (double, M ≤ 4, two grids agree to 2e-4) |
| s₂ at 116.6°, 135°, 153.4° | [HHCWM16] Table 1 α=2 /2: 0.00286, 0.001365, 0.0004615 | 0.0028591, 0.0013665, 0.00046127 (ratios 0.9997, 1.0011, 0.9995; their values are 3-digit) |
| mp vs double at M = 1 | internal | all six angles agree to the printed 8 digits |
| complex a (EE path) | imaginary part must cancel [CHL09] | Im F ≈ 1e-27 at a = ½ − 0.3i and ½ − i |
The first four are the smooth-limit coefficients from the series start alone, i.e. they validate the
boundary values, the local expansion and the branch choice to 7 digits; the angle values validate
the ODE integration and the mass quadrature.

**Results so far (double precision, M ≤ 4, real scalar Rényi-2, 48-node grid).**
θ = 90°: 6.4879e-3; 100°: 4.8632e-3; 110°: 3.5659e-3; 120°: 2.5291e-3; 130°: 1.7072e-3;
135°: 1.36649e-3; 140°: 1.06848e-3; 150°: 5.9099e-4; 160°: 2.5959e-4; 170°: 6.4448e-5
(uncertainty ≈ 2e-4 relative at 90°, ≤ 1e-5 beyond 130°). Values below 90° from this run are
contaminated by the large-mass loss of precision and are superseded by the mp run.

**Grade** solver and controls: verified. Angle values ≥ 90° (Rényi-2): verified to the stated
precision. Everything below 90° and all von Neumann / Dirac values: pending (mp production).

**Status update 2026-09-05 — runs parked at the user's request.** Rényi-2 real scalar completed after
the series-start fix (leading order built in mp, continuation in N; the double-precision warm start
was the cause of the failure above M ≈ 5.4 and had also biased earlier nodes at M ≈ 3 by 0.2–0.5%):
48 mass nodes to M = 15, 1.2 core-hours, σ₂ and σ₂′ from the nodes reproduce the exact values to
9 digits, the smooth limit at 170° to 7e-6, and the seven [HHCWM16] angles to ratios 1.0000, 1.0004,
1.0002, 0.9981 (their value is 3-digit), 0.9997, 1.0011, 0.9995. The sharpest angles (5°, 10°) are
still contaminated by the M ≈ 15 nodes (one node has F(5°) < 0), so "4 digits at any angle" was
overclaimed there. The von Neumann and Dirac runs were not executed (EE nodes for M ≲ 1 exist as
checkpoints). Honest justification, answering the user's challenge: this computation sharpens the
≈1% shape residual beyond (σ, κ) and supplies exact reference values; it does not address why the
band κ/C_T ∈ [3.67, 4.18] is narrow, which is the question. Parked, not killed: the instrument is
validated and can resume in minutes if the residual becomes the target.

**Next steps (if resumed)** von Neumann scalar (controls: σ = 1/256, σ′ = (20+3π²)/(18432π²), s(π/2) = 0.01183, s(3π/4) =
0.002520, κ = 0.0397); then the Dirac fermion (controls: σ = 1/128, σ′ = (16+3π²)/(9216π²),
s(π/2) = 0.02329, s(3π/4) = 0.005022, κ = 0.0722).


## EXP-005  What a bound on κ/C_T would have to use, and why nothing available does

**Date** 2026-09-05. **Status** complete as an audit; negative.

**Goal** Given EXP-003, list every general structure that could in principle constrain κ, and decide
for each whether it can exclude positive spectral measures (the criterion of EXP-003's Corollary).

**Method** For each candidate: what it constrains, whether that constraint is implied by ρ ≥ 0, and
what it would need to become a bound. Sources for each named structure are the ones already
verified in `references.md`.

| structure | what it gives for the corner function | bounds κ? | what would be needed |
|---|---|---|---|
| Strong subadditivity, all configurations | Inequalities among log coefficients arise only when the area terms cancel, i.e. overlapping sectors with shared boundary pieces (HT07; CHL09 with boosts). In every such configuration the *smallest* angle sits on the "≥" side (a(α−β) ≥ a(α)+a(γ−β)−a(γ)), so SSA gives lower bounds on a at small angles — convexity, C3 — never upper bounds. | No (lower bounds only; C2–C3 are already in 𝒞). | An SSA configuration putting a small-angle corner on the "≤" side with cancelling area terms; none exists for sectors (intersections are narrower than their factors). *partially verified*: standard configurations classified, no exhaustive proof. |
| Reflection positivity of the corner function, any order | C4 = ρ ≥ 0. | No (Corollary of EXP-003). | Nothing: it is a positivity condition, blind to the tail. |
| The Rényi tower a_n(θ), n ≥ 2 | Each a_n satisfies its own C1–C4 with h_n in place of C_T [BWK16 eq. II.8]; a_n at integer n is a genuine twist-line two-point function. | No: there is no inequality linking κ_n across n (Rényi mutual information is not monotone in n), and n → 1 is exactly where C4 becomes conjectural. | A proven n-monotonicity or an n-analyticity bound for the *sharp* coefficient; none known. |
| The strip / mutual-information reading of κ | κ is the short-distance coefficient I(A,B) ≈ κℓ/w of two half-planes [CH07; NN15; BW22]; equivalently κ_n = −E_Cas(n)/(n−1), the Casimir energy per unit length of a twist-n line and its orientation reversal (fusion datum, [DKPW24] define the fusion product). Reflection positivity of the slab partition function gives E_Cas ≤ 0, i.e. κ_n ≥ 0. | Lower bound 0 only. | An *upper* bound on the Casimir energy of the reflection-symmetric defect pair, which requires the slab spectrum and overlaps — dynamical data of the twist defect at n → 1. Not available in general; [DKPW24] compute examples. |
| A crossing relation for the two-defect system | The two-twist-line partition function has a short-distance (fusion, κ) and a long-distance (bulk OPE, Δ_min and OPE data) expansion; for 2d CFT the analogous 4-point function is bootstrappable and bounds follow. | Not yet: no positivity-controlled crossing equation is available for the n → 1 limit in d = 3 (positivity of the fusion expansion at n = 1 is again the [CH12] conjecture, which EXP-003 shows is insufficient on its own; the bulk-channel data would have to be added). | The n → 1 defect crossing equation with a positive fusion expansion *and* bulk spectral input. This is the one route that could produce a two-sided bound in terms of CFT data. Unverified, named as the target. |
| Modular theory (Bisognano–Wichmann, relative entropy, first law, QNEC) | Constrain state dependence and *second* null variations of S (QNEC: S''_null ≤ 0 in vacuum, which is the FLP entanglement density ∝ −C_T, i.e. the σ theorem). | No: second order only; κ is the resummation of all orders of the shape expansion (radius of convergence π, κ at its boundary). | An all-orders shape inequality; none exists. |
| Stress-tensor n-point positivity (ANEC, conformal collider) | Bounds 3-point data (t₄ ∈ [−4, 4]); higher-point positivity could in principle bound σ^{(p)} order by order. | No: EXP-002 shows κ is not a function of (C_T, t₄); and no finite set of moments M_{2p} bounds the tail of a positive measure (moment indeterminacy). | Simultaneous control of all orders, which is the crossing relation above in another guise. |
| Free-scalar extremality (κ/C_T ≤ 4.179) | Parallels the conjectured extremality of the free scalar for C_T/F₀ in d = 3 [BFGLM26]; consistent with all known values (EXP-001 R4). | Conjecture only. | An F-theorem-like monotonicity for the strip coefficient; the only known one is holographic (strip c-function, Myers–Singh 2012, not verified here), and it relates κ across an RG flow, not κ to C_T within a CFT. |

**Provenance.** [BWK16] Sec. IX raise the upper-bound question and suggest holography as the tool; the
holographic answer ([Miao15], [BCV21]) was that the Einstein curve is not even a lower bound. No
source treats the question structurally.

**Analysis** Every available general principle either is a positivity condition on the corner
function (and therefore cannot see the tail, by EXP-003), or acts at finite order in the shape
expansion (and therefore cannot see a quantity that sits at the boundary of that expansion's
convergence). The obstruction has a name: **κ is a non-perturbative fusion datum of the twist
defect (the Casimir energy of the reflection-symmetric pair as n → 1), and no entropic inequality or
finite-order correlator bound reaches it.** The only structure that could, a crossing equation for the
two-defect partition function with positive expansions at n = 1, does not exist in usable form. This
is outcome E for the class {entropic inequalities of a(θ)} ∪ {stress-tensor 2- and 3-point data} ∪
{finite-order shape perturbation theory}: no argument in that class can produce the band
κ/C_T ∈ [3.672, 4.179], and the reason is structural, not a failure of ingenuity.

**Grade** verified for the rows marked with sources and for the mechanism; the SSA row is partially
verified (no exhaustive classification); the crossing-relation row is a named target, unverified.

**Next steps** If the user wants to pursue a bound: the twist-defect crossing route at integer
n ≥ 2 first (where positivity is not conjectural), asking whether κ_n/h_n is bounded there; a bound
at n = 2 would be a new result even without the n → 1 continuation. This is analytic/bootstrap
work, not a corner-function computation.


## EXP-006  The integer-n route: formulation, data, and where it inherits the obstruction

**Date** 2026-09-05. **Status** formulated; one structural finding; negative as a bound.

**Goal** Follow EXP-005's one live route at n = 2, where positivity of the twist-line correlators is
not conjectural: ask whether κ_n/h_n is bounded by the structure of the two-twist-line partition
function.

**Setup (M2).** For integer n the twist operator τ_n(∂A) is a codimension-2 conformal defect of CFT^n;
S_n(A) = (1/(1−n)) log[Z_n(A)/Z₁^n]; the Rényi mutual information I_n(A,B) = (1/(n−1)) log[Z_n(A∪B)/(Z_n(A)Z_n(B))]
is the connected two-defect partition function. For two half-planes at separation w, I_n = κ_n ℓ/w
[CH07; BMW15b Sec. 3.2]; κ_n is the sharp-corner coefficient of a_n(θ) and, equivalently, minus the
Casimir energy per unit length of τ_n and its orientation reversal divided by (n−1). h_n is the
conformal weight of τ_n (energy density in the hyperbolic thermal ensemble, [HMS14]).

**Data at integer n (free fields; h_n exact from [BMW15b] Table 1; κ_n are source values from [BMW15b] Table 3, quoted there as 0.0455996(1), 0.0472338(1), etc., i.e. with an uncertainty of 1 in the last digit, reproduced in [BW22] Table 2; none computed here):**

| n | h_n (complex scalar) | κ_n (cs) | κ_n/h_n (cs) | h_n (Dirac) | κ_n (f) | κ_n/h_n (f) | spread |
|---|---|---|---|---|---|---|---|
| 2 | 1/(24π) = 0.013263 | 0.0455996 | 3.438 | 1/64 = 0.015625 | 0.0472338 | 3.023 | 13% |
| 3 | 1/(27√3) = 0.021383 | 0.037339 | 1.746 | 5/(108√3) = 0.026729 | 0.040662 | 1.521 | 14% |
| 4 | (3π+8)/(192π) = 0.028888 | 0.033798 | 1.170 | (1+6√2)/256 = 0.037052 | 0.0376674 | 1.017 | 14% |
| 1 | (C_T-normalised) | 0.0794 | κ/C_T = 4.179 | | 0.0722 | 3.800 | 10% |

The free-field spread of κ_n/h_n is ≈14% at every integer n, no narrower than at n = 1. No
holographic κ_n exists for n ≥ 2 (the strip Rényi entropy is not known holographically), so at
integer n the "band" is two points.

**Fusion-channel positivity is complete monotonicity in the separation, and is tail-blind.** Quantise
with Euclidean time along the direction joining two parallel twist lines; the reflection through the
mid-plane maps one line to the other (for n = 2, τ₂ is its own orientation reversal). Reflection
positivity then gives, for the family of separations, Σ c_i c_j Z(d_i + d_j) ≥ 0, i.e. (Widder)
Q(d) ≡ Z_n(A∪B)/(Z_n(A)Z_n(B)) = ∫ dμ(E) e^{−E d} with μ ≥ 0: Q is completely monotone in d. For two
half-planes Q = e^{(n−1)κ_n ℓ/w}, which is completely monotone for *every* κ_n ≥ 0 (e^{c/w} =
Σ_k c^k/(k! w^k) and each 1/w^k is a Laplace transform of a positive density). So the fusion channel
gives κ_n ≥ 0 and nothing else, by the same mass-versus-tail mechanism as EXP-003: the short-distance
coefficient is the large-E tail of μ, the long-distance behaviour is its small-E part, and positivity
of μ relates neither to the other.

**No crossing symmetry in d = 3 (the structural finding).** In d = 2 the two-interval Rényi entropy
obeys F_n(x) = F_n(1−x) because the complement of two intervals on the Riemann sphere is again two
intervals with cross-ratio 1−x; this exchanges the fusion limit (x → 1) with the OPE limit (x → 0) and
is what lets positivity bound the short-distance coefficient by low-lying data (the mechanism of the
Cardy formula: crossing turns a tail into a mass). In d = 3 the complement of two disjoint disks is a
region with two holes, conformally an annulus, not two disks; purity only reverses the orientation of
the same two circles. The two-disk Rényi partition function Q(η), η ∈ (0,1), therefore has two positive
expansions — the fusion expansion at η → 1 (complete monotonicity) and the bulk OPE expansion at
η → 0, Q = Σ_O C_O² G_O(η) with C_O the one-point coefficients of the twist defect — but **no symmetry
exchanging their limits.** Both expansions describe the same limits from the same side. Without such a
symmetry, positivity in each channel is tail-blind in the sense of EXP-003, and the short-distance
coefficient is fixed only by the high-Δ growth of Σ C_O², which unitarity alone does not bound.
(Consistently, [ACHM25] find the long-distance series of the d = 4 scalar mutual information is only
asymptotic at n = 1, and [AM26] give the exact two-sphere Rényi mutual information of the free
Dirac field in d = 3 for all n, which would be the test function for any sum rule.)

**What the integer-n route would need.** A bound on κ_n/h_n requires a bound on the growth of the
defect one-point coefficients C_O² of τ_n at large Δ in terms of low-lying data — a defect-bootstrap
statement (crossing of the defect two-point function of bulk operators, or of the bulk-to-defect
OPE), not an entropic inequality. That input exists for line defects in principle (defect bootstrap)
but has not been developed for twist lines of CFT^n and is beyond this session.

**Analysis** The obstruction of EXP-003/005 persists at integer n: the only non-conjectural positivity
available (reflection positivity of the two-defect correlator) is complete monotonicity in the
separation, which cannot see the tail, and d = 3 lacks the crossing symmetry that makes the analogous
d = 2 problem bootstrappable. The named input that could reach κ_n is the high-Δ growth of the twist
defect's one-point coefficients.

**Grade** the data table and the complete-monotonicity statement: verified; the absence of a crossing
symmetry for two disks: verified (elementary geometry of complements); "unitarity alone does not bound
the growth of C_O²": partially verified (no such bound is known to me; not proved impossible).

**Next steps** If continued: (i) extract the twist-line one-point coefficient growth from the exact
Dirac two-sphere Rényi mutual information [AM26] at n = 2 and check what "Cardy-like" growth
reproduces κ₂ = 0.0472338; (ii) ask whether the defect bootstrap for τ₂ constrains that growth.


## EXP-007  Complement topology: why the d = 2 tail-to-mass bridge has no d ≥ 3 analogue

**Date** 2026-09-05. **Status** complete; standalone version in `RESULT.md` §6.

**Goal** State the mechanism by which positivity bounds a short-distance coefficient in d = 2 (the
two-interval Rényi entropy), identify precisely what it needs, and show what fails for two balls in
d ≥ 3.

**The mechanism (Cardy).** A positive spectral sum plus a symmetry exchanging its two asymptotic
regimes turns a tail into a mass: modular invariance Z(β) = Z(4π²/β) fixes the high-energy density
of states from the vacuum. For two intervals in a 2d CFT the scaling function obeys F_n(x) = F_n(1−x)
[CCT09 verbatim: "It is also invariant under x → 1−x (even if not manifest in this form)", and "by
symmetry x → 1−x also for x close to 1, corresponding to close intervals"] because the complement of
two intervals on the circle is two intervals with cross-ratio 1−x; the far regime (lightest
operators) and the touching regime (short-distance coefficient) are exchanged.

**What it needs.** (i) a positive expansion of the function in one channel; (ii) a symmetry mapping
the regime where the sought coefficient dominates onto the regime controlled by low-lying data.

**What fails in d = 3.** Two disjoint disks are conformally a disk and the exterior of a concentric
disk [NN15; AM26 eq. 2.16 use exactly this map]; their complement is the annulus between them, a
connected region with two boundary circles, not two disks. Purity only reverses the orientation of the
same two circles. Hence the two-disk Rényi partition function Q(η) has two positive expansions (fusion
at η → 1: complete monotonicity in the separation; bulk OPE at η → 0 [Cardy13]) but no symmetry
exchanging their limits. Each channel's positivity is then tail-blind in the sense of EXP-003, and the
short-distance coefficient is fixed only by the large-Δ growth of the twist defect's one-point
coefficients.

**Generalisation.** In d = 2 an interval's entangling surface is two points and four points can be
re-paired; in d ≥ 3 a ball's entangling surface is a connected sphere and the complement of two balls
in S^d is a shell bounded by both, which cannot be re-paired. So the absence of crossing holds for
two-ball Rényi mutual information in every d ≥ 3, and the tail-blindness applies to every
short-distance coefficient of that function (the strip coefficient κ_d of [AM26] eq. 4.16 in any d).

**Provenance.** Ingredients standard ([CCT09]; [NN15], [AM26]). The assembled statement not found
(searches 2026-09-05 for higher-dimensional mutual information with "crossing"/"complement"; results
are the long-distance-expansion papers [Cardy13] and successors, none of which use or discuss a
crossing symmetry). Offered as new with that caveat.

**Grade** the geometry: verified (elementary); the claim that this is *the* reason bounds are absent
in d ≥ 3: an explanation consistent with everything checked, not a theorem — labelled as such.

## EXP-008  The Abate–Martinek route: what the exactly solvable instance shows

**Date** 2026-09-05. **Status** complete as a reading; negative as a bound.

**Goal** Follow EXP-006's next step: in the one exactly solvable case — the two-sphere Rényi mutual
information of the free massless Dirac field in d = 3 for all n [AM26] — read off how the short-distance
coefficient κ is encoded in the "OPE-channel" data, and ask whether the construction contains a bound.

**What [AM26] do (verified from their §2–4).** They map two spheres to the concentric configuration
(disk of radius a, exterior of radius b; cross-ratio η = 4ab/(a+b)², their eq. 2.16 — the same
disk-plus-exterior geometry as EXP-007), reduce on the angular sphere to a tower of two-dimensional
Dirac fields in AdS₂ with masses μ_ℓ and degeneracies λ(ℓ) (polynomial in ℓ, eq. 4.27), and compute
each mode's Rényi mutual information exactly through Painlevé VI tau functions (eqs. 3.19–3.27). The
full answer is the sum over ℓ (eq. 4.3). In §4.3.1 they extract the area term: "we will approximate
the sum over the angular momentum as an integral, because the divergence will come from the terms
with large ℓ" (eq. 4.18), each large-ℓ mode reduces to the flat-space two-interval problem for a
massive 2d Dirac field (eqs. 4.19–4.21), and the result is
I = 2^{[d/2]+1}/((d−2)(d−3)!) (a/ε)^{d−2} ∫₀^∞ dt t^{d−3} c_flat(t) (eq. 4.24), i.e. exactly the
strip coefficient κ_d = [(d−2)2^{d−3}π^{(d−2)/2}Γ((d−2)/2)]^{−1} ∫ t^{d−3} c_flat(t) dt (eq. 4.17),
which for d = 3 is the Casini–Huerta formula κ = (1/π)∫c(t)dt [CH07 eq. 44]. For n = 2 the same
integral with the Rényi-2 c-function is how [BMW15b] Table 3 obtained κ₂ = 0.0472338(1) (Dirac);
[AM26] do not re-quote that number.

**What this establishes.** In the solvable instance the picture of EXP-003/006/007 is literal: the
long-distance (OPE) regime is the ℓ = 0 sector and the first few modes (their §4.2 and App. B give the
long-distance coefficients mode by mode); the short-distance coefficient κ is the *tail* of the mode
sum, Σ_ℓ λ(ℓ) I(η; μ_ℓ) with λ(ℓ) ~ ℓ^{d−3}, and its value is set by the 2d dynamics of every mode
(the c-function of a massive Dirac fermion), not by any positivity property of the sum. The
"density of contributions" at large ℓ is polynomial and universal (it is the angular degeneracy); the
non-universal content of κ is the integral of the mode function. There is no crossing relation in
their construction (consistent with EXP-007), and the sum over ℓ converges "much slower" in the
short-distance regime, "strongly depending on the value of ε" (their §4.3.2), which is the same
tail-sensitivity in yet another guise.

**What it cannot give.** A bound on κ/h_n would need the mode function's integral to be bounded in
terms of low-ℓ data; in the free theory the mode function is the same 2d c-function for every ℓ (only
the mass changes), so the integral is fixed by the 2d theory and unrelated to h_n except through the
common free-field normalisation. For interacting CFTs the tower does not decouple, and the analogue of
the mode sum is the bulk-channel expansion of the two-defect correlator organised by spin, whose
large-Δ density is the defect one-point-coefficient growth named in EXP-006. The solvable instance
therefore confirms the diagnosis and supplies a test function for any future sum rule; it does not
supply the sum rule.

**Grade** the reading of [AM26]: verified against their text (equations quoted by number). The
interpretation as "κ = tail of the mode sum": verified (it is their derivation). "No bound is
contained in the construction": verified for the free case by inspection; the interacting statement
is the EXP-006 obstruction restated.

**Next steps** None within reach of this session. The open input remains a growth bound on the twist
defect's one-point coefficients at large Δ; the free-field mode sum gives the target growth
(polynomial density times a fixed mode function) that any such bound would have to reproduce.

## EXP-009  Attack on the complement-topology claim: pre-registered falsifiers, outcome "true in a narrower form"

**Date** 2026-09-05. **Status** complete. No computation; reasoning and three metadata lookups.

**The target (EXP-007, RESULT.md §6 as first written).** (T) The complement of two balls in S^d is a
shell for d ≥ 3. (C) This is *why* no bound on κ exists: the Cardy mechanism needs a symmetry
exchanging the two asymptotic regimes of a positive expansion; d = 2 has it (x ↔ 1−x, from the
re-pairing of four endpoints); d ≥ 3 has no such symmetry, so a tail can never become a mass.

**Pre-registered falsifiers (written before looking).**
- Strong (withdraw C): a model-independent two-sided bound or exact determination of a non-local
  short-distance coefficient in a d ≥ 3 CFT — κ, σ′, F, c_S/C_T, or a defect Casimir coefficient —
  derived without any relation between two positive expansions with inversely related parameters.
- Weak (force a narrowing): any d ≥ 3 configuration containing κ that possesses a limit-exchanging
  structure; C as stated says none exists.
- Unfalsifiable: if "limit-exchanging structure" cannot be defined so that a proposed mechanism can be
  tested against it without already knowing the answer.

**Step 1 — where tail-from-mass bounds come from anywhere.** Modular bootstrap (β ↔ 4π²/β); four-point
crossing (u ↔ v; the lightcone bootstrap's large-spin data come from the crossed identity);
open–closed duality of the annulus (t ↔ 1/t; Cardy's boundary-state conditions); Froissart (unitarity
plus analyticity in the crossed channel); EFT positivity, where linear positivity gives one-sided
bounds and crossing gives two-sided ones — [TWZ21] verbatim: "In contradistinction to the linear
positivity for scalars, these inequalities [from full crossing symmetry] can be applied to put upper
and lower bounds on Wilson coefficients"; [CV21] find all coefficients bounded both ways from
causality and unitarity. Positivity alone: Källén–Lehmann bounds the mass side (Z ≤ 1); the
c-theorem's sum rule gives one-sided c_UV ≥ c_IR; Nachtmann/Hölder give convexity in spin, no upper
bound. Anomaly matching fixes local coefficients without any channel relation. Pattern: positivity →
one-sided; two-sided → a second positive expansion with inversely related parameter whose lowest state
is universal; locality → local coefficients only.

**Step 2 — the weak falsifier fired.** Two limit-exchanging structures exist in d ≥ 3:
(i) *Two parallel twist lines (the strip geometry).* Quantising across the lines gives the closed channel
Q(w) = ∫dμ(E) e^{−Ew} (complete monotonicity, EXP-006). Quantising *along* the lines gives an open
channel: Q = Tr_{H(w)} e^{−ℓ H_open(w)} = Σ_k e^{−ℓ E_k(w)}, positive in e^{−ℓ}, where H(w) is the
Hilbert space of CFT^n on the transverse plane with two twist-point insertions at distance w. For
infinite lines only the ground state survives, Q = e^{−ℓE₀(w)}, so E₀(w) = −(n−1)κ_n/w: **κ_n is the
ground-state energy coefficient of the open channel.** The tail of one channel is the mass of the
other. The naive claim "no exchange exists for κ" is false.
(ii) *The torus.* The Euclidean partition function on T² × R^{d−2} is symmetric under exchanging the
two cycles, so the high-temperature entropy density coefficient equals d times the Casimir energy
coefficient of the theory with one compact spatial cycle: c_S = d·c_vac [Sha16, "generalized Cardy
formula"]. Free scalar in d = 3: c_vac = ζ(3)/(2π), c_S = 3ζ(3)/(2π): exact, as it must be (same
Euclidean path integral).
*Why neither yields a bound:* the mass at the other end is itself non-local. E₀(w) is the Casimir
energy of two twist points on a plane; c_vac is the Casimir energy on a circle; in odd d no anomaly
fixes such quantities (there is no conformal anomaly), and in even d anomalies fix Casimir energies only
of curved geometries, not of flat tori or defect configurations. Contrast d = 2, where the crossed
vacuum is universal twice over: the identity operator in the OPE channel, and the Casimir energy
−πc/(6L) fixed by the anomaly in the thermal channel. Numerical corroboration: c_S/C_T in d = 3 is
60.43 (real scalar: s = 3ζ(3)T²/(2π), C_T = 3/(32π²)), 12πζ(3) = 45.3165 (Dirac: s = (3/2)·3ζ(3)T²/(2π),
C_T = 3/(16π²)), 4π⁵/27 = 45.3362 (Einstein: s = 4π²L²T²/(9G), C_T = 3L²/(π³G)) — a 33% spread across
theories despite the exact cycle-exchange relation, because c_vac is non-universal. (The Dirac and
Einstein values agree to 4.4·10⁻⁴ — corrected from 3·10⁻⁴; resolved as chance in EXP-010.)

**Step 3 — the strong falsifier did not fire.** No model-independent two-sided bound on κ, σ′, F,
c_S/C_T or a defect Casimir coefficient in d ≥ 3 exists in the literature reached in this workspace or
in the attempts above. And the moment-problem statement of EXP-003 generalises: for Q(q) = ∫q^Δ dν(Δ)
with ν ≥ 0, any constraint of the form ∫φ dν ≤ B with φ = o(tail growth) leaves the singular-end
coefficient free; a bound requires a growth condition at the singular end itself. Known sources of
such growth conditions: (a) an inverted channel with a universal lowest state (absent for κ: the
two-ball function's only channel with a universal lowest state is radial quantisation about the
common centre, whose universal end is the far limit, and complement topology forbids any conformal map
of the touching end onto it; the strip's open channel exists but its lowest state is non-universal);
(b) locality/anomalies, which fix local coefficients only (σ ∝ C_T; the even-d log term of the
two-sphere mutual information equals the anomaly, [AM26] §4.3.2) — κ is not local (EXP-002);
(c) a finite local Hilbert-space dimension, giving cutoff-dependent bounds (κ ≤ 2β_∞δ from S ≥ 0,
cf. [BW22]); (d) an a priori analyticity-plus-growth bound of Froissart type — in QFT these come from
unitarity plus crossing, or from locality with a cutoff, so (d) reduces to (a) or (c) in every case
known to me. This is "I found no third bridge", not "none can exist".

**Step 4 — what is now a theorem, and what is not.**
(N1) *Theorem (moment problem).* Positivity of the expansion plus any set of constraints dominated by
the mass (finite-order local data, low-lying spectral data, normalisations) cannot bound a
singular-end coefficient from above; a bound requires a growth condition at the singular end.
(N2) *Theorem (d = 2).* The x ↔ 1−x symmetry supplies that growth condition because the crossed
channel's lowest state is the identity with a universal contribution; the symmetry exists because
the four endpoints of two intervals re-pair into two intervals.
(N3) *Theorem (d ≥ 3 geometry).* The two-ball Rényi function has exactly one positive channel with a
universal lowest state (radial quantisation; identity at the far end) and no conformal map sends the
touching end to the far end (complement of two balls is a shell). The strip has an inverted channel,
but its lowest state is the non-universal Casimir energy E₀(w) ∝ κ_n.
(N4) *Fact (odd d).* Casimir energies of flat and defect geometries are non-local in odd d, so inverted
channels there relate non-universal quantities to each other (torus: c_S = d c_vac; strip: κ_n = E₀).
(C, narrowed) The only known bridges from a singular-end coefficient to universal data are (a) an
inverted channel with a universal lowest state and (b) locality/anomaly; for κ, (a) is absent by
N3, (b) is excluded by EXP-002; no third bridge is known. This is a classification of known
mechanisms and is falsifiable by exhibiting a third; it is not a theorem that none exists.

**Step 5 — consequences checked against things not used to build the claim.**
- Torus: the generalised Cardy relation c_S = d·c_vac holds exactly in every CFT [Sha16] — predicted
  by "inverted channel ⇒ tail = mass"; and c_S/C_T is nonetheless non-universal (33% spread above) —
  predicted by "the mass is non-universal in odd d". Both checked.
- Even versus odd d: the refined mechanism says short-distance coefficients fixed without a channel
  relation must be local; the two-sphere mutual information's log coefficient is the anomaly in even d
  [AM26 §4.3.2] and no such universal subleading term exists in odd d, where the subleading term is
  F [AM26 eq. 4.4] — consistent.
- Forward-looking, falsifiable: no proof of the free-scalar extremality conjectures (κ/C_T ≤ 4.18;
  C_T/F₀ ≤ scalar value, [BFGLM26]) can come from entropic inequalities or finite-order positivity; a
  proof would have to supply a growth condition at a singular end. Consistent with [BFGLM26]'s d = 5
  finding that F(A) is unbounded in both signs for general regions.

**Outcome.** *True in a narrower form.* (T) stands. (C) as first stated is wrong: limit-exchanging
structures do exist in d ≥ 3 (strip along/across; torus cycles) and one of them contains κ. The
surviving statement is N1–N4 plus the narrowed classification: what d ≥ 3 lacks for κ is not an
exchange but an exchange *onto a universal lowest state*, and in odd d the missing universality is the
absence of anomaly-fixed Casimir energies. The general principle "positivity gives one-sided bounds,
crossing gives two-sided ones" is prior art in the EFT-positivity literature [TWZ21, CV21]; the
generalised Cardy relation is [Sha16]; the application to entanglement coefficients, the
open-channel reading of κ_n, and the "universal lowest state" refinement are not in the literature
reached here.

**Grade** N1–N3: verified (N1 is EXP-003's mechanism; N2 elementary with [CCT09]; N3 elementary
geometry plus the along/across quantisation). N4: verified as stated (no anomaly in odd d; torus
and defect Casimir energies non-local). The narrowed (C): a classification, partially verified —
its falsifier is a third bridge. Numbers in Step 2: computed here from standard free-field and
Einstein-gravity formulas; not independently sourced.

## EXP-010  The parked coincidence c_S/C_T (Dirac) ≈ c_S/C_T (Einstein): chance, and here is the base rate

**Date** 2026-09-05. **Status** complete; arithmetic and three lookups, no computation.

**Pre-registration (before looking).** Null: chance. "Chance" withdrawn only if (a) the base rate against
the actual Dirac–Einstein spread in this family comes out below ~1% *and* (b) a further independent
quantity shows the same pair within 1e-3 while the scalar does not. "Relation" only if it predicts a
number not used to find it. "Less non-universal than the theorem allows" requires a third,
structurally different theory within ~1% of the value.

**Correction of my own numbers first.** 12πζ(3) = 45.3165 and 4π⁵/27 = 45.3362, not 45.320 and 45.332
as written in EXP-009 and TODO (both now corrected). The agreement is 4.4·10⁻⁴, not 3·10⁻⁴. The
underlying inputs are standard and were re-derived here: real scalar s = 3ζ(3)T²/(2π), C_T = 3/(32π²);
Dirac s = (3/2)·3ζ(3)T²/(2π), C_T = 3/(16π²); Einstein s = 4π²L²T²/(9G) (planar AdS₄ black brane,
T = 3r_h/(4πL²)), C_T = 3L²/(π³G) [BMW15]. Since 4π⁵/27 = 12π·(π²/9)², the physical coincidence is
exactly the arithmetic near-identity **ζ(3) ≈ π⁴/81** (81ζ(3)/π⁴ = 0.99956).

**It is not new and not isolated in the sense that matters: it is the n → 0 end of a known curve.**
The Rényi corner coefficient σ_n of a disk-type twist is set by the thermal free energy on H² at
temperature T₀/n; as n → 0 that is the flat-space high-temperature limit, i.e. c_S. [BMW15b] Tables 2
and 4 give lim_{n→0} n²σ_n/C_T = ζ(3)/π² (Dirac) and π²/81 (Einstein): the same two numbers, the same
ratio π⁴/(81ζ(3)). [BMW15b] already recorded (Sec. 5, verified text) that σ_n/C_T for the free Dirac
fermion and Einstein gravity agree to "no more than 2.6% for n ≥ 1 and 0.2% in the range 0 ≤ n ≤ 1".
So the c_S coincidence is the endpoint of a curve whose 0 ≤ n ≤ 1 branch was already known to agree to
0.2%. The two are one observation, not two.

**Base rate, three ways.**
1. Conditional on the known 0.2% envelope on 0 ≤ n ≤ 1 with a forced zero at n = 1 (the σ theorem): a
   smooth deviation of typical size ≲ 2·10⁻³ on that branch lands within 4.4·10⁻⁴ at the endpoint with
   probability of order 4.4·10⁻⁴/2·10⁻³ ≈ 20%.
2. Unconditionally, against the Dirac/Einstein log-ratios of the quantities in hand — κ/C_T +2.4%,
   σ′ +1.3%, σ″ +3.7%, σ‴ +4.5%, a(π/2) +0.3%, a(45°) +1.2%, σ_∞ +2.6%, h₂ +0.95% (Dirac π²/12 = 0.8225
   vs Einstein π·σ₂^{hol}/C_T = π³(5√13−1)/648 = 0.8148, from [BMW15b] Table 4), F/C_T −34%, c_S −0.044% —
   a spread of a few per cent gives ≈1% per quantity for a 4.4·10⁻⁴ hit, and ≈5–10% for at least one
   among the eight or so comparable quantities.
3. Arithmetically: the chance that ζ(3) lies within 4.4·10⁻⁴ of *some* π^k/n with small k and n ≤ 100 is
   of order 10–20% (the spacing of π⁴/n near 1.2 is ≈0.015, so that family alone gives ≈6%).
None reaches the pre-registered 1%.

**Criterion (b) fails.** The one out-of-sample quantity I had not looked at, h₂/C_T, differs by 0.95%
between the pair; σ_∞ by 2.6%; F/C_T by 34%; t₄ maximally (−4 vs 0). The pair's typical proximity is
1%, not 10⁻³. The only sub-percent agreements are the forced ones near n = 1 (σ theorem) and the n < 1
branch already noted by [BMW15b].

**Hypothesis "less non-universal than allowed" fails.** Third theories: real scalar 16πζ(3) = 60.43;
N = ∞ O(N) Wilson–Fisher (4/5)·16πζ(3) = 48.34 (c̃/N = 4/5 [Sac93], with C_T = N C_T^{free} at leading
order [WWS17]); N = ∞ Gross–Neveu equals N free Dirac fermions exactly, c̃/N = 3/2 [PSN99], hence not
an independent point. The value 45.3 is shared only by the free Dirac fermion and Einstein gravity;
bosonic theories sit 7–33% higher. The obstruction theorem is untouched: c_S/C_T spans a 33% band.

**Hypothesis "a relation" fails as an exact statement and is not pursued as an approximate one.** Any
relation making the two functions equal would have to hold on n > 1 as well, where they differ by up
to 2.6% with a definite sign (Dirac above Einstein for every n > 1, Einstein above at n → 0). No
relation is proposed; constructing one to hit 45.32 would be the post-hoc fitting the contract
forbids.

**Verdict.** Chance, superposed on a known, loose and still unexplained pattern: the hyperbolic thermal
free energy of the free Dirac fermion and of Einstein gravity, normalised by C_T, agree exactly at
T = T₀ (theorem), to ≤ 0.2% for T ≥ T₀ (n ≤ 1), and to ≤ 2.6% for T < T₀ (n > 1) [BMW15b]; the c_S
endpoint at 4.4·10⁻⁴ is within that envelope. The residue worth explaining, if any, is the 0.2%
branch, and it belongs to [BMW15b]'s observation, not to this session. What would distinguish
"crossing plus coincidence" from anything structural: the sign of the deviation on n ∈ (0, 1) —
both closed forms are known (Einstein: (π²/24) n x_n(1−x_n²)/(n−1) with x_n = (1+√(1+3n²))/(3n),
reproducing Table 4; Dirac: [BMW15b] eq. 3.10 sums) — a sign change inside (0, 1) would make the
small endpoint difference a crossing artefact; but even a uniform sign would not turn a 0.2%
agreement into a relation without a prediction on n > 1, where none exists.

**Grade** numbers: verified (re-derived; cross-checked against [BMW15b] Tables 2 and 4, which reproduce
the same ratio). Base rates: estimates, stated as such. Verdict: the null, with the pre-registered
criteria applied as written.

## EXP-011  The Abate–Martinek route at n = 2: κ₂ is the tail, the bridge is absent, and it is confirmation

**Date** 2026-09-05. **Status** complete; reading and arithmetic only, no computation.

**Pre-registration.** Three outcomes named before reading: (A) a sum rule relating a growth rate to κ₂
that predicts something not used to build it; (B) confirmation that κ₂ is exactly the tail with
nothing in the construction bounding it; (C) the step is not session-sized. Also pre-registered: a
growth rate fitted to reproduce 0.0472338 is not a result, and (B) if obtained is not news.

**Fact 1 — the n = 2 tail formula, and what 0.0472338 is.** [AM26] §4.3.1 write the area term only at
n → 1 (eqs. 4.18–4.24, mutual information I and the entropic c-function). The Rényi version is the
same derivation with I → I_n, c̃ → c̃_n; in d = 3 it is exactly [BMW15b] eq. (3.20),
κ_n^f = (1/π)∫₀^∞ c_n^f(t) dt, and their Appendix B states that Table 3 was obtained by "numerically
solv[ing] eqs. (B.4) and (B.6) … and then us[ing] the results to evaluate eq. (3.22)". So
κ₂ = 0.0472338(1) *is* the tail integral evaluated numerically. Comparing "the growth read off the
solvable case" with it compares a formula with its own evaluation: an identity, not a test. No
independent 3d determination of κ₂^f (lattice or corner-function extraction) was found to test
against, and none is needed, because the tail identity is a derivation, not a conjecture.

**Fact 2 — what "the growth" is in the solvable case, and why it cannot bound anything.** In d = 3
the degeneracy is λ(ℓ) = 1 and μ_ℓ = ℓ + ½ ([AM26] eqs. 2.9–2.10). The area term (their 4.18) keeps
only the top power of λ and only ℓ ~ ℓ_* ~ a/ε → ∞ (their 4.25); any finite set of low modes
contributes at most O(log(a/ε)) (their 4.28: each mode gives ⅓ log(a/ε) + 𝓘(μ_ℓ)). Translated to
defect language with a/ε = 1/(2√(1−η)) (their 4.4): the bulk-channel coefficient density of the
two-defect Rényi-2 function must grow so that its partial sums scale as Λ^{1/2}; the exponent is
kinematic (the dimension of the entangling circle) and the amplitude is κ₂ by definition. The only
relation between "growth rate" and κ₂ available in the construction is this Tauberian identity, which
predicts nothing that was not used to state it. Outcome (A) is empty.

**Fact 3 — the sharpest form of the obstruction, read off at n = 2 (new here, arithmetic).** From
[BMW15b] (B.2)–(B.3) at n = 2 the fermionic sum has the single sector k = ½, a = k/n = ¼, so
c₂^f(t) = −2ω_{1/4}(t) = 2∫_t^∞ y u²_{1/4}(y) dy, and swapping the order of integration,

    κ₂^f = (1/π)∫₀^∞ c₂^f dt = (2/π) ∫₀^∞ y² u²_{1/4}(y) dy,       ∫₀^∞ y u²_{1/4}(y) dy = 1/8.

The second equation is the UV central charge: c₂^f(0) = (c/6)(1 + 1/n) = ¼ for c = 1, equivalently
ω_a(0) = −2a² (check: (1/(1−n)) Σ_k (−2k²/n²) with Σ_{k=−(n−1)/2}^{(n−1)/2} k² = n(n²−1)/12 gives
(n+1)/(6n); at n = 2, ¼). So in the solvable instance κ₂ and the universal UV datum are the **second
and first moments of the same positive profile y u²_{1/4}(y)**, a Painlevé transcendental with fixed
short- and long-distance asymptotics ((B.7): −½ log t at t → 0, (2/π) sin(π/4) K_{1/2}(t) at t → ∞).
Positivity, a fixed first moment, and a fixed decay rate do not fix a second moment; only the full
connection problem does. This is EXP-003's mass-versus-tail dichotomy realised inside the one
exactly solvable case, one step further down (in the 2d mode function itself). Grade: derivation
verified against the quoted equations; the number 0.0472338 not recomputed.

**Fact 4 — a physical pair with equal tail and different head ([AM26]'s own remark, d = 4).** "If the
sum begins at ℓ = 1 instead, (4.2) gives the RMI for the Rarita–Schwinger field in d = 4" (their §4.1).
The area term depends only on the top power of λ(ℓ) at ℓ → ∞ (their 4.18), so Dirac and
Rarita–Schwinger in d = 4 have the same κ₄, while the removed ℓ = 0 mode carries the leading
long-distance term (η^{2μ₀+1} = η³, the Δ = 3/2 fermion) and shifts the log coefficient (their 4.8,
ΔS = ⅙ log(a/ε) + 𝓘(1)). That is the truncation of RESULT.md Theorem (b) — cut the bottom of the
tower, keep the tail — realised by two free fields rather than by a constructed density. Caveats: it
is d = 4 not d = 3, and the entanglement entropy of the spin-3/2 gauge field carries the usual
edge-mode subtleties, which [AM26] address only by matching their ref. [41]; the pair is an
illustration, not part of the theorem.

**Outcome (B), stated as such.** κ₂ is exactly the tail; the construction contains no bound; and this
is confirmation of EXP-003/006/008, not news. The step tightens the obstruction from "no bridge
found" to: *in the one solvable instance the bridge is absent too, and the reason is visible — the
universal datum and κ₂ are different moments of one positive function.*

**What is not session-sized, and what it would need (outcome (C) for the remainder).**
(i) A closed form for ∫y²u²_{1/4}: a Painlevé connection-type integral; integrable-systems question,
no bearing on the bound. (ii) An independent 3d κ₂^f to test the identity: unnecessary, see Fact 1.
(iii) The actual open input, unchanged: a growth condition on the bulk-channel density of the
two-defect function that does not come from the tail itself. It would have to come from a second
positive expansion with a universal lowest state (absent for two balls in d ≥ 3, RESULT.md §6) or
from an analyticity-plus-growth argument of a type not yet available for defect fusion. Search terms
for a next person: defect fusion, Casimir energy of parallel conformal defects, cusp/fusion
anomalous dimensions; not surveyed here and no specific paper is cited.

**Not done, by decision.** The only sum-rule-shaped structure the solvable case offers is
cross-dimensional: κ_d ∝ ∫t^{d−3}c_n(t)dt are Mellin moments of one positive function ([AM26] 4.17,
[CH07]), so log-convexity in d must hold for free fields. It is a free-field statement about
dimensional reduction, not about the bound; the Casini–Huerta table of κ_d needed to check it did
not survive the text conversion of arXiv:0905.2562; left unchecked and listed in TODO.

**Grade** Facts 1–2: verified against the quoted equations. Fact 3: derivation verified; arithmetic
checked in two ways. Fact 4: verified as [AM26]'s statement; physical status of the RS entropy not
examined. Outcome (B): the null, as pre-registered.
