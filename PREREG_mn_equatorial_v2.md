# Pre-registration — MN on the EQUATORIAL solution with iahub v2 (target registration)

**Committed before any v2 computation on this target.** It follows `PREREG_iahub_v2.md` (registered 33321aa),
whose validation ladder **passed in full**:
- VG0;
- VCTRL (12/12);
- VREPRO (4/4, axial MN re-proved and replayed by v1);
- V-provenance (equatorial and axial, 4.3e−50 against the bridge's independent derivation);
- V-Lean (`lake build`, no `sorry`, standard axioms only).

**Relation to the v1 stage.** `PREREG_mn_equatorial_certified_monodromy.md` (v1) found no certificate: p1 rows
INCONCLUSIVE on time, p2 rows 11–13 cut short or still running. Its outcome stands on its own. This registration
is a **new, independent route** with a different integrator and a different equation form. It is **not** an
amendment of v1.

## What runs

**Target rows.** The same as v1: MN at p1 (M = 5, a = 3, β = 1/5) and at p2 (M = 13, a = 5, β = −1/3), on
the equatorial solution y = 0, p_y = 0, at (E, L, μ²) = (1, 0, 4), (1, 0, 9) and **(1, 1, 4)**. That is 6 rows.

**Equation.** The non-reduced ξ₁ system `Y′ = [[0, 1], [−q, −p]] Y` in t (x = (t + 1/t)/2). Its coefficients lie
in ℚ(t, E₁, E₂, E₃) and are built by the same exact pipeline that rung 5b verified against the bridge's independent
derivation. The essential singularities t = ±1 are declared `bad`.

**Search.** The frozen v2 driver `qsim/mr_v2.py`:
- nearest-first generators;
- incremental testing of generators and pairwise products;
- stop at the first certified pair;
- N = 140, 192 bits.

**Certificate.** The scale-free GL(2) form, decided by `ia_native.certificate_gl2` on the Arb enclosures:
- tr(G)²/det(G) ∉ [0, 4], and the same for H;
- tr[G, H] ≠ 2.

**The logic from certificate to verdict is machine-checked:** `L6_gl2` in `lean/ZiglinCert` gives "no finite-index
subgroup of ⟨G^k, H^k⟩ is abelian, for all k ≥ 1". The covering lift is k = 2, and the case k = 1 means G⁰ is not
abelian, because G⁰ has finite index (cited).

**Two-implementation rule.** A v2 certificate counts only after the frozen **v1** hub (`ia_hub`, reduced ξ₁ form,
SL(2) certificate) **replays** the certifying loops and its own enclosures satisfy the certificate.
- The v1 replay is slow on MN equatorial (minutes to tens of minutes per loop), but it only needs the 2–4
  certifying loops.
- If the v1 replay fails or times out, the row is graded **"v2 certificate, v1 replay failed"**. That is not
  OBSTRUCTION.

**Resources.** One guarded child per row: 2 GB, **6 h** (search plus replay), `memory_pressure` and disk guards,
6 native threads, detached under nohup. Results are committed and pushed per row.

## Verdict wording (fixed now)

**OBSTRUCTION at a row:** for MN at P, with (E, L, μ²) as stated, the reduced flow H_{E,L} admits no additional
first integral meromorphic in a neighbourhood of the **equatorial** phase curve Γ. So it is not meromorphically
Liouville-integrable at that level.

The record of each such row carries:
- the certifying loops (centres, radii, base point);
- the GL(2) certificate quantities (explicit mid ± rad);
- the v1 replay's SL(2) quantities.

**Otherwise INCONCLUSIVE, never "integrable".**

## Setup correspondence

**The claim to be supported.** That MN (q-anomaly subclass) has no Carter-like integral, now with the
**equatorial** solution, which has the same solution type as the positive control (ZV equatorial), and **including
L ≠ 0**.

**What is actually tested.** No meromorphic integral near the equatorial Γ, at the 6 stated points.

The two match only up to these gaps:
- meromorphic integrals only;
- the tested levels only (one L ≠ 0 level);
- the supplied metric (a verified transcription; vacuum exact but pointwise);
- AI-written code, though the numbers come from two implementations, the logic is machine-checked, and the
  equation is independently derived.

The Ziglin / Morales–Ramis theorem is cited.
