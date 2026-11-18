# A general non-integrability theorem for Manko–Novikov geodesics: design

**Status: DESIGN, unreviewed. Nothing was run, built or launched to produce it.** No statement below is registered or
certified. It is input for an Opus review and then for registration by the Bridge.

**Model provenance.**
- Sections 1–9 (route comparison, theorem statements, all proofs and derivations): Claude Fable 5.2, session
  "Quantum-personal", 2026-11-18. Every derivation was done by hand; no computer algebra or numerics were used.
- LITERATURE.md (Step 0) and the two read-only digests of fleet results used in section 5: Claude Opus 5.5 subagents,
  briefed by Fable. Their findings are quoted with their own verification labels. LITERATURE.md lists what it could
  not verify; in particular the original Manko–Novikov paper was not opened (formulas are from reprints).
- Task brief: the Bridge, 2026-11-18 (general theorem for MN beyond the pointwise certificates; compare routes 1–4).

## 1. Summary

The pointwise certificates prove an obstruction at ten parameter rows. The question was which route gives a theorem
for a whole parameter family. My answer:

1. **Best route (section 4, Theorem 1): the symmetry-axis geodesic, analysed at the essential singularity x = 0.**
   On the axis the normal variational equation of ANY stationary axisymmetric vacuum spacetime is, exactly,
   `v'' + (3/16) (P'/P)^2 v = 0` with `P = E^2 - mu^2 f(z)` and `f = -g_tt` on the axis (Lemmas 1–2). For MN,
   `f` contains `exp(2 beta/x^3)`, so `P` has infinitely many zeros (complex turning points) accumulating at x = 0.
   Near x = 0 the equation converges, in the coordinate `sigma = 2 beta/x^3`, to a Fuchsian equation in
   `W = e^sigma` (static case: a hypergeometric equation with exponent differences `(0, 1/2, i sqrt(3)/2)`; rotating
   case: six regular singular points).
   That model has monodromy group Zariski-dense in SL(2,C), by an exponent argument that needs no computation.
   Density is an open condition, so the true equation inherits it.
   **Claimed conclusion: for every beta != 0, every rotation parameter, every energy E != 0 and every mu != 0, the
   identity component of the differential Galois group of the variational equation along the axis geodesic is not
   solvable, so the MN geodesic flow has no complete set of meromorphic first integrals in involution.** No
   certified computation is needed; the proof is analytic. It needs review, and cheap independent checks
   (section 7) can falsify it. Numbers the fleet already holds agree with it (section 5, H3 and H5).
2. **Route 2 (Poincaré–Kozlov) does not give a fixed-beta theorem.** It excludes integrals analytic in beta. I state
   what it does give (section 9.3).
3. **A fifth route, not in the brief, gives the real-analytic, fixed-small-beta statement plus chaos:** Melnikov's
   method along Kerr's homoclinic (zoom-whirl) orbits (section 9.2). It needs one certified integral.
4. **Routes 1 and 4** reduce to a cheap generic statement (section 9.1) and to a heavy box computation.

Position in the literature (LITERATURE.md): every published MN integrability result is numerical. The only
Morales–Ramis theorem found for a vacuum Weyl or stationary axisymmetric geodesic flow is Maciejewski–Przybylska–
Stachowiak 2013 for Zipoy–Voorhees, proved for delta = 2 on an equatorial solution with Kovacic's algorithm. No source
was found for the general axis equation of Lemma 1 (only explicit Kerr formulas, which agree with it), or for a
Galois argument at an essential singularity with accumulating singular points.

The class of integrals excluded by Theorem 1 is the usual Morales–Ramis class: meromorphic in a complex neighbourhood
of the complexified axis geodesic, including complex positions near x = 0 (r = M, inside the horizon). It says
nothing about integrals that are only real-analytic on the exterior. Section 9.2 is the route for those.

## 2. Setting and notation

Weyl–Papapetrou form, signature (-,+,+,+):

    ds^2 = -f (dt - omega dphi)^2 + f^{-1} [ e^{2 gamma} (drho^2 + dz^2) + rho^2 dphi^2 ].

Prolate spheroidal coordinates: `rho = k sqrt((x^2-1)(1-y^2))`, `z = k x y`. The axis outside the horizon is `y = 1`,
`x > 1`, where `z = k x`. Geodesic Hamiltonian `H = (1/2) g^{mu nu} p_mu p_nu = -mu^2/2`, with `E = -p_t`, `L = p_phi`.
A dot is the derivative in the affine parameter of H; a prime is d/dz.

MN (Manko–Novikov 1992) with Kerr-type parameter `alpha` (|alpha| < 1) and anomalous multipoles `alpha_n`:
`f = e^{2 psi} A/B`, `psi = sum_n alpha_n P_n(xy/R)/R^{n+1}`, `R = sqrt(x^2+y^2-1)`,

    A = (x^2-1)(1+ab)^2 - (1-y^2)(b-a)^2,
    B = [x+1+(x-1)ab]^2 + [(1+y)a + (1-y)b]^2,
    a = -alpha exp( - sum_n 2 alpha_n ( -1 + sum_{l=0}^{n} (x-y) P_l / R^{l+1} ) ),
    b =  alpha exp( sum_n 2 alpha_n ( (-1)^n + sum_{l=0}^{n} (-1)^{n-l+1} (x+y) P_l / R^{l+1} ) ).

The fleet's case is `alpha_2 = beta`, all other `alpha_n = 0`. Kerr is `alpha_n = 0`, with `M/k = (1+alpha^2)/(1-alpha^2)`
and `a/k = 2 alpha/(1-alpha^2)`. For n = 2 these are the forms in the fleet's two transcriptions (section 5, H1). The
general-n forms agree with Bambi–Barausse 2011, Appendix A, Eqs. (A10)–(A11), which that paper says correct typos in
the original (LITERATURE.md A.1). They matter only for Corollary 1a.

## 3. The routes compared

| Route | Theorem it can give | Class of integrals | Parameters covered | What it needs | Verdict |
|---|---|---|---|---|---|
| 1. Deformation / limit with semicontinuity of the Galois group | Specialisation only shrinks the group. From Kerr (beta = 0) nothing follows: the Kerr group is virtually abelian and that is compatible with anything at beta != 0. From one certified row it gives a GENERIC statement (9.1). The limit that works is not beta -> 0 or E -> infinity but the approach to x = 0 at fixed parameters: that is route 3* | meromorphic | generic (9.1); all (3*) | 9.1: analyticity of monodromy in parameters. 3*: section 6 | absorbed into 3* and 9.1 |
| 2. Poincaré–Kozlov | No first integral that is analytic in beta (or a formal series in beta) and independent of H. NOT: no analytic integral at each fixed small beta | real-analytic families | a neighbourhood of beta = 0, as a family | Kerr non-degeneracy; nonzero resonant coefficients on infinitely many resonant tori (V19 has 3, numerically) | weaker than asked; kept as 9.3 |
| 3. Galois theory over C(x, exp(2 beta/x^3)) on the axis | Non-solvable Galois group for the axis NVE | meromorphic | all beta != 0, all alpha, all E != 0, mu != 0 | Done here by local monodromy at the essential singularity (3*), not by a Kovacic-type algorithm. Singer's 1991 algorithm exists for C(x, exp(rational)) but is not needed, and it would give the weaker class: the group over C(x, e^r) can be larger than the group over M(Gamma) | **best: Theorem 1** |
| 4. Parameter-uniform certified monodromy over boxes | Obstruction at every point of compact boxes | meromorphic | compact boxes away from beta = 0 | many certified runs; cannot reach beta -> 0 or unbounded ranges | superseded if Theorem 1 survives review; otherwise the heavy fallback |
| 5. Melnikov along Kerr's homoclinic orbits (added) | Transversal homoclinic orbits, hence a horseshoe and no real-analytic integral, for each fixed small beta != 0 | real-analytic (and chaos) | generic (a, E, L_z) admitting a homoclinic orbit; 0 < \|beta\| < beta_0(a, E, L_z) | one certified integral (a Melnikov function with a simple zero) | complements Theorem 1; section 9.2 |

Why 3* wins. It is the only route that reaches every beta != 0 with a proof that does not depend on a computation, and
its mechanism is specific to what distinguishes MN from Kerr: the essential singularity that the anomalous multipole
puts on the axis. Kerr has finitely many singular points on the axis and its group is dihedral-type; Zipoy–Voorhees
delta = 2 likewise (section 8, retrodictions).

## 4. Theorem statements

**Theorem 1 (claimed).** Let g be an MN metric with k > 0, |alpha| < 1 and anomalous quadrupole `alpha_2 = beta != 0`
(all other alpha_n = 0). Let E != 0 and mu != 0, and let Gamma be the complexified axis geodesic: the Riemann surface
`{ (z, zdot) : zdot^2 = E^2 - mu^2 f(z) }` over the z-domain where f is holomorphic and nonzero, with the points over
`x = +-1` removed. Then:

(i) the differential Galois group, over the field of meromorphic functions on Gamma, of the variational equation of H
along Gamma has an identity component that is not solvable (it has PSL(2,C) as a quotient);

(ii) consequently H has no four first integrals that are meromorphic on a neighbourhood of Gamma in the complexified
phase space, pairwise in involution, and functionally independent on that neighbourhood. In particular there is no
fourth such integral completing H, p_t, p_phi;

(iii) in the fleet's formulation: for every E != 0 and mu != 0 the reduced two-degree-of-freedom flow `H_{E, L=0}` in
(x, theta) has no additional first integral meromorphic in a neighbourhood of the axial phase curve. (Its NVE in
delta-theta is equation (1) of section 6 up to the gauge factor `sqrt(g^{theta theta})`.)

The static sub-family alpha = 0 (Schwarzschild plus the MN quadrupole) is included.

**Corollary 1a (claimed, same proof).** The same holds for any finite set of anomalous multipoles alpha_n with at
least one alpha_n != 0.

**Proposition (Lemmas 1–2; claimed for every stationary axisymmetric vacuum metric with a regular axis).** Along the
axis geodesic the transverse variational system is equivalent to

    chi'' * P + (1/2) P' chi' + (1/4) P'' chi = 0,   P(z) = E^2 - mu^2 f(z),   f = -g_tt on the axis,

equivalently `v'' + (3/16)(P'/P)^2 v = 0` for `v = P^{1/4} chi`. The twist potential drops out, and E enters only
through P.

What Theorem 1 does not say: nothing about null geodesics (mu = 0: the axis equation is trivial), nothing about
first integrals that are not meromorphic near Gamma, and nothing quantitative about chaos.

## 5. Hypotheses of Theorem 1 and their status

Status words: FLEET = supported by a fleet result (file, commit); HAND = proved or derived by hand in section 6, not
machine-checked; LIT = a published theorem (see LITERATURE.md); COMPUTE = needs a new computation; OPEN.

| # | Hypothesis | Status | Evidence / what is missing |
|---|---|---|---|
| H1 | The MN metric functions are those of section 2 | FLEET, with limits | ansatz's package `conjecture_machine/data/MN_for_quantum/MN_METRIC.md` and `scripts/_mn_build.py:42-66` (a transcription of the Gair–Li–Mandel form, with one correction, +8 beta in gamma). Vacuum is checked exactly but pointwise, in a formal field, at 3 points per parameter set; Kerr limit symbolic. The Bridge's independent transcription `V9_mn_obstruction_check/code/v9_nve.py:8-23` agrees to 1e-15. Only p1 = (5, 3, 1/5) and p2 = (13, 5, -1/3) were built. A full symbolic vacuum identity for general (M, a, beta) is NOT in the fleet |
| H2 | Regular axis: omega = 0 and gamma = 0 on y = 1, as identities in x | FLEET at p1, p2; HAND in general | Gate G1 of `PREREG_mn_axis_certified_monodromy.md` (verdict 2ce8b41; `qsim/mr_mn_G1.json`): omega(y = +-1) = 0 exactly at both points. e^{2 gamma} = 1 on the axis at both points (MN_METRIC.md). For general parameters: Lemma 3 gives omega = 0; and at y = 1, `E_Q = 1`, `E_A = E_B = e^{-2 beta/x^3}`, `A = (x^2-1)(1-alpha^2)^2`, so e^{2 gamma} = 1 (hand). C1 confirms |
| H3 | Lemma 1 (axis equation (1)) | HAND; supported by FLEET numbers | Derivation in 6.1. Independent support: (a) the fleet's certified ZV delta = 2 axial generator trace, -85.03 (axis prereg, G2 control), equals `-2 cosh(pi sqrt(2))` = -85.03, which is what (2) predicts for the double pole of P at x = -1; (b) the Kerr control loops have traces 0 to 1e-21, "elliptic of order 4", as (2) predicts at simple zeros and poles of P; (c) the fleet's first-integral relation `xdot^2 = (E^2 - mu^2 f(x,1))/k^2` is P. The exact identity "xi_1 form = (2)" is check C2 |
| H4 | Lemma 2 (normal form (2), exponents) | HAND | elementary |
| H5 | Lemma 3 (formula (3) for f on the axis) | HAND; reproduced by the Opus digest; supported by FLEET numbers | The digest derived the same a(x,1), b(x,1), A, B, C, f independently. By hand: at p1, the located singular point 0.58054 + 0.20511 i of the certificate satisfies `4x + 5 = 3 i e^{2 beta/x^3}` to 4 digits (a zero of B(x,1), i.e. a pole of P), and the real point 1.84145 at level (E, mu^2) = (1, 4) gives f_0 = 0.25000 = E^2/mu^2 (a zero of P). C1 confirms symbolically |
| H6 | Lemma 4 (model group dense) | HAND; static case also LIT | 6.5. Uses Frobenius theory at regular singular points and the list of algebraic subgroups of SL(2,C). For the static model, Kimura 1969, Theorem I (p. 277), which allows complex exponent differences, gives independently that `(0, 1/2, i sqrt(3)/2)` is not solvable (LITERATURE.md B.3). C4 is a machine check |
| H7 | Lemma 5 (density is open), and 6.5(d) | HAND | 6.6. Uses Burnside's theorem (a finitely generated linear torsion group of bounded exponent is finite) |
| H8 | Lemma 6 (convergence to the model) | HAND | 6.4. C3 and C5 test it |
| H9 | Over M(Gamma), Gamma non-compact, the Galois group is the Zariski closure of the monodromy group | LIT | Morales-Ruiz–Ramis, Methods Appl. Anal. 8 (2001), Theorem 7 (p. 72), states it as part of the theorem; their Theorem 12 (appendix) sets up connections on an arbitrary Riemann surface with a discrete set of poles (read by the Opus agent; LITERATURE.md B.1). Used in the same way by the fleet (axis prereg :29-33: "an essential singularity (here x = 0) is simply a puncture of Gamma") |
| H10 | Morales–Ramis for the integral curve without points at infinity | LIT | Same Theorem 7: n meromorphic first integrals in involution, independent over a neighbourhood of the curve (not necessarily on it), force the identity component of the Galois group of the VE over Gamma to be abelian; Corollary 8 (p. 79) is the NVE form. This is the version the fleet's certificates cite. Outside Lean, as for the existing certificates |
| H11 | H is holomorphic near Gamma at complex x close to 0 | HAND | 6.7, last paragraph. The reviewer should check the branch (R = x on the continued axis) |
| H12 | A finite-j, pointwise version at a fleet row | COMPUTE (optional) | C6. The Lean theorem `L6_gl2` (`lean/ZiglinCert/ZiglinCert/Certificate.lean:307-316`, build a7b6add) already turns two certified matrices with tr^2/det outside [0,4] and tr[G,H] != 2 into "no finite-index subgroup is abelian" |

Relation to the existing certificates. They certify an obstruction at four axial rows (E = 1, mu^2 in {4, 9}, at p1 and
p2; 2ce8b41; replayed by CAPD, `qsim/capd/MR_REPLAY.md`, 24/24) and six equatorial rows (v2 FINAL 5da26fe). Their
loops stay at |x| >= 0.35 and none encloses x = 0. The documents contain no analysis near x = 0, no statement for all
beta or all E, and no genericity argument. Theorem 1 is about the region they exclude.

One observation, not a test. At p1, level (1, 9), the certified loop h around the located point 0.0634 + 0.4514 i
(radius about 0.12) has trace -229.723 + 8.646 i in the xi_1 normalisation. By my estimate that loop encloses the
first two turning points of the lattice of section 6.4 (near 0.08 + 0.47 i and 0.02 + 0.35 i). The static model gives
`-(4 + 2 cosh(pi sqrt(3)))` = -234.77 for two consecutive turning points. The rotating model and the finite-sigma
corrections change this value, so a 2% agreement proves nothing; but what the loop encloses is cheap to settle (C0
below), and it is the first place to look.

## 6. The hardest step, attempted in full: proof of Theorem 1

The proof has six lemmas. Lemmas 1–3 are computations done by hand here; section 7 lists the machine checks that
should confirm them. Lemmas 4–6 are the new argument.

### 6.1 Lemma 1 (the axis variational equation of a stationary axisymmetric vacuum metric)

**Hypotheses.** f, omega, gamma are analytic functions of (rho^2, z) near a piece of the axis rho = 0; they satisfy the
vacuum equations; omega = O(rho^2) and gamma = O(rho^2) (regular axis). All of this is preserved by analytic
continuation in z, so it holds on the complexified axis wherever the functions stay analytic.

**Statement.** The axis is a geodesic with `tdot = E/f_0`, `zdot^2 = E^2 - mu^2 f_0(z)`, where `f_0(z) = f(0, z)`. Write
`zeta = xi + i eta` for the transverse Cartesian displacement. Then `zeta = sqrt(f_0) e^{-i theta} chi` with
`thetadot = (1/2) E w f_0` turns the transverse variational equation into

    chiddot = (mu^2/4) f_0''(z) chi.                                                    (1)

**Proof.** Near the axis write `f = f_0 + rho^2 f_2 + O(rho^4)`, `gamma = rho^2 gamma_2 + O(rho^4)`,
`omega = (1/2) w rho^2 + O(rho^4)`. Let c be the twist potential (Ernst potential `f + i c`), c_0 its axis value.
- Real part of the Ernst equation, `f Lap f = |grad f|^2 - |grad c|^2`, on the axis (`Lap f = 4 f_2 + f_0''`):
  `4 f_0 f_2 = f_0'^2 - c_0'^2 - f_0 f_0''`.
- `gamma_rho = (rho/(4 f^2)) (f_rho^2 - f_z^2 + c_rho^2 - c_z^2)` gives `gamma_2 = -(f_0'^2 + c_0'^2)/(8 f_0^2)`.
- `f^2 grad omega = +- rho e_phi x grad c` gives `w^2 = c_0'^2 / f_0^4`.

With `omega dphi = (1/2) w (xi d eta - eta d xi)` and E = f (tdot - omega phidot) conserved, the Routhian (t eliminated)
to second order in (xi, eta) is

    R = E^2/(2f) + (1/2) E w (xi etadot - eta xidot) + (1/(2f)) e^{2 gamma} (zdot^2 + xidot^2 + etadot^2).

Its transverse Euler–Lagrange equations combine to

    d/dtau( zetadot / f_0 ) + i E w zetadot + (i/2) E w' zdot zeta = K zeta,
    K = -E^2 f_2/f_0^2 + zdot^2 ( 2 gamma_2/f_0 - f_2/f_0^2 ).

Put `zeta = g chi`, `g = sqrt(f_0) e^{-i theta}`, `gdot/g = fdot_0/(2 f_0) - (i/2) E w f_0`. The chidot terms cancel, the
imaginary part of the chi coefficient cancels identically, and with `psi = (1/2) ln f_0`, `zddot = -mu^2 f_0 psi'`:

    chiddot = [ f_0 K - psiddot + psidot^2 - (E w f_0)^2/4 ] chi.

Insert `zdot^2 = E^2 - mu^2 f_0`. The coefficient of E^2 is
`-2 f_2/f_0 + 2 gamma_2 - psi'' + psi'^2 - c_0'^2/(4 f_0^2)`; using the three axis relations, the f_0'^2/f_0^2 terms sum to
`-1/2 - 1/4 + 3/4 = 0`, the c_0'^2/f_0^2 terms to `1/2 - 1/4 - 1/4 = 0`, and the f_0''/f_0 terms to `1/2 - 1/2 = 0`.
The coefficient of mu^2 is `-2 f_0 gamma_2 + f_2 + f_0 psi'' = f_0''/4`. This is (1). QED.

Checks done by hand (mu = 1): Schwarzschild, `f_0 = 1 - 2M/r`, gives `chiddot = -(M/r^3) chi`, the transverse tidal
equation of a radial geodesic. Kerr, `f_0 = 1 - M/(r+ia) - M/(r-ia)`, gives
`chiddot = -Re[ M/(r-ia)^3 ] chi = -[ M r (r^2 - 3a^2)/(r^2+a^2)^3 ] chi`, which is the published on-axis tidal
coefficient of Kerr (Lima Junior, Crispino, Higuchi 2020, Eqs. 33–36; the Opus agent made the same comparison
independently, LITERATURE.md A.8). The vanishing of the E^2 terms is boost invariance along the axis: by axial
symmetry only Psi_2 is nonzero there, for any stationary axisymmetric metric, and the derivation above does not
assume type D.

The variational equation of H along the axis geodesic splits, by axial symmetry, into a longitudinal block (t, z) and
this transverse block; so the transverse block is a direct summand of the full variational equation.

### 6.2 Lemma 2 (normal form)

With `P = E^2 - mu^2 f_0` we have `zdot^2 = P`, so `d^2/dtau^2 = P d^2/dz^2 + (1/2) P' d/dz`, and `f_0'' = -P''/mu^2`.
Equation (1) becomes `P chi'' + (1/2) P' chi' + (1/4) P'' chi = 0`. Put `chi = P^{-1/4} v`:

    v'' + (3/16) (P'/P)^2 v = 0.                                                         (2)

At a zero or pole of P of order m the point is regular singular with exponents solving `s(s-1) = -3 m^2/16`:
`1/4, 3/4` for m = 1 (the fleet's local coefficient b = -3/16), `1/2 +- i/sqrt(2)` for m = 2.

### 6.3 Lemma 3 (MN on the axis)

At y = 1: `R = x`, `P_l(xy/R) = 1`, `psi = sum_n alpha_n x^{-n-1}`. Write `W = e^{2 psi}`; for the fleet's case
`W = exp(2 beta/x^3)`. The geometric sums give `sum_{l=0}^{n} (x-1) x^{-l-1} = 1 - x^{-n-1}` and
`sum_{l=0}^{n} (-1)^{n-l+1} (x+1) x^{-l-1} = (-1)^{n+1} - x^{-n-1}`, hence

    a(x,1) = -alpha W,     b(x,1) = alpha / W,     ab = -alpha^2,
    A = (x^2-1)(1-alpha^2)^2,     B = [(1-alpha^2) x + (1+alpha^2)]^2 + 4 alpha^2 W^2,
    C = 2 alpha W (x^2-1)(1-alpha^2)   so   omega = 2k e^{-2psi} C/A - 4k alpha/(1-alpha^2) = 0 on the axis,

    f_0 = W (x^2-1)(1-alpha^2)^2 / ( [(1-alpha^2)x + (1+alpha^2)]^2 + 4 alpha^2 W^2 )
        = W (r^2 - 2Mr + a^2) / ( r^2 + a^2 W^2 ),     r = kx + M.                       (3)

So on the axis MN is "Kerr with a^2 -> a^2 W^2 in the denominator, times W". The static case alpha = 0 is
`f_0 = W (x-1)/(x+1)`. The identity omega = 0 on the axis is a consistency check on the signs of a and b.

### 6.4 The local coordinate at the essential singularity, and Lemma 6 (convergence)

Take the quadrupole case; the general case is identical with `sigma = 2 psi(x,1)`. Put `sigma = 2 beta / x^3`, so
`W = e^sigma`. On any disc that avoids sigma = 0, `x = (2 beta/sigma)^{1/3}` is a single-valued injective analytic
function, so closed loops in the sigma-disc are closed loops in the x-plane. In the variable sigma, equation (2) is

    v_ss + (4/(3 sigma)) v_s + (3/16) ( d ln P / d sigma )^2 v = 0,                      (4)

because `sigma_zz / sigma_z^2 = 4/(3 sigma)` exactly. By (3), `f_0 = W G(x, W)` with G rational in (x, W) and analytic
at x = 0. Put eps = mu^2/E^2 and

    F(W) = W G(0, W) = - W (1-alpha^2)^2 / ( (1+alpha^2)^2 + 4 alpha^2 W^2 ),     Q(W) = 1 - eps F(W).

**The model equation** is

    v_ss + (3/16) ( d ln Q(e^s) / ds )^2 v = 0,   i.e.   v_WW + v_W / W + (3/16) (Q'/Q)^2 v = 0.     (5)

**Lemma 6.** Fix a compact set K' in the s-plane that avoids the singular set of (5) (the points where Q(e^s) is 0 or
infinite; this set is 2 pi i-periodic). For the translates `K'_j = K' + 2 pi i j`, the coefficients of (4), read in the
variable `s = sigma - 2 pi i j`, converge uniformly on K' to those of (5) as j -> infinity. Hence the monodromy
matrices of (4) along any fixed finite set of loops in K'_j, in the basis normalised at a base point of K'_j, converge
to the monodromy matrices of (5) along the same loops in K'.

*Proof.* On K'_j, `|sigma| >= 2 pi j - const`, so `x = (2 beta/sigma)^{1/3} -> 0` uniformly and `4/(3 sigma) -> 0`. Since
`e^sigma = e^s`, `P/E^2 = 1 - eps e^s G(x(sigma), e^s) -> Q(e^s)` uniformly on K', where Q is finite and nonzero; uniform
convergence of analytic functions gives convergence of the s-derivative. Solutions of a linear ODE depend continuously
on the coefficients along compact paths. The Wronskian of (4) is proportional to sigma^{-4/3}, single-valued on K'_j,
so the monodromy matrices of (4) have determinant 1. QED.

For large j the singular points of (4) in K'_j (zeros and poles of P, which are the only singular points of (2) other
than x = 0) lie in small discs around the model's singular points (Hurwitz); the loops are chosen outside those discs.

So: **at fixed parameters, the lattice of complex turning points and poles approaching x = 0 looks more and more like
the periodic model (5).** No limit in beta or E is taken.

### 6.5 Lemma 4 (the model group is dense in SL(2,C))

Equation (5) in the variable W is Fuchsian on the Riemann sphere:
- W = 0: Q(0) = 1, so the coefficient of v is analytic; exponents (0, 0). The local monodromy T is unipotent and not
  the identity (equal exponents always produce a logarithm).
- zeros and poles of Q of order m: exponents solving `s(s-1) = -3m^2/16`.
- W = infinity:
  - static case alpha = 0: `Q = 1 + eps W`, `W Q'/Q -> 1`, exponents `+- i sqrt(3)/4`. With u = eps W, (5) is
    `u^2 v_uu + u v_u + (3/16)(u/(1+u))^2 v = 0`: a Riemann (hypergeometric) equation with singular points 0, -1,
    infinity and exponent differences `(0, 1/2, i sqrt(3)/2)`.
  - rotating case alpha != 0: `Q = (ah^2 W^2 + eps W + m^2)/(ah^2 W^2 + m^2)` with `m = M/k`, `ah = a/k`. Then Q -> 1,
    exponents (0, 0) at infinity. The finite singular points are the two zeros `W_+-` of `ah^2 W^2 + eps W + m^2` and the
    two poles `+- i m/ah`: six singular points in all.

Let K be the monodromy group of (5) on the W-sphere minus the singular points; K is in SL(2,C).

**(a) K is irreducible.** A common eigenvector is a solution `v_0 = prod_i (W - a_i)^{s_i} q(W)`, with a_i the finite
nonzero singular points, s_i a local exponent there, q a polynomial, and no factor of W (the eigenvector of T is the
solution holomorphic at 0). At infinity `v_0 ~ W^{sum s_i + deg q}`, and that power must be minus an exponent at
infinity.
- Static: the required power is `+- i sqrt(3)/4`, not real, but `s_1 + deg q` is real (s_1 is 1/4 or 3/4).
- Rotating, simple zeros: the required power is 0, but `sum s_i + deg q >= 4 * (1/4) = 1`.
- Rotating, double zero (eps = 2 m ah): the exponents at the double zero are `1/2 +- i/sqrt(2)`, at the two poles
  1/4 or 3/4; the sum has imaginary part `+- 1/sqrt(2)`, not 0.
In every case there is no common eigenvector.

**(b) The Zariski closure of K is SL(2,C).** A proper algebraic subgroup of SL(2,C) that is irreducible is finite or
lies in the normaliser of a torus; all its elements are semisimple. K contains T, unipotent and not the identity.

**(c) The loops that exist in the x-plane.** Loops near x = 0 are loops in the s-plane, the universal cover of the
punctured W-plane. Their classes form the kernel of the winding number around W = 0, a normal subgroup; its image H is
normal in K and K = H<T>. The closure of H is normalised by the closure of K, so it is a closed normal subgroup of
SL(2,C): trivial, {+-1}, or SL(2,C). If H were central, K would be abelian, contradicting (a).
**So H is Zariski-dense in SL(2,C).**

**(d) A finitely generated dense subgroup exists.** Write H as an increasing union of finitely generated H_n. If none
were dense, infinitely many would be of one type: reducible (then the nonempty closed sets of invariant lines are
nested, so H has an invariant line); in a torus normaliser (same argument with invariant pairs of lines); or finite of
order at most 120 (then the chain is stationary and H is finite). Each contradicts (c).

**(e) An explicit pair in the static case.** Normalise `T = [[1,1],[0,1]]` and, by a conjugation that fixes T,
`R = [[0,-1/c],[c,0]]` with `c = tr(TR) = 2 cosh(pi sqrt(3)/2)`. The turning points of the lattice have monodromies
`R_j = T^{-j} R T^{j}`. Then

    h_1 = R_0 R_1 = [[-1, -1], [-c^2, -1-c^2]],     h_2 = R_1 R_2 = T^{-1} h_1 T = [[c^2-1, 2c^2-1], [-c^2, -1-2c^2]],
    tr h_1 = tr h_2 = -(c^2+2),     tr(h_1 h_2) = 2 + 4c^2,     tr[h_1, h_2] = 2 - 4 c^6.

With `c^2 = 2 + 2 cosh(pi sqrt(3))`, about 232.769: `tr h_i` is about -234.769 and `tr[h_1,h_2]` about -5.04e7. Both
h_i are loxodromic and they share no eigenvector. That is exactly the hypothesis of the fleet's Lean theorem `L6_gl2`
(no finite-index subgroup of <h_1, h_2> is abelian). These are strict inequalities, so by Lemma 6 they hold for the
true equation for all large j. **In the static case the conclusion "G^0 is not abelian" therefore needs neither
Lemma 5 nor the classification of subgroups, only Lemma 6 and this 2x2 computation.**

### 6.6 Lemma 5 (density is an open condition)

The set of m-tuples of SL(2,C) that generate a Zariski-dense subgroup is open. Proof: let tuples A_n -> A with every
<A_n> not dense. Passing to a subsequence, all are reducible, or all preserve a pair of lines, or all generate finite
groups of order at most 120. In the first two cases the invariant line (pair) has a convergent subsequence and the
limit is invariant under A. In the third, every word w satisfies `w(A_n)^{120!} = 1`, so `w(A)^{120!} = 1`; a finitely
generated linear torsion group of bounded exponent is finite (Burnside). So <A> is not dense. QED.

### 6.7 Assembly

1. By 6.5 choose finitely many loops in the s-plane whose model monodromies generate a dense subgroup of SL(2,C). By
   Lemmas 5 and 6, for all large j the monodromies of the true equation (2) along the corresponding loops near x = 0
   generate a dense subgroup of SL(2,C). This holds for every beta != 0, |alpha| < 1, E != 0, mu != 0.
2. From v to chi and to Gamma. `chi = P^{-1/4} v`, and Gamma is the double cover `zdot^2 = P`. The z-loops that lift to
   closed loops on Gamma form a subgroup of index at most 2; its v-monodromy group D_0 is still dense (a finite-index
   subgroup of a dense subgroup of a connected group). Along such a loop c, `P^{-1/4}` changes by a sign, so the
   chi-monodromy of c^2 is the square of the v-monodromy of c. The group generated by the squares of D_0 is normal in
   D_0, so its closure is a closed normal subgroup of SL(2,C); it is not central, because `g^4 = 1` is a closed
   condition that fails on SL(2,C). So it is dense, and the monodromy group of equation (1) on Gamma is dense in
   SL(2,C).
3. Over the field of meromorphic functions on a non-compact Riemann surface, a function of the solutions fixed by the
   monodromy is a single-valued meromorphic function, so the Galois group is the Zariski closure of the monodromy
   group. So the Galois group of (1) over M(Gamma) is SL(2,C).
4. From chi to the transverse block. The transverse solutions are `zeta_+ = sqrt(f_0) e^{-i theta} chi_a` and
   `zeta_- = sqrt(f_0) e^{+i theta} chi_b`, and `zeta_+ zeta_- = f_0 chi_a chi_b`. So the Picard–Vessiot extension of the
   transverse block contains that of the symmetric square of (1), whose Galois group is PSL(2,C). Hence PSL(2,C) is
   a quotient of the Galois group of the transverse block, and of the full variational equation. The identity
   component maps onto PSL(2,C) (connected), so it is not solvable. This is Theorem 1(i).
5. Morales–Ramis (the version for the integral curve without points at infinity): n meromorphic first integrals in
   involution, independent in a neighbourhood of Gamma, force the identity component of the Galois group of the
   variational equation over M(Gamma) to be abelian. This contradicts 4 and gives Theorem 1(ii).

The Hamiltonian is holomorphic near Gamma: for complex x_0 not 0 or +-1, (x, y) are analytic functions of (rho^2, z)
near the axis point (the Jacobian there is `2 k^3 (x_0^2 - 1)`), R is nonzero, and gamma = 0, omega = 0 on the axis by
analytic continuation; poles of f_0 and the points x = +-1 are removed from Gamma. The axis inside the horizon
(|x| < 1, y = 1) is reached from the exterior axis by continuation around z = k.

### 6.8 Where each restriction is used

- beta != 0 (some alpha_n != 0): the essential singularity, hence the infinite lattice of singular points and the
  coordinate sigma. For Kerr, P is rational with two zeros and two poles, all with exponent difference 1/2.
- mu != 0: for null geodesics P is constant and (2) is v'' = 0.
- E != 0: eps is finite. (E = 0 has a different model; not treated.)
- |alpha| < 1, k > 0: only to have the MN family as given; the argument is algebraic in alpha.

## 7. Computations that would close the gaps, and who should do them

None of these is needed for the logic of section 6; they check it. All are small.

| # | Computation | Purpose | Tool / owner | Size |
|---|---|---|---|---|
| C0 | For each certified MN axial loop (2ce8b41 and the VREPRO pairs), count the zeros and poles of `P = E^2 - mu^2 f(x,1)` inside it (argument principle) | settles what the existing loops enclose; tests the rule "one simple zero or pole inside gives trace 0 in the xi_1 form"; identifies the p1 (1,9) loop with trace -229.72 | quantum (Arb); the Bridge in floats | seconds |
| C1 | Substitute y = 1 in the implemented MN functions and simplify: `f(x,1)`, `omega(x,1)`, `gamma(x,1)`, `a(x,1)`, `b(x,1)` | confirms Lemma 3, i.e. formula (3), and the regular-axis hypotheses | quantum (sympy on its MN package); the Bridge repeats on the V9 transcription | seconds |
| C2 | Show that the axis NVE the certificates use (the "xi_1 form") is equation (2) with `P = E^2 - mu^2 f(x,1)`. In the notation of `qsim/mr_mn_axis.py` (A = g^{theta theta} on the axis, X = xdot^2, B = d^2H/dtheta^2, ' = the exact derivation D) this is the single identity `B = X''/(4A) - X'A'/(4A^2) + 3 X A'^2/(4A^3) - X A''/(2A^2)` in Q(x, E), equivalently `r_xi1 + (3/16)(X'/X)^2 = 0`. Independently, expand H to second order in transverse Cartesian coordinates for a general Weyl–Papapetrou metric and reproduce (1) | confirms Lemmas 1–2 | quantum (sympy); ansatz for the independent general derivation | seconds to minutes |
| C3 | **Static falsification test.** alpha = 0 (Schwarzschild plus MN quadrupole), any beta != 0 and any E, mu (say beta = 1/5, mu = 1, E = 0.95). Locate the axis turning points x_j near x = 0 (zeros of `E^2 - mu^2 e^{2 beta/x^3} (x-1)/(x+1)`). Certify the monodromy of (2), in the chi normalisation, around a simple closed loop enclosing exactly x_j and x_{j+1}, for a range of j | tests the model (5), Lemma 6 and the whole mechanism with two numbers: the trace must tend to `4 + 2 cosh(pi sqrt(3))`, about 234.769 (hand-evaluated; recompute), with a correction of relative order 1/j; and for the loops around (x_j, x_{j+1}) and (x_{j+1}, x_{j+2}) the commutator trace must tend to `2 - 4 (2 + 2 cosh(pi sqrt(3)))^3`, about -5.04e7 (section 6.5(e)). A loop around a single x_j must give a reflection (trace 0, det -1) exactly | quantum (ia_hub or the v2 Rust/Arb core); the Bridge reproduces in floats | minutes |
| C4 | The model equation (5) has rational coefficients in W. Run the existing Kovacic / Morales–Ramis tool on it: static model (hypergeometric), and the rotating model at the fleet's (alpha, eps) rows | independent confirmation of Lemma 4: expected "no Liouvillian solution, group SL2" | quantum (`qsim/mr_*.py`) | seconds to minutes |
| C5 | At one fleet row, compare the true monodromy tuple on a cell of singular points near x = 0 (j = 5, 10, 20) with the model's | tests Lemma 6 in the rotating case | quantum (v2 core) | minutes |
| C6 | Optional: an Arb certificate of density for the true tuple at one finite j and one row | a pointwise certificate near x = 0 that does not rest on the limit argument | quantum | minutes to an hour |
| C7 | Optional: formalise Lemmas 4(b)–(d) and 5 (group theory only) next to `lean/ZiglinCert` | proof-grade record of the group-theoretic step | quantum (Lean) | open-ended |
| C8 | Only for the fallback 9.2: a certified enclosure of the Melnikov function at two phases with opposite signs, and of its derivative between them, at one parameter point (the static limit has an elementary homoclinic orbit) | Theorem 2 | quantum (Arb quadrature with explicit tail bounds); the Bridge in floats | hours |

Where the constant in C3 comes from. In the static model let T be the monodromy at W = 0 (unipotent), R the one at
the turning point (eigenvalues +-i in the v normalisation, so R^2 = -1 and tr R = 0), and `c = tr(TR) = 2 cosh(pi sqrt(3)/2)`
(the monodromy at infinity has eigenvalues `exp(+- pi sqrt(3)/2)`). Consecutive turning points have monodromies R and
`T^{-1} R T`. A direct 2x2 computation with `T = [[1,1],[0,1]]`, `R = [[p,q],[c,-p]]`, `p^2 + qc = -1` gives
`tr(R T^{-1} R T) = -(c^2 + 2)`. In the chi normalisation the sign flips (two simple zeros of P), so the trace is
`c^2 + 2 = 4 + 2 cosh(pi sqrt(3))`.

## 8. What would falsify the route

- F1. C1 fails: the on-axis f is not (3). The model changes and section 6.5 must be redone. (The mechanism only needs
  `f_0 = W G(x, W)` with G rational, a unipotent local monodromy at W = 0, and the exponent count in 6.5(a).)
- F2. C2 fails: the axis NVE is not (2).
- F3. C3 fails: the two-turning-point trace does not tend to 234.769. That refutes the model or Lemma 6.
- F4. The existing axis certificates contradict the local structure: every loop around one simple turning point must
  have, in the v (xi_1) normalisation, eigenvalues +-i. The digest in section 5 reports what the certificates show.
- F5. A stationary axisymmetric vacuum metric that is known to be meromorphically integrable and whose axis function f
  has an essential singularity of this kind. I know of none, and LITERATURE.md found none.
- F6. The Morales–Ramis theorem for a non-compact Gamma, or the identification "Galois group over M(Gamma) = closure
  of monodromy", is not what section 6.7 assumes. LITERATURE.md B.1 quotes Theorem 7 and it is what 6.7 assumes; the
  reviewer should still read the hypotheses on the symplectic manifold and on Gamma in the original.
- F7. An error in sections 6.1–6.7 found by the Opus review.

Retrodictions the route already passes (no new computation):
- Kerr: P has two zeros and two poles (r = +- ia), exponent differences 1/2 at all four, infinity ordinary. This is
  the solvable, dihedral-type case, consistent with the tool's "no certificate" on Kerr.
- Zipoy–Voorhees delta = 2: `f_0 = ((x-1)/(x+1))^2`, so (2) has three singular points with exponent differences
  `(1/2, 1/2, i sqrt(2))`, which is the dihedral row of Kimura's table: solvable. This matches the fleet's record that
  ZV gave no axial certificate (its positive control was equatorial).
  Quantitatively: the double pole of P at x = -1 has exponents `1/2 +- i/sqrt(2)`, so its local monodromy has trace
  `-2 cosh(pi sqrt(2))` = -85.03. The fleet's certified ZV axial run found exactly two generators, with traces -85.03
  and about 0.
- The local coefficient -3/16 at turning points matches the fleet's b = -3/16.

## 9. Fallbacks and complements

### 9.1 Generic non-integrability from one certificate (routes 1 and 4, minimal form)

**Theorem B (provable from existing certificates plus analyticity).** Let p range over a connected complex-analytic
family of parameters (k, alpha, beta, E, mu) on which the singular points used by a certificate move without
colliding, and let `M_1(p), M_2(p)` be the certified monodromy matrices transported along the family. If at one
p_0 the group generated is Zariski-dense in SL(2,C), then it is dense for all p outside a countable union of proper
analytic subsets: the zero set of `tr[M_1, M_2] - 2`, the zero sets of `tr M_1`, `tr M_2`, `tr M_1 M_2`, and the level
sets `tr M_1 = 2 cos(2 pi q)`, q rational. Each is a proper analytic subset because it misses p_0. On real parameters
the exceptional set is meagre and of measure zero.

This is the precise content of "semicontinuity": a certificate at one point spreads to generic points, never to all
points, and from the integrable point beta = 0 nothing spreads. The literature check found the subgroup statement
(the Galois group of a specialisation is a subgroup of the generic one: Seiss, Theorem 0.1; Goldman 1957, not opened)
but not this countable-union form, and Feng–Wibmer note that good specialisations need not form a Zariski-open set.
The proof sketched here is direct and does not use those results. It needs only the analytic dependence of the
transported monodromy, which holds away from collisions of singular points. If Theorem 1 fails review, this is the
statement that survives at no cost.

### 9.2 Melnikov along Kerr's homoclinic orbits (real-analytic class, fixed small beta, chaos)

Reduce at fixed (E, L_z), mu = 1. In Mino time the Kerr Hamiltonian separates on its zero level:
`K_0 = Sigma (H_0 + 1/2) = K_r(r, p_r) + K_theta(theta, p_theta)`. For (E, L_z) with E < 1 in the range where the radial
potential has a double root r_u (an unstable spherical orbit) and a further turning point outside it, the reduced flow
has a hyperbolic periodic orbit (r = r_u, theta librating with Mino frequency Upsilon_theta) whose stable and unstable
manifolds coincide (the zoom-whirl separatrix). Define `K_beta = Sigma_Kerr (H_beta + 1/2) = K_0 + beta K_1 + O(beta^2)`,
analytic near the separatrix, which lies outside the horizon. The Melnikov potential and function are

    Lm(psi_0) = Int_{-inf}^{inf} [ K_1( z_h(lambda), psi_0 + Upsilon_theta lambda ) - K_1( z_u, psi_0 + Upsilon_theta lambda ) ] d lambda,
    M(psi_0) = Upsilon_theta dLm/dpsi_0 = Int {K_r, K_1} d lambda,

where z_h is the homoclinic radial motion, z_u the saddle, and psi_0 the theta-phase. This is exactly the
Holmes–Marsden setting `F(q,p) + G(I) + eps H_1`.

**Theorem 2 (conditional on one computation).** If M has a simple zero, then for all sufficiently small beta != 0 the
reduced MN flow on the level has transversal homoclinic orbits to a hyperbolic periodic orbit; hence a horseshoe,
positive topological entropy, and no real-analytic first integral independent of H on a neighbourhood of the
homoclinic tangle. M is analytic in (a, E, L_z), so if it has a simple zero at one parameter point, the conclusion
holds on an open set, and `Lm` is non-constant outside a proper analytic subset.

For non-integrability alone, transversality is not needed. Kozlov 1983, Ch. V §2, Theorem 3 (p. 48): if the
Poincaré–Melnikov integral is not identically zero and a doubly asymptotic solution persists, there is no additional
analytic integral for small eps != 0; the separatrices only have to intersect and not coincide (also Cushman 1978 for
finite contact; LITERATURE.md B.5). M has zero mean, so `M not identically 0` already forces a sign change and an
intersection. So the computation can be reduced to: one Fourier coefficient of `Lm` is nonzero.

Literature status (LITERATURE.md A.6, A.7, B.6): no Melnikov theorem exists for MN or for Kerr plus a multipole.
Polcar–Semerák 2019 apply this reduction to Schwarzschild plus a ring or disc with numerically evaluated integrals
and state no theorem. The exact hypotheses of Holmes–Marsden 1982 were not read in full text and must be checked. No
closed form for inclined Kerr homoclinic orbits was found; none is needed, since the separated radial equation with a
double root integrates in elementary functions.

Facts that hold without computation: M has zero mean; by the reflection symmetry y -> -y of MN only even harmonics of
psi_0 appear (the same parity rule as V19). In the static limit a = 0 everything is elementary: with u = M/r and
chi the in-plane angle, the homoclinic orbit is `u = u_u - A sech^2(kappa chi)`, `A = (6 u_u - 1)/2`, `kappa^2 = A/2`,
`4M < r_u < 6M`; `y = sin(iota) sin(chi + psi_0)`; and for a static Weyl metric `psi = psi_0 + beta psi_1`,
`gamma = gamma_0 + beta gamma_1`,

    K_1 = 2 k^2 (x+1)^2 [ (gamma_1 - psi_1) mu^2 - (gamma_1 - 2 psi_1) E^2 (x+1)/(x-1) ] + 2 gamma_1 L_z^2 / (1-y^2).

Limits: beta_0 is not explicit, so this does not reach beta = 1/5 or -1/3; and it needs C8. It is the only route here
that addresses real-analytic integrals and proves chaos for a whole range of beta.

### 9.3 What Poincaré–Kozlov gives (route 2, stated correctly)

**Theorem 3 (conditional).** Suppose (N) the Kerr frequency map of the reduced system is non-degenerate on an open set
of tori, and (R) there are infinitely many resonances, accumulating inside that set, on each of which some resonant
Fourier coefficient of the first-order perturbation is not identically zero. Then the reduced MN Hamiltonian has no
first integral of the form `F_0 + beta F_1 + ...` (a formal series in beta with analytic coefficients on that set)
that is independent of H.

This excludes analytic FAMILIES of integrals. It does not exclude an analytic integral at a fixed beta != 0: for a
fixed beta only finitely many of the destroyed resonant tori produce non-degenerate periodic orbits that are visible,
and an analytic function can be dependent on H along finitely many closed curves. Kozlov 1983, Ch. IV §1, Theorem 1
(p. 33) concludes only that there is no integral "that can be expressed as a formal power series" in eps, and on
p. 40 he writes that "from this theorem one cannot deduce the non-integrability of perturbed systems for fixed values
of" eps != 0 (LITERATURE.md B.4, read in the English translation).

Status of the hypotheses: (R) is supported numerically by V19 on three tori (40-digit quadrature, not certified; one
torus sub-threshold); "infinitely many" is open. It would follow from 9.2: along the resonances
`Upsilon_r : Upsilon_theta = 1 : n`, n -> infinity (tori approaching the separatrix), the coefficient `F_(2n,-2)` times
the radial Mino period tends to the second Fourier coefficient of `Lm`. So one nonzero Fourier coefficient of the
Melnikov potential gives (R). (N) is checked numerically in V19 only by a scan that was not saved. The literature
check found no proof that the Kerr frequency map is non-degenerate on an open set (Xue 2021 proves a twist condition
for Schwarzschild and relies on plots for Kerr), so (N) needs one certified Hessian determinant.

The V19 digest also flags two unverified steps in V19's own argument: that `k . dF_0/dJ` is nonzero at the specific
tori, and the evenness assumption behind its cosine-only Fourier formula.

### 9.4 Boxes (route 4)

Parameter-uniform certified monodromy over boxes gives every point of a compact box. It cannot reach beta -> 0
(the certificate degenerates to Kerr) or unbounded E. With Theorem B it would upgrade "generic" to "all" on the boxes
covered. It is the heavy fallback if Theorem 1 fails.

## 10. Open points, and what I did not verify

1. I ran nothing. Every formula in section 6 is hand-derived; C1–C3 are the checks I would want before anyone relies on
   it. The constant 234.769 is hand arithmetic.
2. The class of integrals. Theorem 1 excludes integrals meromorphic near the complexified axis geodesic at complex
   positions near x = 0. Whether that class is the one the paper wants is a judgement for the Bridge and ansatz. The
   existing certificates use complex loops too, but near the real turning point and complex poles, not near x = 0.
3. Morales–Ramis is used for the full 4-degree-of-freedom Hamiltonian with integrals in involution. A statement about
   each reduced system at fixed L_z != 0 does not follow from the axis orbit (which has L_z = 0).
4. E = 0 and mu = 0 are excluded. For mu = 0 the axis gives nothing.
5. Corollary 1a (general multipoles) uses the general-n forms of a, b and gamma' from Bambi–Barausse 2011 (a reprint;
   the original was not opened and the reported typo corrections are not individually verified). With those forms,
   a(x,1) = -alpha W, b(x,1) = alpha/W and gamma'(x,1) = 0 for every n (hand).
6. I did not read the certificates' code. Section 5 relies on the digests.
