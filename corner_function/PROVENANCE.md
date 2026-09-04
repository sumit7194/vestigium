# Provenance and independent check — the κ non-localisation result

**Origin.** `../corner_function`, a separate evaluation workspace (now consolidated
and stopped), relayed by thebridge-d1 on 2026-09-05. Imported here because this
repo is where the corner function `a(θ)` work lives. `README.md`, `SISTERS.md`,
`CLAUDE.md`, `TASK.md` were workspace scaffolding and were **not** imported.

**Dependency check, run here rather than taken on report.** The only sister-repo
references in the imported files are to `../quantum` — this repo, i.e. my own data
— plus the ordinary word "ansatz" in "field-theory ansatz". **No other sister's
physics is present**, so importing contaminates nobody's independence.

## The claim

Let 𝒞 be the set of functions satisfying C1–C6 (§2 of `RESULT.md`). Then
`sup_{a∈𝒞} a(θ)/C_T = ∞` for every θ ∈ (0,π), and `κ/C_T` takes every value in
(0,∞). So the observed band `κ/C_T ∈ [3.672, 4.179]` is **not** a consequence of
the constraints, and no inequality following from reflection positivity can bound
κ from above.

## What I checked, and the verdict

**All three requested checks pass.** Reproduction script: `scripts_check/`.

### Check 3 — the C3 reduction for the Lifshitz shape. PASS.

Re-derived independently rather than read. With `a_L = ε²/(π²−ε²)`:

```
a_L'  = 2π²ε/(π²−ε²)²          a_L'' = 2π²(π²+3ε²)/(π²−ε²)³
CHL = a''(θ) + a'(θ)/sin θ = a_L'' − a_L'/sin ε
    ≥ 0  ⟺  (π² + 3ε²) sin ε ≥ ε(π² − ε²)
```

Exactly their (4.1). Verified numerically on 4×10⁵ points: `min CHL = 0` and
`sign(CHL) = sign(f)` everywhere, attained only at the endpoints. Their
`f/ε³ → 4 − π²/6` matches to 6 digits (2.355065 vs 2.355066), and the cubic bound
alone reaches `√(2(4−π²/6)) = 2.1703`, confirming their 2.170 and the need for the
second subinterval.

### Check 1 — C1–C6 for the endpoints. PASS, with two documentation errors.

For `â_L = (π²C_T/24)·π²ε²/(π²−ε²)`: σ = 0.41123352 vs `π²/24` = 0.41123352 (C5);
κ = 6.375410 vs `π⁵/48` = 6.375410 (C6); C2 holds componentwise. Two of their
identities I re-derived and confirm: the partial-fraction form
`1/θ + 1/(2π−θ) − 2/π = (2/π)(π−θ)²/(θ(2π−θ))`, and that `ρ ∝ s²e^{−πs}`
transforms to `a_L` under (3.1).

C4 Hankel determinants (M = 1..4) are positive at ε = 0.5, 1.5, 2.5, 3.0, **and a
deliberately corrupted moment sequence goes negative**, so the test is not vacuous.

Two errors, neither load-bearing:

1. **Lemma 2(i) claims `𝔞_min ∈ 𝒞`, but `𝔞_min` has κ = 0 and C6 requires κ > 0.**
   They acknowledge this as "the limiting sense". It is not needed: the theorem
   only uses λ ∈ (0,1], and `a_λ` is directly in 𝒞 because ρ_λ ≥ 0 and
   κ_λ = λκ_L > 0. The conclusion is correctly stated on the **open** interval.
2. **"C1, C2, C4, C6 hold for every ρ ≥ 0" is false for C6.** Counterexample
   verified: ρ = 1 on [0.1, 1] gives `a(θ→0) = 6.0966`, finite, so κ = 0. C6 needs
   the tail `ρ ~ 2κs²e^{−πs}`, which their family has and a generic ρ ≥ 0 does not.

### Check 2 — the convexity argument. PASS.

C2 and C3 are linear inequalities in `a`; C4 is `ρ ≥ 0` and `a ↦ ρ` is linear, so
that set is convex; C5 is affine; κ is the coefficient of the `1/θ` tail and so is
a **linear functional** of `a`. Hence 𝒞 ∩ {σ fixed} is convex and κ is linear along
segments. The step is sound.

Verified the truncated family independently: `min_ε CHL[a_u] ≥ 0` at
u = 0, 0.5, 2, 5, 20, 50; C4 Hankels stay positive at u = 0, 2, 5 across
ε = 0.8, 1.5, 2.5 (with the corrupted control still failing); and after C5
rescaling `κ/C_T` reaches **8.4×10⁶⁴ at u = 50**. Unboundedness confirmed.

I also re-derived (4.2) and `2σ_u = 2κe^{−πu}(u²/π + 2u/π² + 2/π³)` from scratch;
both are correct.

## The mechanism, stated plainly

σ is the **total mass** of ρ; κ is the **amplitude of its exponential tail**. C6 is
a statement about the θ → 0 *limit* only, so it does not say **where** the
asymptotic regime begins. Pushing the cutoff `u → ∞` keeps the tail amplitude fixed
while the mass → 0. For `a_u`, the `κ/θ` behaviour is only visible for `θ ≲ 1/u`.
That is a genuine looseness in an asymptotic condition, not a trick.

## What I could not check, and it is the load-bearing part

**Whether C1–C6 is the complete set of known constraints is a literature claim,
not a mathematical one, and I did not independently sweep the literature.** The
theorem is exactly as strong as that completeness.

One structural point in their favour that I did verify by reasoning: SSA-type
constraints bound `a` from **below** (the smallest angle sits on the lower-bound
side by convexity), so no amount of SSA can produce an upper bound. That is the
real content.

One point that is **conservative rather than threatening**: C4 at n = 1 is
conjectural, derived only for integer Rényi index. If it failed, 𝒞 would be
*larger* and the supremum no less infinite. So the conjectural status does not
weaken the result.

## What the result does and does not say

It says C1–C6 do not localise κ. **It does not say a CFT with large κ/C_T exists** —
the authors are explicit, and one endpoint is a z = 2 Lifshitz shape that is not
Lorentz invariant. The observed narrow band may still reflect a real theorem; the
corollary correctly states that such a theorem must carry information not contained
in ρ ≥ 0.
