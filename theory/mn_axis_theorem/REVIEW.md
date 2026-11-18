# Independent review of DESIGN.md (MN axis theorem)

- Reviewer: a fresh Claude Opus 5.5 subagent with no Fable context, 2026-11-18. It was given DESIGN.md, LITERATURE.md
  and the Bridge's V21 PREREGISTRATION/FINDINGS, and asked to attack Lemma 1, Lemma 6, Lemma 4(a)–(e), Lemma 5,
  H9–H11 and the class of integrals. It ran short sympy/mpmath checks: Lemma 1's cancellation with generic f0, c0;
  Lemma 2; sigma_zz/sigma_z^2; the 2x2 algebra of 6.5(e) under both conjugation conventions; the numbers in sections
  5 and 8; and the zeros and poles inside the p1 (1,9) certified loop.
- Recorded by Claude Opus 5.5 (Quantum-personal). The review is summarised faithfully below; nothing was softened.

**Overall verdict: Theorem 1 STANDS WITH CORRECTIONS.** No fatal error. The core holds: Lemma 1, the lattice model
at x = 0, the density argument, and the static 2x2 pair. The corrections concern the definition of the integral
curve, the wording of the class of integrals (above all the section 1 headline), and local slips.

## Verdicts by part

| Part | Verdict | Main point |
|---|---|---|
| A. Lemma 1 (axis VE) | SOUND | The three axis relations, the Routhian, the gauge and both cancellations re-derived; sympy gives an exact 0. The direct summand is correct by the SO(2) weight splitting: frame dragging enters H as g^{t xi} p_t p_xi with g^{t xi} proportional to eta, so its coupling to the weight-0 block is cubic. For MN the lemma needs the section 2 metric to be vacuum; the fleet checks that pointwise (a check, not a gap) |
| B. Lemma 6 (convergence) | SOUND | (i)–(v) all hold. Wording: "on any disc avoiding sigma = 0" should be "on a simply connected domain avoiding 0 (here a half-plane)". x = +-1 maps to sigma = +-2 beta, bounded, and P is regular there |
| C(a) irreducibility | SOUND | It is the standard Fuchsian argument. The exponents at infinity (static +- i sqrt3/4; rotating (0,0) with a log) and the Fuchs relation check. Correction: the double zero is at eps = 2m\|ah\| (+-2m ah for complex eps), not "eps = 2 m ah" |
| C(b) | SOUND | |
| C(c) normal subgroup | SOUND WITH A WORDING FIX | The s-plane is NOT the universal cover of the punctured W-plane. It is the Z-covering belonging to N = ker(winding about W = 0). The rest holds |
| C(d) f.g. dense subgroup | SOUND WITH A FIX | In the torus-normaliser case, nested invariant unordered pairs live in Sym^2 P^1 = P^2; a degenerate limit pair is an invariant line, still a contradiction |
| C(e) static pair | SOUND | Confirmed symbolically under both conventions; tr[h1,h2] = 2 - 4c^6 = -5.0447e7; only c^2 matters (orientation immaterial). It yields "G^0 not abelian", which is enough for Morales–Ramis but not for (i)'s "not solvable" |
| D. Lemma 5 | SOUND WITH A FIX | Same Sym^2 P^1 fix. Burnside is unnecessary: {g^{120!} = 1} is a proper Zariski-closed set |
| E(i) v -> chi -> Gamma | SOUND | |
| E(ii) to the full VE | SOUND | zeta_+^{(a)} zeta_-^{(b)} = f0 chi_a chi_b spans Sym^2; Gal surjects onto PSL2 |
| E(iii) Morales–Ramis applicability | SOUND WITH TWO FIXES | (1) Gamma = {(z, zdot)} is NOT an integral curve of the 4-dof H: dt = E dz/(f0 sqrt P) has periods. Use the covering Gamma~ (its monodromy is normal in the dense group with abelian quotient, hence still dense), or reduce at p_t = -E first. (2) Remove equilibria (multiple zeros of P) from Gamma. H11 is correct |
| E(iv) Theorem 1(iii) | SOUND, DERIVATION MISSING | With L = 0, the solutions are exactly the real-chi ones; the gauge sqrt(g^{theta theta}) is algebraic over M(Gamma) (Morales–Ramis Thm 5); H_{E,L=0} is analytic at theta = 0. The statement must say "independent of H_{E,L=0}" |
| F. Class of integrals | BODY CORRECT, HEADLINE OVERSTATED | See the corrected statement below |
| G. Corollary 1a | SOUND WITH A FIX | a(x,1), b(x,1), gamma'(x,1) and omega(x,1) verified for every n; spell out the inverse branch of sigma = 2 sum alpha_n x^{-n-1} (Rouché); it relies on the unverified general-n transcription |
| G. Retrodictions | ZV right; Kerr right but under-justified | Kerr: exponents alone do not fix a four-point group. Here all differences are 1/2, so on the elliptic double cover the local monodromies are +-1 and the group is virtually abelian. Both assume E != mu |
| G. Section 5 H3/H5 numbers | CORRECT | |
| G. Section 5 "observation" | WRONG | The p1 (1,9) loop h encloses 2 zeros AND 2 poles of P (one period of the rotating lattice), not "the first two turning points". The static constant does not apply. Independently confirmed by the certified C0 (qsim/mn_lattice/pre_A1/C0.json) |
| G. Theorem B (9.1) | WRONG AS WRITTEN | The zero set of tr M_i is not proper when M_i is a single-turning-point loop, whose trace is identically 0. The exceptional set must be {tr[M1,M2] = 2} union {at least two of tr M1, tr M2, tr M1M2 vanish} union {finitely many primitive-finite trace triples} |

## Corrected statement of Theorem 1 (the reviewer's wording, adopted)

> For every eps > 0: there are no four first integrals that are meromorphic on a complex neighbourhood of (a connected
> component of) the part of the complexified axis integral curve Gamma~ lying over 0 < |x| < eps, that are pairwise
> in involution, and that are independent on an open dense subset of it. Here x != +-1, and the poles of f and the
> equilibria are removed. In particular, none completes H, p_t, p_phi. The same holds for the reduced flow
> H_{E,L=0} with one integral independent of it.
>
> This says nothing about integrals that are real-analytic on the exterior but do not continue single-valuedly and
> meromorphically to that complex region.

Comparison with the existing certificates.
- For the class "meromorphic near all of Gamma", Theorem 1(iii) contains the four axial certificates (2ce8b41).
- In localised form the two are incomparable. The certificates use loops at |x| >= 0.35 and exclude integrals
  meromorphic only there, which Theorem 1 does not.
- So route 4 is "superseded" only for the near-all-of-Gamma class.

Comparison with Maciejewski–Przybylska–Stachowiak 2013 (ZV). Their NVE is Fuchsian and rational, which upgrades their
result to "meromorphic on the whole phase space, any growth". Here the VE has an essential singularity at x = 0, so no
such upgrade exists, and Theorem 1 sits strictly in the Theorem 7 class.

## Overruled points of the design (Fable 5.2), with reasons

| # | Fable wrote | Overruled because |
|---|---|---|
| O1 | Section 1 headline: "no complete set of meromorphic first integrals in involution" (no qualifier) | The theorem covers only integrals meromorphic near the complexified orbit near x = 0; the qualifier is mandatory (F) |
| O2 | Theorem 1: Gamma = {(z, zdot) : zdot^2 = P} | Not an integral curve of the 4-dof H (periods of dt); must be Gamma~ or the p_t-reduced system, with equilibria removed (E(iii)) |
| O3 | "Functionally independent on that neighbourhood" | Must be "on an open dense subset (not necessarily on Gamma)" |
| O4 | 6.5(c): the s-plane is the universal cover of the punctured W-plane | It is the Z-covering belonging to ker(winding about W = 0) |
| O5 | Double zero at eps = 2 m ah | eps = 2m\|ah\| (+-2m ah for complex eps) |
| O6 | Section 5 observation: the p1 (1,9) loop encloses the first two turning points | It encloses 2 zeros and 2 poles (reviewer, and certified C0) |
| O7 | Section 8: Kerr is dihedral because all exponent differences are 1/2 | True, but it needs the double-cover argument; exponents alone do not fix the group |
| O8 | Section 3: route 4 is superseded | Only for the near-all-of-Gamma class; localised, the pointwise certificates exclude integrals Theorem 1 does not |
| O9 | 9.1 Theorem B: "each is a proper analytic subset because it misses p0" | False for trace-zero generators; the exceptional set must be redefined as above |

Points where the design was right, against an obvious objection:
- the E^2 cancellation in Lemma 1 (exact);
- the regular-axis hypotheses;
- that x = +-1 and the cube-root branch introduce no extra singular points near the lattice;
- the static constant -(4 + 2cosh(pi sqrt 3)) and the sign conventions.
