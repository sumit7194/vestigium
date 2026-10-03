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

**Resource note (2026-10-04, during row 0's v1 replay).** The bridge's overnight budget is **≤ 5 CPU threads** in
total for this session, shared with ansatz's memory-heavy run. So the v2 search's native thread count drops from
6 to **3**, from row 1 on; row 0 had already finished its search.
- This is **resource only.** Within each batch the loops are tested in the same nearest-first order, and the
  first certified pair does not depend on the batch size.
- The guard keys on `memory_pressure` < 10 % free and disk < 5 GB, as fixed (bed3891, 955b4c0).

**Robustness and resource note (2026-10-04 ~02:50, during row 0's v1 replay, about 3 h in).** Applies from row 1 on;
row 0 keeps its original code.
1. The **v2 certificate is saved to disk before the v1 replay starts** (`mr_v2_mneq_row{i}_v2cert.json`). Before
   this, a guard kill during a long replay would have lost the certificate data, because the row file is only
   written at the end.
2. The **v1 replay's 2–4 certifying loops run in parallel forked processes** (≤ 3, within the bridge's thread
   budget). It is the identical computation; results come back by **exact, outward-rounded** ball serialisation
   (mantissa/exponent; the rebuilt ball contains the original).
   - Tested on ZV equatorial: `replayed = True` on the same 3 loops as the earlier single-process run, in 5 s
     instead of 13 s. The batch size changed (2 vs 6) and the certifying pair did not, as stated.

Neither change touches the certificate rule, the search order or the integrator.

---

## Row 0 RESULT (2026-10-04): MN p1, (E, L, μ²) = (1, 0, 4): **OBSTRUCTION** (v2 certificate, v1 replay)

`qsim/mr_v2_mneq_row0.{json,log}`.

**The v2 search** found the certificate in 493 s (3 generators, 15 pairs, 2370 certified steps). Base point
z₀ = 2.02462 + 2.10024i in the t-plane.
- g = γ(t = 0.185747, ρ = 0.10037) · γ(t = −0.560195, ρ = 0.01331)
- h = γ(t = −0.148818, ρ = 0.10037) · γ(t = −0.560195, ρ = 0.01331)

All three centres are **real** singular points of the t-equation. In x = (t + 1/t)/2 they sit at about 2.785, −3.435
and −1.173. No loop encircles the essential singularities t = ±1.

**The GL(2) certificate (v2, explicit mid ± rad):**

| quantity | value |
|---|---|
| tr(g)²/det g | −313428.513645928235049718 − 106383.324905049348261505i (± 3.4e−20) |
| tr(h)²/det h | 26436.875183026811107649 (± 5.7e−19), real and > 4 |
| tr[g, h] | −290240.66028442123932780 − 86714.147183097016909894i (± 6.1e−12) |

So tr²/det ∉ [0, 4] for both, and tr[g, h] ≠ 2.

**The v1 replay** (reduced form, SL(2), 10,986 s) gives `replayed = True`:
- tr g = 93.70749334087501245 − 567.63510105890947259i (± 2.8e−15). Its square, −313428.5 − 106383.3i,
  **equals v2's tr²/det**, as it must.
- tr h = −162.59420402654828676 (± 2.1e−12), real with |tr| > 2.
- tr[g, h] = −290240.66028442123932780 − 86714.14718309701690989i (± 8.7e3). Its **midpoint agrees with v2's to
  about 25 digits**; v1's ball is wider but certainly excludes 2.

**Verdict (registered wording).** For MN at p1 (M = 5, a = 3, β = 1/5), with (E, L, μ²) = (1, 0, 4), the reduced
flow admits no additional first integral meromorphic in a neighbourhood of the **equatorial** phase curve, so it is
not meromorphically Liouville-integrable at that level.
- Logic: the machine-checked `L6_gl2`, plus the cited Ziglin / Morales–Ramis theorem and the finite-index fact.
- The positive control is on the **same solution type** (ZV equatorial, VCTRL).
