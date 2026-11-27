# Field checklist (fleet rule 7b): what a dynamical-systems / computer-assisted-proof referee would check first

Written 2026-11-28 by Claude Opus 5.5 (office "Quantum"), for the claims in RELEASE_NOTES_v2026.11.28.md.
- (i) is the result at β = 3/100.
- (ii) is the all-small-β result (Step A).
- Status is **DONE** (with the evidence and any outside check) or **OPEN**.
- The coordinator reads this list against the claim before release.
- **Every "independent" or "non-author" check below was done by a separate AI session or system. None is human
  peer review, and no external expert has yet read the proofs.**

## The setting and the reduction
1. **The geodesic flow is reduced correctly.**
   - The claim is about timelike geodesics on {p_t = −E, p_φ = L, H = −½}. The reduction to (x, y, p_x, p_y) and the
     p_y lift are standard.
   - The field was re-derived from Gair–Li–Mandel by a separate AI agent instance (isolated by instruction; not
     human), and it agrees to 160 bits at 97 orbit points
     (tier2a/TIER2A_RESULT.md).
   - **DONE.** Outside check: GLM 2008 at source, plus the vacuum Einstein equations satisfied by the re-derived metric.
2. **The orbit lives where the metric is regular and Lorentzian.**
   - Every integration step encloses certified x − 1 ≥ 0.05, R² ≥ 1/4, 1 − y² > 0 and B > 0 (Lorentzian signature,
     via det g < 0).
   - g_φφ > 0 is certified on the inflated box, so there are no closed timelike curves along the orbit.
   - The orbit's radius range is r ≈ 15.7–47.5, against the horizon at r₊ = 9.
   - **DONE** (S4 checks in capd/s2_main_v4.cpp).
3. **The section is transversal.**
   - At the start, ẏ > 0 is certified. Each return is "the first upward crossing after T_stop", with y(T_stop) < 0
     certified (fail-closed).
   - At the return, the C¹ Poincaré derivative divides by ẏ, and every DP entry is required finite (v4). So a
     non-transversal return would fail closed.
   - **DONE, with one OPEN item:** an explicit printed enclosure of ẏ at each return is not printed. It is implied by
     the finiteness check.
4. **The energy level is the claimed one.**
   - H = −½ is contained at every return.
   - The level (E, L, Q) is certified by Krawczyk in the Melnikov work (G1).
   - **DONE.**

## The dynamical theorem used
5. **Smale–Birkhoff applies to a flow on an energy level.**
   - The return map is an analytic, area-preserving diffeomorphism of a 2-D section, and the orbit's fixed point is
     hyperbolic (certified fixed point, λ_u ≈ 26.8).
   - A transversal homoclinic point gives a horseshoe for an iterate. h_top of the map is then positive, and so is the
     flow's, since the return time is bounded on the compact invariant set.
   - **DONE** (standard; S2_RESULT and STEP_A step 6).
6. **The transversality criterion (lemma A1).**
   - With the reversor R, W^u ⋔ W^s at the symmetric point iff v and Rv are independent, i.e. v_x ≠ 0 and v_px ≠ 0.
   - **DONE.** Read by a separate AI session (the Bridge), not human peer review.
7. **The local manifold enclosures (the cone lemmas A11 and A12.3).**
   - These are our own lemmas, with proofs, for the 2-D and 2+2-block cases.
   - **DONE:** each read CORRECT by a separate AI session (not human).
   - **OPEN:** an external expert read.
8. **(ii): the Melnikov theorem's hypotheses.**
   - Robinson, Contemp. Math. 198 (1996), Thm 3.4 with Rem. 3.10: complete integrability (F = K_r), a hyperbolic
     periodic orbit with a coinciding separatrix, a fixed energy level, and the displacement measured by F.
   - **DONE**, checked at source.
   - **OPEN:** Lemma 3.8's proof (Robinson, ETDS 1988) was not read.
9. **(ii): nondegeneracy of the Melnikov zero.**
   - |L″(3π/2)| ≥ 8(|L₂| − 4|L₄| − T₃) = 1.22e−4, from certified L₂, L₄ and the T₃ tail bound.
   - **DONE.** The Arb certificate is in qsim/mn_melnikov/RESULT.md. The Stage-2 margin is thin (T₃ uses 68% of |L₂|) but
     positive.

## Computer-assisted-proof failure modes (the field's known false positives)
10. **Floating point leaking into "rigorous" code.**
    - A compile-time guard rejects any non-MPFR CAPD interval type, and trig goes only through range-checked wrappers.
    - **DONE** (guard_build.sh / check_proof_object.sh).
11. **NaN or ∞ swallowed by interval operations.** This is a known CAPD hazard: multiplication can absorb a NaN.
    - We caught it ourselves (A12.9): v4 requires every enclosure to be finite, and every decision is routed through
      certainly_* helpers.
    - The rerun was identical.
    - The second-library checker refuses non-finite dump entries; its must-fail cases fired.
    - **DONE.**
12. **The wrapping effect and wrong norms.**
    - A wrapping bug was caught by our own Kerr control (v2), and the derivative is now applied to thin vectors first
      (v3).
    - The second-library checker re-derived Y, Z, the cones and the sign tests from dumps, using exact rational
      coverage.
    - **DONE.**
13. **Decision arithmetic.**
    - It was re-evaluated in python-flint/Arb, from the stated formulas and not ported from the C++. The checker was
      written by the same AI session that wrote the C++, and a separate AI session read it: CORRECT.
    - **DONE.**
    - **OPEN:** this covers the decision layer, not the integrator.
14. **The integrator itself** (Taylor–Lohner enclosures, the Poincaré crossing, C¹ variational equations).
    - It rests on CAPD alone. There are an earlier differential check of CAPD against Arb (DIFFCHECK) and a positive
      control reproducing a published CAPD-based proof (CKMJ).
    - **OPEN:** a second validated integrator (Tier 2b) has not been run.
15. **Negative and positive controls.**
    - Kerr must not certify transversality, and does not.
    - Kerr's homoclinic family is certified.
    - A field sabotaged in one β² term gives a disjoint certificate.
    - A published proof (CKMJ) is reproduced.
    - **DONE.**
16. **Predictions and decision rules fixed before each computation.**
    - **DONE:** every rule and expected outcome was committed before its run (PREREG.md A1–A13; TIER2A_PREREG.md).
    - Deviations are disclosed, among them a mis-designed must-fail case (m1) and post-hoc substitutes.

## Reproducibility
17. **The environment is pinned.**
    - CAPD commit 2f06098, MPFR 4.2.2, GMP 6.3.0, python-flint 0.9.0, mpmath 1.3.0, Python 3.13.12, macOS (Apple
      silicon).
    - The binary sha256 values are logged (s2/binaries.txt).
    - **DONE.**
    - **OPEN:** there is no container or lock file. The versions are recorded, not packaged.
18. **How to rerun.**
    - Build capd/s2_main_v4.cpp with qsim/capd/tests/guard_build.sh, with CXXEXTRA="-I qsim/capd/horseshoe" (for
      gen/mn_field.h).
    - Run `s2_main_v4 {fp|cone|bvp|meet} s2/<case>/<stage>.spec <dump>` on the committed specs (s2/mn, kerr_i, sab_iii,
      meet_ii). This takes about 6 core-h for all four.
    - Then run `python tier1_check.py run` and `python tier2a/compare.py`.
    - **DONE** in substance.
    - **OPEN:** a one-command script and a README section with the exact commands.
    - The large control-(iv) specs are not committed (sha256 manifest); its bvp2 spec is committed gzipped.

## Not claimed (stated in the release notes)
- No entropy value.
- No other levels or orbit families.
- No explicit β₀ in (ii), so (ii) does not reach β = 3/100.
