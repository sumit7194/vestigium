# S1 result (float only): GO

Run 2026-11-27 14:02–14:09 IST on the Mac mini: 1 core, nice 10, detached (tools/detach.sh). Final log: `s1_run.out`;
per-β records: `s1_beta_<β>.json`; G-norm: `s1_gnorm.json`. Code: `s1.py`, `run_s1.sh`. Registration: `PREREG.md`
(e010d1d + a5f2054), unchanged. Written by Claude Opus 5.5 (office "Quantum").

## Plain reading
- At small β the MN field splits Kerr's r_u = 16 homoclinic loop by exactly the amount the certified Melnikov
  coefficient predicts: β · 2.8676e-3 · sin 2ψ0, against the prediction β · 2.8672e-3 (0.01% off at β = 1e-4).
- The splitting stays linear in β to 0.1% over 1e-4…1e-3, and to 1.4% out to β = 3e-2.
- The BVP's conditioning improves as 1/β, as transversality predicts. At β = 3e-2 the best zero has cond(DF) ≈ 7.5e5,
  well under the registered 1e8.
- So both registered criteria hold. **S1 = GO.** S2 waits for the Bridge's go.

## Gates (all PASS)
| Gate | Registered | Measured |
|---|---|---|
| G-norm | 8 points, 1e-6 rel | PASS: worst H0 2.2e-16, Hb 5.2e-15 |
| G-Kerr | β = 0: \|ΔK_r\| ≤ 1e-9; K_r conserved ≤ 1e-9 | max\|ΔK_r\| 3.27e-11; spread of K_r over the 64 W^u apo points 3.87e-11; K_r(fp) − mean K_r(W^u apo) 3.0e-11 |
| G-fp | \|P(fp) − fp\| ≤ 1e-11 at every β | worst 8.6e-14 |

## Numbers
| β | λ_u | A/β (sin 2ψ0 coefficient / β) | b2 (cos 2ψ0) | cond(DF) at the 4 zeros (ψ0 ≈ π/2, π, 3π/2, 2π) | best |
|---|---|---|---|---|---|
| 0 | 26.86870 | – (max\|ΔK_r\| 3.3e-11, noise) | – | 7.8e9, 2.3e9, 7.1e9, 6.6e9 (noise zeros) | – |
| 1e-4 | 26.86837 | 2.86764e-3 | 1.2e-11 | 3.2e9, 5.0e8, 2.3e8, 5.1e9 | 2.3e8 |
| 3e-4 | 26.86769 | 2.86794e-3 | 1.2e-10 | 7.0e8, 8.1e8, 6.8e7, 1.7e9 | 6.8e7 |
| 1e-3 | 26.86532 | 2.86939e-3 | 1.3e-9 | 2.1e8, 5.4e8, 2.3e7, 4.5e8 | 2.3e7 |
| 3e-3 | 26.85850 | 2.87349e-3 | 1.2e-8 | 7.9e7, 2.0e8, 8.0e6, 1.7e8 | 8.0e6 |
| 1e-2 | 26.83422 | 2.88595e-3 | 1.3e-7 | 2.2e7, 3.9e7, 2.3e6, 4.7e7 | 2.3e6 |
| 3e-2 | 26.76128 | 2.90660e-3 | 1.2e-6 | 7.2e6, 1.4e7, 7.5e5, 1.4e7 | **7.5e5** |

- **Criterion (a):** |A/β| = 2.86764e-3 at β = 1e-4, against 2.86724e-3 (+0.014%; the limit is 10%). The spread over
  1e-4…1e-3 is 0.1% (the limit is 20%). **TRUE.**
- **Criterion (b):** some cond(DF) ≤ 1e8 at β ≥ 1e-2. Best 2.3e6 at β = 1e-2 and 7.5e5 at β = 3e-2. **TRUE.**
- **Sign (reported, not a criterion):** A > 0, i.e. K_r(W^u) − K_r(W^s) = +β · 2.87e-3 · sin 2ψ0. Here ψ0 is the Mino
  θ-phase at the outer turning point, measured from the preceding z = +z_m turning point.
- **Other harmonics** are small. At β = 1e-2: a1/β 3e-6, a3/β −6e-6, a4/β −3e-6, against a2/β 2.9e-3.
- **The O(β²) drift** in A/β is +1.3e-3 per unit β (2.8676e-3 → 2.9066e-3 from 1e-4 to 3e-2).
- **S2's β by the registered rule** (the smallest cond at β ≥ 1e-2): β = 3e-2, the zero at ψ0 ≈ 4.695 (≈ 3π/2),
  n = 8 section returns.

## Caveats on cond(DF) (this is a float estimate, not a bound)
- **It is evaluated at an approximate homoclinic point.** s_u is the W^u point whose apo phase is the first-order zero
  of ΔK_r (from the exact ψ–log s linear relation). The orbit then returns to within 4e-5 to 9e-4 of fp (`dist_end`),
  not exactly onto W^s.
- **The value at the nearest W^u sample agrees** to a few % at β ≥ 1e-2. Both are recorded (`nearest_sample`).
- **β = 0 sets the float noise floor:** cond ≈ 2e9 to 8e9 where DF is singular in exact arithmetic. At β = 1e-4
  the transversality signal is only 1 to 10× above that floor. The clean 1/β scaling of the best zero (2.3e8 → 7.5e5
  over 300× in β) is the evidence that cond tracks transversality, not noise.
- **The ψ0 ≈ 3π/2 zero is about 10× better conditioned than the others at every β.** I have not explained that
  asymmetry; it is noted for S2.

## Disclosures (bugs found and fixed before the final run; all records kept)
- **`superseded_run1/` (12:29).**
  - The backward z_max search was cut at τ 200, so only 17/64 W^s points finished.
  - cond used MNFlow.P with tmax 400.
  - Both limits were raised. MNFlow.P was then too slow, because its event is non-terminal, so I wrote `Pstep` (a
    terminal-event return with the section Jacobian). Pstep matches MNFlow.P to 4e-15 in the point and 1.7e-7 in J at
    β = 0.
  - `fixed_point` now uses Pstep too, with damped Newton.
- **`superseded_run2/` (13:26).**
  - In cond_df, after passing fp, the orbit leaves along the inward branch and plunges toward the horizon
    (r+ = 9, x = 1). DOP853 then crawls there without end.
  - Fix: a terminal plunge event at x < 1.5 (r < 11) in Pstep and to_apo. This is a domain guard, not a time cap.
  - In cond_df, a plunge after the closest approach ends the return search.
- **`superseded_run3/` (13:41).**
  - Pstep's first 10-τ step had no plunge guard, and a return at x = 1.59, p_x = −5.36 hung there. That phase is now
    guarded.
  - In the same patch, cond moved from the nearest W^u sample to the interpolated zero, which is the registered
    definition. Both values are now recorded.
  - All β were rerun for consistency. The gate and amplitude numbers in run 3 are identical to the final run.
- **Unused:** `cfield.py` / `cbuild/` (a compiled-C field; it gave only 4× and is not used by `s1.py`) and the
  explore*/prof* diagnostics are local only.
- **No result was read before the fixes except as listed.** The amplitudes at β = 1e-4 and 3e-4 were seen in run 3.
  Neither criterion or threshold changed.

## Budget and conduct
- **Final run:** 6.4 min wall on 1 core (~0.11 core-h).
- **The whole S1 effort** (superseded runs, timing and diagnostics) is an upper estimate of ≈ 2 core-h, within the
  registered 3. I do not have exact CPU totals for runs 1–3.
- **Memory:** observed RSS was well under the declared 300 MB footprint.
- No caps. Hung runs were stopped by SIGTERM on my own verified PIDs (nothing else touched).
