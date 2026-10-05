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

## Row 1, A6 re-run (post-failure): MN p1, (1, 0, 9): **INCONCLUSIVE (v2 certificate, v1 replay FAILED)**

- **v2:** the certificate was found at 773 s, after 3 loops near t = 1 were skipped (A6 (b)).
  - g = γ(1.261448 + 0.321527i) · γ(1.287403 + 0.239791i), h = γ(1.261448 + 0.321527i) · γ(−0.160033)
  - tr²/det(g) = −2547891.7087 + 4172532.2258i (± 5e−5)
  - tr²/det(h) = −6817.1486 + 7154.6411i
  - tr[g, h] = 51202181.921165786 + 30889220.299715389i (± 37)
- **v1 replay** (11,293 s) gave `replayed = False`, and it is **not a contradiction**:
  - v1's tr[g, h] midpoint, 51202181.921165836 + 30889220.299715405i, agrees with v2's to about **15 digits**;
  - v1's tr(g)², about −2.5479e6 + 4.1725e6i, matches v2's tr²/det(g);
  - but v1's commutator ball has radius **1.3e11**, larger than the value, so it cannot certify tr ≠ 2.
- **Cause:** a precision shortfall in v1. The certifying loops sit at t ≈ 1.26–1.29, about 0.3 from the essential
  point t = 1, where coefficient growth makes v1's tail bounds at N = 100 very loose, and the four-loop
  commutator product amplifies them.

By the registered rule the row is **INCONCLUSIVE**. A fix (a v1 replay at a higher order N, after re-running v1's
G0 at that N) needs the bridge's approval; it is proposed, not applied.

## AMENDMENT A7 (2026-10-04), POST-FAILURE, bridge-approved: v1 replay at Taylor order N = 140. Filed before the code.

Triggered by row 1's A6 replay at N = 100: `replayed = False`, the commutator radius was 1.3e11, the midpoints agreed
with v2 to about 15 digits, and it was **not a contradiction**.

1. **v1's G0 is re-run at N = 140 first.** The known traces must be enclosed with ≥ 10 digits, or A7 stops there.
2. **The row-1 v2 certificate is re-replayed by v1 at N = 140, unchanged:** the same loops and the same SL(2)
   certificate rule.
3. **A7 is ONE declared step.** If N = 140 still cannot certify, the row stays INCONCLUSIVE. Any further raise of N,
   or any change of method, is a new amendment through the bridge.
4. **From now on,** any v1 replay that hits the same tail-limited failure is repeated at N = 140, and the N = 100
   result is logged each time.

**Resources:** the re-replay uses 2 processes, alongside the running A6 rows, within the 5-thread budget.

**A7 step 1 — v1 G0 at N = 140: PASS.** All known traces are enclosed, at 34.5, 34.5 and 33.9 digits
(`qsim/mr_v2_a7_G0.{json,log}`). Step 2, the row-1 re-replay at N = 140 (2 procs, guarded), is running.

**Row 1, bridge numerical reproduction (V9, pre-registered): REPRODUCED, with a thin margin.**
- Relative agreement: tr²/det(g) 5.1e−8, tr²/det(h) 1.7e−12, tr[g,h] 5.1e−8.
- Abel gate: 1.1e−10. Tolerance convergence: 9.9e−8, against its 1e−7 gate.
- The loops near t ≈ 1.27 cost about 5 digits, consistent with the v1 tail limit.
- This corroborates the midpoints to about 7 digits. It is **not** a substitute for A7: the row's grade waits for the
  N = 140 v1 replay.

## Row 2, A6 re-run: MN p1, (E, L, μ²) = (1, 1, 4) — **OBSTRUCTION** (v2 certificate + v1 replay at N = 100)

- **Certificate.** v2 tried 9 pairs over 3 generators. Base point z₀ = 2.4691717810397047 + 2.5614059326191394i.
  - g = M_a·M_b, with a = γ(1.0407508871125104 + 0.4677121389555332i, ρ 0.03132088280290887) and
    b = γ(1.0080515742827576 + 0.36856210426090547i, ρ 0.03132088280290887).
  - h = M_a·M_c, with c = γ(0.19761156121947301, ρ 0.1154952476585107).
  - Skipped (step underflow): the conjugate loops g[1.008052 − 0.368562i] and g[1.040751 − 0.467712i].
- **v2 enclosures:**
  - tr²/det(g) = 48.16395921732219238937 − 56.11599596601088473492i (±8.2e−16);
  - tr²/det(h) = −12146.88614102791808418 − 6932.690639883441608725i (±8.6e−22);
  - tr[g,h] = 544.0346538066000467109 − 550.2748225118644843529i (±8.7e−12).
- **v1 replay (reduced form, SL(2) rule): `replayed = True`.**
  - tr g = −7.813933230303 + 3.590765003493i (±5e−9);
  - tr h = 30.324446564554152 − 114.308609476602497i (±1e−15);
  - tr[g,h] = 544.03465380660005 − 550.27482251186448i (±0.98), so certainly ≠ 2.
  - The midpoints agree with v2 to about 18 digits.
  - The replay was not tail-limited, so A7 term 4 does not apply.
- **Verdict (as registered): OBSTRUCTION** at MN p1, (1, 1, 4). Per Lean `L6_gl2` / `L6_not_virtually_abelian` and the cited
  Morales–Ramis / Ziglin theorem, the system has no meromorphic first integral independent of H near the equatorial
  solution, at this parameter row.
- **Bridge numerical reproduction (V9, pre-registered): REPRODUCED.**
  - Relative agreement: tr²/det(g) 2.5e−10, tr²/det(h) 1.5e−11, tr[g,h] 8.9e−9.
  - Abel gate 3.2e−10; convergence 1.1e−8; the commutator is the same in both composition orders.

## 2026-10-04 15:56 — unplanned machine reboot; resumed on the user's instruction

The Mac rebooted unexpectedly. No shutdown record, cause unknown. At that point:
- the A7 row-1 re-replay at N = 140 was still running (it had run for more than 3 h; nothing is saved mid-run);
- row 4's v1 replay was running. Its v2 certificate had been saved before the replay, as designed:
  `qsim/mr_v2_mneq_row4_a6_v2cert.json`.

Row 5 and the TS stage had not started. **No result was lost or altered**: unfinished computations simply have no
outcome yet.

**Resumed, with no change to any method:**
1. **A7 row-1 re-replay at N = 140.** The certificate, loops and rule are unchanged. The singular-point list is now
   rebuilt by the same deterministic `locate_a6` the row run used, and asserted equal to the stored list. The killed
   attempt used the stored 6-digit-rounded list; that list only steers step sizes, and rigour comes from the ball
   evaluation either way.
   - Guard 3 GB / **12 h**. A resource change only: the first attempt passed 3 h with a loop near t ≈ 1.27 still
     running.
2. **Row 4:** v1 replay of the saved certificate at N = 100. If that replay fails without an error (the
   tail-limited pattern), it is repeated at N = 140 under A7 term 4, and both results are logged.
3. **Row 5 A6**, then the **TS v2 stage**, both as registered.

Each step uses ≤ 3 threads alongside A7's 2 processes, so the total stays ≤ 5. Code: `qsim/mr_v2_a7.py`
(REPLAY / FINISH), `qsim/resume_chain.sh`. The A6 summary file now merges rows instead of being rewritten
(bookkeeping only).

**Row 4, bridge numerical reproduction (V9, pre-registered, β = −1/3): INCONCLUSIVE by the bridge's own gates.**
- Abel 7.7e−8 and convergence 4.2e−7 miss their 1e−8 and 1e−7 gates. Loops a and b, near t = 1, exhaust complex128.
- Recorded but not graded: the bridge's values agree with the v2 midpoints to 1.5e−6 (g and comm) and 1.1e−11 (h),
  and lie well inside the v2 balls, so nothing points the other way.
- Row 4's grade rests on the v1 replay (N = 100, then N = 140 under A7 term 4 if tail-limited).
- A tighter bridge check would need a pre-registered method change; none has been started.
- Note: the recipe message gave "β = 1/5" by a typo. The run uses p2's β = −1/3 (checked at runtime and in the data
  file header).

**Row 4, v1 replay at N = 100 (logged per A7 term 4): `replayed = False`, the tail-limited pattern, not a contradiction.**
- tr g = 2470.922213831767 + 7803.744734379116i (±0.035) and tr h = 11.590472881549 − 4.636608841620i (±2.4e−8).
- Both are certainly loxodromic. Squared, they reproduce the v2 midpoints of tr²/det to ~5 and ~10 digits.
- tr[g,h] = NaN: g's entries are ~1e4 with radius ~0.03, so the ball for det = ad − bc, about ±700 wide, contains 0
  and g⁻¹ cannot be bounded. This is the same loose-enclosure mechanism as row 1.
- The N = 140 replay started automatically under A7 term 4 (`qsim/mr_v2_a7_row4_N100.{json,log}`, 11 182 s).

**Noted for later; NOT part of A7, and nothing has been changed.** The bridge observed that v1's reduced form y″ = r·y is
trace-free, so every monodromy matrix has det = 1 exactly (Abel/Liouville). The true g⁻¹ is then adj(g) =
[[d, −b], [−c, a]], and the enclosure of adj(g) is a rigorous enclosure of g⁻¹ without any division.

Confirmed in the code: `ia_hub.inv` (line 262) divides by the det ball. That is the source of row 4's NaN commutator,
and very likely of row 1's 1.3e11 radius.

**Candidate amendment A8**, to be proposed only if N = 140 still cannot certify rows 1 or 4:
- v1's SL(2) path uses the adjugate;
- an assert keeps the check that the det ball contains 1;
- it applies to v1 only;
- it is filed as its own amendment through the bridge.

## A7 step 2 — row 1, v1 re-replay at N = 140: **`replayed = True` → row 1 OBSTRUCTION**

MN p1 = (β = 1/5), (E, L, μ²) = (1, 0, 9). The certificate, loops and SL(2) rule are unchanged
(`qsim/mr_v2_a7_row1_replay.json`, 21 386 s, guard ok).
- **v1 values:**
  - tr g = 1081.908658362446608144 + 1928.320008126658253952i (±5.5e−19);
  - tr h = 39.14894909118748933261 + 91.37717906664021126471i (±8e−26);
  - tr[g,h] = 51202181.92116583575865 + 30889220.29971540544108i (±0.16), certainly ≠ 2.
- **Consistency with v2:**
  - tr g² and tr h² reproduce v2's tr²/det(g) = −2547891.7087 + 4172532.2258i and
    tr²/det(h) = −6817.1486 + 7154.6411i;
  - the two commutator midpoints differ by 4.9e−8, inside both balls (v2 ±37, v1 ±0.16).
- **N = 100 result (logged per A7 term 4):** `replayed = False`, commutator radius 1.3e11. It remains in the row file
  as `v1_replay_N100`.
- The bridge's V9 numerical reproduction is consistent, with a thin margin (5.1e−8 relative).

**Verdict (as registered, via A6 + A7, both post-failure and bridge-approved): OBSTRUCTION** at MN p1, (1, 0, 9). The
argument is Lean `L6_gl2` / `L6_not_virtually_abelian` plus the cited Morales–Ramis / Ziglin theorem.

Resource note: the run took 5 h 56 min, just under the original 6 h guard. The 12 h guard set at the resume was
needed.

## Row 4, A6 + A7 term 4 — v1 replay at N = 140: **`replayed = True` → row 4 OBSTRUCTION**

MN p2 = (M, a, β) = (13, 5, −1/3), (E, L, μ²) = (1, 0, 9). This is the v1 replay of the saved v2 certificate
(`qsim/mr_v2_a7_row4_N140.json`, 11 722 s, guard ok).
- **v1 values:**
  - tr g = 2470.9222138317666648 + 7803.7447343791164096i (±2.6e−14);
  - tr h = 11.590472881549370865 − 4.636608841619880899i (±2.8e−20);
  - tr[g,h] = 9307414017.84987 − 4874574714.68493i (±1.2e5), certainly ≠ 2.
- **Consistency with v2:**
  - tr g² and tr h² reproduce v2's tr²/det targets;
  - the commutator midpoints differ by ~1.6e4 (relative ~2e−6), inside both balls (v2 ±3.2e9, v1 ±1.2e5);
  - this is consistent with the bridge's ungraded V9 agreement of 1.5e−6.
- **N = 100 result (logged):** `replayed = False`, an unbounded g⁻¹ because the det ball contained 0. It stays in the
  row file under `v1_replay_by_N`.

**Verdict (as registered, via A6 + A7 term 4, post-failure and bridge-approved): OBSTRUCTION** at MN p2, (1, 0, 9).

**MN equatorial v2, running score:** rows 0, 1, 2, 3, 4 are OBSTRUCTION. Row 5 (p2, 1,1,4) A6 is running.

**Row 5 (p2, 1,1,4), bridge V9 numerical reproduction (pre-registered): CONSISTENT, not REPRODUCED.**
- All of the bridge's gates pass: Abel 4.2e−9, convergence 2.6e−8.
- Agreement with the v2 midpoints: 1.3e−8 (g), 2.8e−7 (h), 2.7e−7 (comm). All lie inside the v2 balls, but h and comm
  miss the bridge's 1e−7 REPRODUCED bar.
- The bridge's converged tr[g,h] ≈ −1.29999e10 − 2.03482e11i. Numerically, its imaginary part is far from 0, which
  supports the thin Im-only exclusion of 2 (numerical, not a certificate).
- The grade waits for the v1 replay (N = 100, then N = 140 under A7 term 4 if tail-limited). A8 stays parked.

**Row 5, v1 replay at N = 100 (logged per A7 term 4): `replayed = False`, the tail-limited pattern.**
- tr g = −865.43764231152593 − 486.66383617065217i (±2.3e−4) and tr h = −1535.3030904994618 − 3401.5560711705944i
  (±2.7e−3).
- Both are certainly loxodromic, and their squares reproduce v2's tr²/det.
- tr[g,h] = NaN: the det ball contains 0, so g⁻¹ cannot be bounded, the same mechanism as row 4.
- The N = 140 replay from the saved certificate was launched under A7 term 4 (2 procs, 12 h guard), alongside the
  TS stage (3 threads).

## Row 5, A6 + A7 term 4 — v1 replay at N = 140: **`replayed = True` → row 5 OBSTRUCTION**

MN p2 = (13, 5, −1/3), (E, L, μ²) = (1, 1, 4) (`qsim/mr_v2_a7_row5_N140.json`, 19 371 s, guard ok).
- **v1 values:**
  - tr g = −865.43764231152593300 − 486.66383617065217147i (±2.5e−16);
  - tr h = −1535.3030904994618373 − 3401.5560711705944404i (±2.3e−15);
  - tr[g,h] = −12999927129.4587 − 203481690679.4769i (±1.6e6), certainly ≠ 2 in both parts.
- **Consistency with v2:**
  - the commutator midpoints differ by ~5e4 (relative ~2.6e−7), inside both balls (v2 ±1.6e11, v1 ±1.6e6);
  - this matches the bridge's V9 CONSISTENT agreement of 2.7e−7.
- **N = 100 result (logged):** `replayed = False`, an unbounded g⁻¹.
- **Verdict (as registered, via A6 + A7 term 4): OBSTRUCTION.** A8 was never needed.

---

# FINAL OUTCOME — MN equatorial v2 (2026-10-05, 07:02 IST): **OBSTRUCTION at all 6 rows**

| row | point, (E,L,μ²) | route | v1 N | bridge V9 |
|---|---|---|---|---|
| 0 | p1, (1,0,4) | frozen | 100 | REPRODUCED |
| 1 | p1, (1,0,9) | A6 + A7 | 140 | REPRODUCED (thin margin) |
| 2 | p1, (1,1,4) | A6 | 100 | REPRODUCED |
| 3 | p2, (1,0,4) | frozen | 100 | REPRODUCED |
| 4 | p2, (1,0,9) | A6 + A7 t4 | 140 | INCONCLUSIVE by its gates (consistent, not graded) |
| 5 | p2, (1,1,4) | A6 + A7 t4 | 140 | CONSISTENT (2.7e−7 vs a 1e−7 bar) |

- **Basis of every row.** A v2 GL(2) certificate (non-reduced ξ₁ form, Arb balls), replayed by the independent v1
  SL(2) certificate (reduced form). G⁰ is non-abelian by Lean `L6_gl2` / `L6_not_virtually_abelian` (axioms propext,
  Classical.choice, Quot.sound), plus the cited Morales–Ramis / Ziglin theorem and the finite-index fact.
- **Amendments.** A6 and A7 are post-failure, and both were bridge-approved before use. Every N = 100 failure is
  logged next to its N = 140 success.
- **Claim scope.** As registered: meromorphic first integrals, a complex neighbourhood of the equatorial solution, the
  tested parameter points and levels, and the supplied metric.
