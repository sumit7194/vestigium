# MN axis theorem: corrected statement (revision 1)

Claude Opus 5.5 (Quantum-personal), 2026-11-18. This folds the independent review (REVIEW.md, 6811d2d) into the
statement of Fable 5.2's Theorem 1 (DESIGN.md, kept verbatim). The proof is DESIGN.md section 6, with the fixes listed
under "Proof changes". Status: a corrected claim, reviewed once, NOT yet registered as a result. Numerical and
certified evidence is listed at the end.

## Setting

- MN metric with k > 0, |alpha| < 1, anomalous quadrupole alpha_2 = beta != 0 (all other alpha_n = 0; the static
  alpha = 0 member included).
- Geodesic Hamiltonian H = (1/2) g^{mu nu} p_mu p_nu, with E = -p_t != 0, mu^2 = -2H != 0, and the axis orbit at L = 0.
- P(x) = E^2 - mu^2 f(x, 1), where f(x, 1) = W (r^2 - 2Mr + a^2)/(r^2 + a^2 W^2), W = exp(2 beta/x^3), r = kx + M.
- The integral curve: Gamma~, the complexified axis integral curve in phase space. It is the covering of the
  Riemann surface {(z, zdot) : zdot^2 = P} fixed by the periods of dt = E dz/(f sqrt P). Equivalently, one may
  work with the system reduced at p_t = -E.
- Removed: points over x = 0 and x = +-1, poles of f, and equilibria (multiple zeros of P).

## Theorem 1 (revision 1)

For every eps > 0, consider the part Gamma~_eps of (a connected component of) Gamma~ lying over 0 < |x| < eps.

(i) The identity component of the differential Galois group of the variational equation along Gamma~_eps, over the
meromorphic functions on Gamma~_eps, maps onto PSL(2, C). In particular it is not solvable.

(ii) Consequently, there are no four first integrals of H that are meromorphic on a complex neighbourhood of Gamma~_eps,
pairwise in involution, and functionally independent on an open dense subset of that neighbourhood (not necessarily
on Gamma~_eps itself). In particular none completes H, p_t, p_phi.

(iii) The same holds for the reduced two-degree-of-freedom flow H_{E,L=0} in (x, theta): it has no first integral that
is meromorphic on a complex neighbourhood of its axial phase curve over 0 < |x| < eps and independent of H_{E,L=0}.

**Explicitly NOT covered:** integrals that are real-analytic (even globally) on the physical exterior but do not
continue single-valuedly and meromorphically to the complex region near x = 0 (r = M, inside the horizon). Null
geodesics (mu = 0) and E = 0 are not covered.

**Relation to the pointwise certificates** (2ce8b41, VREPRO, CAPD replay):
- For the class "meromorphic near the whole axial phase curve", (iii) contains the four axial certificates, for all
  parameters at once.
- In the localised form they are incomparable. The certificates use loops at |x| >= 0.35 and exclude integrals
  meromorphic only there.

**Corollary (general multipoles).** The same holds for any finite set of anomalous multipoles with some alpha_n != 0.
It is conditional on the general-n MN transcription (Bambi–Barausse 2011, a reprint; the original was not opened), and
on spelling out the large-|sigma| inverse branch of sigma = 2 sum alpha_n x^{-n-1} (Rouché).

## Proof changes relative to DESIGN.md section 6 (all from REVIEW.md)

1. Lemma 6: "a disc avoiding sigma = 0" becomes "a simply connected domain avoiding 0 (a half-plane)".
2. Lemma 4(a): the double zero of the rotating model is at eps = 2m|ah| (+-2m ah for complex eps).
3. Lemma 4(c): the s-plane is the Z-covering of the punctured W-plane belonging to ker(winding about W = 0), not
   the universal cover.
4. Lemma 4(d) and Lemma 5: invariant unordered pairs are taken in Sym^2 P^1 = P^2. A degenerate limit pair is an
   invariant line. Burnside is not needed: {g^{120!} = 1} is a proper Zariski-closed set.
5. Assembly: replace Gamma by Gamma~.
   - The monodromy group of Gamma~ is a normal subgroup of the dense group D_chi, with abelian quotient.
   - Its closure is normal in SL2.
   - It is not central, because otherwise D_chi would be solvable.
   - So it is still dense.
   Remove the equilibria.
6. (iii): with L = 0 the solutions are the real-chi solutions of (1). The NVE of H_{E,L=0} is (1) gauged by
   sqrt(g^{theta theta}) = sqrt(f)/(k sqrt(x^2 - 1)), which is algebraic over M(Gamma), so the identity component is
   unchanged (Morales–Ramis Theorem 5). H_{E,L=0} is analytic at theta = 0.
7. WITHDRAWN as written: Section 9.1 (Theorem B). The exceptional set must be
   {tr[M1, M2] = 2} union {at least two of tr M1, tr M2, tr M1M2 vanish} union {the finitely many primitive-finite
   trace triples}.
8. WITHDRAWN: the DESIGN.md section 5 remark that the p1 (1,9) certified loop h encloses "the first two turning
   points", with -234.77 as the comparison value. It encloses 2 zeros and 2 poles of P (certified C0; REVIEW.md O6),
   so the static constant does not apply.
9. Section 8 Kerr retrodiction: all exponent differences are 1/2, so on the elliptic double cover the local
   monodromies are +-1 and the group is virtually abelian. This assumes E != mu.

## Evidence (none of it replaces the proof)

| item | what | where |
|---|---|---|
| Lemmas 1–3 for MN | V21 C1, C2 (Bridge, floats, 6e-35) | TheBridge V21 (30231db) |
| Lemmas 1+2 for MN p1 and static | exact symbolic identity in the certified pipeline (Q1) | qsim/mn_lattice/Q1_*.json (c806979) |
| Lemma 1 general | re-derived; exact sympy cancellation with generic f0, c0 | REVIEW.md, A |
| Static model limit (Lemmas 4(e), 6) | V21 C3 (floats, 1e-8); certified T-limit at j = 10, 100, 1000 (S1, S2) | V21; qsim/mn_lattice/RESULT.md |
| Exponents 1/4, 3/4 at every lattice point | certified T-exact, 66 loops, static and rotating | qsim/mn_lattice/RESULT.md |
| Obstruction near x = 0 at four rows | certified T-L6 at j = 10, 100, 1000 (S1, S2, R1, R2); 12/12 Lean-checked (L6_gl2) | qsim/mn_lattice/RESULT.md |
| Static limit at large j | T-limit PASS at j = 100 and 1000 (deviation 1.97e-5 at j = 1000) | qsim/mn_lattice/RESULT.md |
