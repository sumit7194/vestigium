# Zenodo preprint record: DRAFT metadata (for the coordinator's read; not uploaded)

**Resource type:** Publication / Preprint
**Title:** Chaotic geodesics in the Manko–Novikov spacetime: a computer-assisted proof and a Melnikov theorem (AI-assisted)
**Creator:** Pal, Sumit (Independent researcher; ORCID 0009-0000-9541-2793)
**Version:** v1 (2026-11-28)
**License:** CC BY 4.0 (to confirm with Sumit). The software record is MIT.
**Files:** mn_chaos.pdf (preview), SUMMARY.pdf, REFEREE_GUIDE.md, README.md, SHA256SUMS.txt

## Description (abstract with sections)

**Result.**
- We prove that timelike geodesics of the Manko–Novikov spacetime, the Kerr black hole deformed by an anomalous mass
  quadrupole β, are chaotic on an energy level near an unstable spherical orbit.
- For mass M = 5, spin a = 3 and β = 3/100, the stable and unstable manifolds of a hyperbolic periodic orbit intersect
  transversally. So the return map has a Smale horseshoe, and the geodesic flow on that level has positive topological
  entropy.
- By a Melnikov-type argument resting on an interval-certified Fourier coefficient, the same conclusion holds for every
  0 < |β| < β₀ of either sign, with β₀ > 0 not computed.

**Method.**
- The first result is a computer-assisted proof in interval arithmetic (CAPD, 128-bit MPFR).
- It uses a Newton–Krawczyk argument for a reversibility-symmetric boundary-value problem, and a cone lemma for the local
  unstable manifold. The criterion "the unstable tangent at the symmetric point is neither horizontal nor vertical" is
  certified: the tangent's horizontal component is about 3×10⁻⁵ of its length, roughly 500 times the enclosure error.

**Verification.**
- The same code applied to Kerr (β = 0) correctly finds no transversality.
- A field with one β² term removed gives a different certificate.
- The validator reproduces a published computer-assisted homoclinic proof in the restricted three-body problem.
- Every decision was re-evaluated from exact dumps in a second arithmetic library (Arb).
- The field was re-derived from the published metric by a separate implementation, and agrees to about 4×10⁻⁴⁶
  relative (at the 160-bit working precision).
- The decision rules and expected outcomes were fixed before each computation.

**Limits.**
- No entropy value is claimed. One level, one spin and one orbit family are treated, and β₀ is not explicit.
- The flow enclosures rest on one validated integrator.

**AI assistance.**
- This work was carried out with substantial assistance from AI systems, Claude (Anthropic) and Gemini (Google).
- All checks described as independent were done by separate AI sessions or systems, not by human peer review. No
  external expert has yet read the proofs.

**Code and certificates:** vestigium v2026.11.28, doi:10.5281/zenodo.24602464.

## Keywords
computer-assisted proof; interval arithmetic; Manko–Novikov spacetime; bumpy black hole; geodesic chaos; transversal
homoclinic orbit; Smale horseshoe; topological entropy; Melnikov method; AI-assisted

## Related identifiers
| Relation | Identifier | Resource |
|---|---|---|
| isSupplementedBy | 10.5281/zenodo.24602464 | Software (vestigium v2026.11.28) |
| cites | 10.1103/PhysRevD.77.024035 | Gair, Li & Mandel 2008 (MN metric form) |
| cites | 10.1103/PhysRev.174.1559 | Carter 1968 (the Carter constant) |
| cites | 10.1088/0264-9381/9/11/013 | Manko & Novikov 1992 (the MN metric) |
| cites | 10.1090/conm/198/02519 | Robinson 1996 (Melnikov method for autonomous Hamiltonians) |
| cites | arXiv:2205.03922 | Capiński, Kepley & Mireles James, "Computer assisted proofs for transverse collision and near collision orbits in the restricted three body problem" (the validator control) |
| cites | arXiv:2010.07097 | Kapela, Mrozek, Wilczak & Zgliczyński (CAPD::DynSys) |
| cites | 10.1007/BF02096667 | Moeckel 1992 |
| cites | 10.1088/0264-9381/9/12/004 | Bombelli & Calzetta 1992 |
| cites | 10.1088/0951-7715/9/1/001 | Delshams & Ramírez-Ros 1996 |
