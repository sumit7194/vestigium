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

## Row 1 RESULT: MN p1, (1, 0, 9): **INCONCLUSIVE** (transport failure; not a verdict)

The v2 search aborted after 319 s: "transport failed on γ(t = 0.611725, ρ = 0.11648): step size underflow near
t = 0.70765 − 0.06576i". That point lies at distance 0.1163 from the loop's centre, i.e. **on the loop's circle**:
a singular point the float locator **missed**, so its loop radius was not limited by it.

The located list (6 points) is visibly **incomplete**:
- the coefficients are real, so singular points come in conjugate pairs, but −0.98142 + 0.21985i and
  −0.74271 + 0.06204i appear without their conjugates;
- x(t) = x(1/t), so the singular set is invariant under t ↦ 1/t, but 0.611725 appears without 1/0.611725
  ≈ 1.6347.

The grid-local-minimum locator (spacing 0.1 on [−6, 6]²) is too coarse for this equation.

**Under the frozen policy, this is INCONCLUSIVE for the row.** No certificate is lost or invented. The fix is a
search-policy change, so it is **proposed to the bridge** and not applied:
- a complete singular-point locator (conjugate and t ↦ 1/t closure, finer grid, Newton verification);
- skip, rather than abort on, a loop whose transport cannot be certified.

Rows 2–5 continue under the frozen policy.

## AMENDMENT A6 (2026-10-04), POST-FAILURE, bridge-approved: search policy only. Filed before the code.

Triggered by row 1's transport failure: an unlocated singular point lay on a loop.

**(a) A complete singular-point locator.**
- Grid 4× finer (spacing about 0.025 on [−6, 6]²); local minima of |den| for the denominators of p and q; Newton
  refinement.
- Then **closure under complex conjugation**, valid because the coefficients are real-rational in t and exp of
  real-rationals. Each conjugate is Newton-verified.
- The **t ↦ 1/t images are tried only as Newton-verified candidates.** Per the bridge's correction this is **not** a
  symmetry: R(1/t) = −R(t) on the single rational branch, and the MN coefficients contain odd powers of R. Many
  images are expected to be rejected, and an absent image is **not** evidence of a miss.
- Dedupe at 1e−8.

**(b) Skip, don't abort.** If a loop's transport cannot be certified, that loop is recorded and **skipped**, and
the search continues. Skipping only removes candidates, so it cannot create a false certificate.

**(c) Re-runs, labelled post-failure:** row 1, and any later row whose search fails the same way. They run after
rows 2–5 finish, within the CPU budget.

**Frozen defaults are unchanged** for the rows still running under the original policy: the new locator and the
skip behaviour are opt-in.

Row 0 is unaffected: each certified loop is a legitimate element of π₁, whatever it encloses.

**CORRECTION to the row-1 diagnosis (2026-10-04, before any A6 run).** The failure point t = 0.70765 − 0.06576i is
**not** an unlocated pole:
- the denominators of p and q are clearly nonzero there (|Q_p| ≈ 0.51, |Q_q| ≈ 0.26), and Newton from that point
  finds no root nearby;
- the A6 locator (25 points against the old 6, conjugate pairs complete) finds nothing within 0.116 of it.

The real cause is **growth near the essential singularity t = 1**, 0.30 away: the exponent g₃ = −3β²/(4R⁶) reaches
|g₃| ≈ 13.7 there, so the coefficients vary by factors around e¹³, and the certified step's ρM̄ ≤ 4 forces h below the
1e−7 floor. The loop's straight path passed through that region.

- **A6 (b), skip-not-abort, is what fixes this.** A6 (a) is still a real completeness improvement (the old list
  was incomplete), but it was not the cause here.
- Row 2's failure, near t = −0.73436 + 0.14529i, about 0.30 from t = −1, is presumably the same mechanism near
  the other essential singularity.
- Row 0's result is unaffected.

**Row 0, independent numerical reproduction (bridge V9-eq′, reported, not re-run here).**
- Method: the bridge's own equatorial NVE and a DOP853 integrator, from my loop recipe only.
- Relative agreement: tr²/det(g) 7.0e−11, tr²/det(h) 5.9e−11, tr[g, h] 4.3e−11. tr²/det(h) comes out real to
  about 1e−6, the commutator is the same in both composition orders, and the Abel det and tolerance checks pass.
- The bridge's first run disagreed because of its own √(R₀²) branch bug. It is disclosed and kept on record on
  its side.

**Row 0 grade:** OBSTRUCTION (v2 certificate + v1 replay), **independently reproduced (numerical, bridge V9-eq′).**

## Row 3 RESULT (2026-10-04): MN p2, (E, L, μ²) = (1, 0, 4): **OBSTRUCTION** (v2 certificate, v1 replay)

**The v2 search** found the certificate in 251 s (13 located points, 3 generators, 9 pairs, 2689 steps, no loop
skipped). Base point z₀ = 2.667119562555136 + 2.7667479123938024i.
- g = γ(0.307967384242499, ρ 0.20760978472725028) · γ(−0.4751366065599529 + 0.22858319755496656i, ρ 0.07700413164438846)
- h = γ(0.307967384242499, ρ 0.20760978472725028) · γ(−0.7703523566330759 + 0.37656494220755987i, ρ 0.017435697281317466)

**The GL(2) certificate (v2, mid ± rad):**

| quantity | value |
|---|---|
| tr²/det(g) | 1345.2758406025942679 − 1011.6353858956783367i (± 9.8e−16) |
| tr²/det(h) | −2371.4390654371280839 − 7787.8783024198235091i (± 1.6e−16) |
| tr[g, h] | −389140.59069213841206 + 1464024.0755057192621i (± 8.9e−11) |

**The v1 replay** (parallel; 8686 s for the whole row) gives `replayed = True`:
- tr g = 38.913231095430261 − 12.998604297530035i. Its square equals v2's tr²/det(g).
- tr h = −53.709835242169482 + 72.499554944689964i.
- tr[g, h] = −389140.59069213841206 + 1464024.0755057192621i (± 0.05). It agrees with v2 to about 19 digits.

**Verdict (registered wording):** for MN at p2 (M = 13, a = 5, β = −1/3), with (E, L, μ²) = (1, 0, 4), the reduced
flow admits no additional first integral meromorphic in a neighbourhood of the equatorial Γ, so it is not
meromorphically Liouville-integrable at that level.

**Row 3, independent numerical reproduction (bridge V9-eq′, first run, reported, not re-run here).** Relative
agreement: tr²/det(g) 2.2e−12, tr²/det(h) 4.6e−13, tr[g, h] 2.2e−12. The commutator is the same in both composition
orders, and the Abel and convergence gates pass at 1e−11.

**Row 3 grade:** OBSTRUCTION (v2 certificate + v1 replay), **independently reproduced (numerical, bridge V9-eq′).**

Both parameter points (p1 row 0, p2 row 3) are now obstructed on the equatorial solution, each by two rigorous
implementations plus an independent numerical reproduction.

## Row 4 RESULT: MN p2, (1, 0, 9): **INCONCLUSIVE** under the frozen policy (transport failure)

The search aborted at 278 s on γ(−0.801214 + 0.112890i): step-size underflow near t = −0.73491 + 0.16353i, about
0.31 from the essential point t = −1. This is the same mechanism as rows 1 and 2. The row is queued for the A6
re-run (skip-not-abort).

## Row 5 RESULT: MN p2, (1, 1, 4): **INCONCLUSIVE** under the frozen policy (transport failure)

The search aborted at 1447 s on γ(−0.763109 + 0.100024i), near t = −0.73838 + 0.15504i, close to t = −1. Same
mechanism as rows 1, 2 and 4.

**Frozen-policy summary:**

| rows | outcome |
|---|---|
| 0 (p1, (1, 0, 4)) | **OBSTRUCTION** |
| 3 (p2, (1, 0, 4)) | **OBSTRUCTION** |
| 1, 2, 4, 5 | INCONCLUSIVE (transport failure near t = ±1) |

The A6 re-runs of rows 1, 2, 4 and 5 (post-failure) start now, via the overnight chain.
