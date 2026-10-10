# Pre-registration — TS δ=2 obstruction at the levels of ansatz's chaos search (2026-10-10)

**Committed before any obstruction computation at these levels.** Approved by the bridge (2026-10-10, "GO for
item 1", under the user's standing instruction). The row list was supplied by ansatz-machine, in file units.

**Why.** The 6 levels of `PREREG_ts2_v2.md` were chosen to be rational, and they turn out to be **plunge-only**
(`qsim/ts_bound_orbits_findings.md`). This stage puts the theorem on the **bound orbits** that ansatz's
Lyapunov/frequency-map search actually probes. That includes Dubeibe et al. 2007's Fig. 1 level, the source of the
"completely integrable" claim, and the near-separatrix levels where ansatz's pre-registered hypothesis expects
thin chaotic layers.

## Setup (unchanged from PREREG_ts2_v2.md)

- **Metric.** Ansatz's WP components, σ = 1: t1o2 for p = 3/5, t1o3 for p = 4/5. The mass is M = 2σ/p (10/3, 5/2).
- **Hamiltonian and solution.** H = ½ g^{ab} p_a p_b = −μ²/2, with p_T = −E and p_φ = L, on the equatorial
  solution Γ: y = 0, p_y = 0.
- **NVE form.** The non-reduced ξ₁ form for v2; the reduced forms for v1 and 2b′.

## Rows (p, E, L, μ²), file units; real motion classified by `qsim/ts_bound_orbits.py` (exact root isolation)

| row | p | E | L | μ² | role (ansatz) | real equatorial motion (checked) |
|---|---|---|---|---|---|---|
| 1 | 4/5 | 47/50 | −39/5 | 1 | Dubeibe Fig. 1, far field | PLUNGE (ring, 3.428); **BOUND [9.956, 21.923]** |
| 2 | 3/5 | 47/50 | −52/5 | 1 | same physical level, far field | PLUNGE (ring, 2.032); **BOUND [17.962, 26.905]** |
| 3 | 4/5 | 19/20 | −773/100 | 1 | near separatrix (L_sep = −7.700) | PLUNGE (ring, 4.234); **BOUND [6.310, 33.113]** |
| 4 | 4/5 | 97/100 | −201/25 | 1 | near separatrix (L_sep = −8.000) | PLUNGE (ring, 3.936); **BOUND [5.913, 67.105]** |
| 5 | 4/5 | 97/100 | 1051/100 | 1 | near separatrix, other sense (+10.475) | PLUNGE (ring, 10.485); **BOUND [14.845, 51.703]** |
| 6 | 3/5 | 19/20 | −93/10 | 1 | near separatrix (L_sep = −9.267) | PLUNGE (ring, 3.848); **BOUND [5.293, 49.127]** |
| 7 | 3/5 | 97/100 | −48/5 | 1 | near separatrix (L_sep = −9.567) | PLUNGE (ring, 3.700); **BOUND [5.024, 93.946]** |
| 8 | 3/5 | 97/100 | 287/20 | 1 | near separatrix, other sense (+14.30) | PLUNGE (ring, 15.767); **BOUND [21.315, 65.672]** |

Every row has a closed bound equatorial pocket. Γ is the complex phase curve of the equatorial motion at that
level, which contains the real bound orbit.

**Controls (must NOT obstruct):** Kerr-WP at the levels of rows 1 and 2 (file KERR_P2 at row 1's level, KERR_P1
at row 2's level). Kerr is integrable, so the v2 search must find no certificate, and 2b′ must not output
OBSTRUCTION. These are the same kinds of checks as VCTRL and the 2b′ V-neg rows, re-run at the new levels.

## Per row, in order

1. **Gates.**
   - Exact y = 0 invariance.
   - Provenance: the v2 ξ₁ pipeline against the Stage-2 loader (`mr_ts2.load_wp` + `mr_nve`), relative
     difference < 1e−25 at 3 points.
   - Failing either gate stops that row.
2. **Route A — 2b′** (Kovacic / differential Galois, root-free; `mr_factor_route.analyse_v2`), on both reduced
   forms ξ₂ and ξ₁.
3. **Route B — certified monodromy.**
   - The frozen v2 driver with the A6 search policy (complete locator, skip-not-abort), which is
     pre-registered here.
   - Every certificate is then replayed by v1 (reduced form, SL(2) rule) at N = 100.
   - **Pre-registered here, not post-failure:** if the N = 100 replay fails without an error (the tail-limited
     pattern), it is repeated at N = 140, and both results are logged. This is the A7 term-4 rule from the MN
     stage, adopted in advance.
4. **Recipes** go to the bridge for V8-mono reproduction.

## Verdict rules (fixed now)

Each route was validated separately: 2b′ in the re-validation d77605e; v2 + v1 in the iahub v2 ladder. Neither
route ever outputs NO_OBSTRUCTION, so a route conflict is impossible by construction.

- **OBSTRUCTION (two routes):** 2b′ gives OBSTRUCTION on at least one form, AND v2 certifies with a successful v1
  replay.
- **OBSTRUCTION (single route: A or B):** only one route succeeds. The row is reported with that label.
- **INCONCLUSIVE:** neither route succeeds. This says nothing about integrability.
- **A control obstructing** (2b′ OBSTRUCTION, or a v2 certificate on Kerr) **stops the stage** and is reported
  as a tool failure.

**Wording, per row.** At (p, E, L, μ²), the reduced TS δ=2 geodesic flow H_{E,L} admits no additional first
integral that is meromorphic in a neighbourhood of the equatorial phase curve Γ. **The real part of Γ includes a
bound equatorial orbit.** Scope: as in PREREG_ts2_v2 (meromorphic integrals only; complex neighbourhood; these
points; the supplied metric).
- It says nothing about where chaos is, or how large the chaotic layers are.
- It does not contradict Dubeibe's regular-looking sections, which are a statement about the measure and
  visibility of chaos, not about integrability.

## Setup correspondence: is the run testing the claim it will be quoted for?

**The claim this will be quoted for.** "The levels at which ansatz searches for chaos, including Dubeibe's
'completely integrable' Fig. 1 level, admit no additional meromorphic first integral."

**The condition actually tested.** At each (p, E, L, μ²) in the table: no first integral of H_{E,L} meromorphic
in a neighbourhood of the equatorial phase curve Γ at that level. This **matches** the claim:
- the rows are exactly ansatz's levels, in the same units and sign convention (confirmed by ansatz: M = 2σ/p,
  L < 0 for Dubeibe);
- the bound pocket at each level was checked to be real and to lie on Γ;
- the metric is the same WP file that ansatz's integrator uses.

**Gaps that remain, stated so they are not overclaimed:**
- meromorphic integrals only;
- the complex neighbourhood of Γ, not a real region;
- Γ is the equatorial orbit, while Dubeibe's sections are meridional (off-equator) motion at the same (E, L);
- the result covers these points only.

## Predictions (filed now)

- **P1. All 8 rows OBSTRUCTION by both routes.** Reason: at all 6 earlier levels the 2b′ local data were
  level-independent in their essentials: the log at x = 0 (N = 2), b = −3/16 at the ring and the turning points,
  and order 4 at ∞. Only the turning-point sextic moves with the level.
- **P2. Both Kerr controls are clean:** no certificate, and no 2b′ OBSTRUCTION.
- **P3. Cost:** each row under 2 min with 3 threads and < 200 MB. The pocket's far edge (up to x ≈ 94) may
  lengthen the loops, so P3 is the least certain prediction.
- **If P1 fails at a row** (INCONCLUSIVE or single-route), it is reported as such and not re-run with changed
  settings. Any change would be a new, labelled amendment through the bridge.

## Resources

One guarded child per row: 2 GB, 1 h, ≤ 3 threads. Ansatz's chaos scans run alongside (about 1 GB, a few
threads), so the total stays within the box. Commit and push per row.

## OUTCOME (2026-10-10, 04:49 IST): **all 8 bound-orbit rows OBSTRUCTION (two routes); both Kerr controls PASS**

Files: `qsim/mr_ts2_chaos.{txt,json}`, `qsim/mr_ts2_chaos_row{0..9}.{json,log}` (full recipes: base, loop geometry,
words, v2 and v1 midrads). Every row was guarded; peak ≤ 138 MB.

| row | p | (E, L, μ²) | gates (provenance) | 2b′ ξ₂ / ξ₁ | v2 cert | v1 replay | v2 tr[g,h] | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 Dubeibe Fig. 1 | 4/5 | (47/50, −39/5, 1) | pass | OBS / OBS | yes | N=100 ✓ | 0.97422 (real) | **OBSTRUCTION, two routes** |
| 2 | 3/5 | (47/50, −52/5, 1) | pass | OBS / OBS | yes | N=100 ✓ | 4.4972 − 7.3406i | **two routes** |
| 3 | 4/5 | (19/20, −773/100, 1) | pass | OBS / OBS | yes | N=100 ✓ | 0.63414 (real) | **two routes** |
| 4 | 4/5 | (97/100, −201/25, 1) | pass | OBS / OBS | yes | N=100 ✓ | 0.81868 (real) | **two routes** |
| 5 | 4/5 | (97/100, 1051/100, 1) | pass | OBS / OBS | yes | N=100 ✓ | 15.462 − 18.659i | **two routes** |
| 6 | 3/5 | (19/20, −93/10, 1) | pass | OBS / OBS | yes | N=100 ✗ → N=140 ✓ | 1.29013 (real) | **two routes** |
| 7 | 3/5 | (97/100, −48/5, 1) | pass | OBS / OBS | yes | N=100 ✗ → N=140 ✓ | 1.37113 (real) | **two routes** |
| 8 | 3/5 | (97/100, 287/20, 1) | pass | OBS / OBS | yes | N=100 ✓ | −4.1810 − 14.056i | **two routes** |
| ctrl | Kerr 4/5 | row-1 level | pass | INC / INC | none | — | — | **PASS** |
| ctrl | Kerr 3/5 | row-2 level | pass | INC / INC | none | — | — | **PASS** |

- **Provenance** worst relative difference ≤ 2e−54 across rows.
- The N = 140 replays in rows 6–7 follow the **pre-registered** retry rule (tail-limited at N = 100). Both N = 100
  results are logged in `v1_replay_by_N`.
- **v1 vs v2** commutator midpoints agree to ≥ 20 digits in every row.
- In rows 1, 3, 4, 6 and 7, tr[g,h] is real and in (0, 2), with v1 radius ≤ 0.15, so it is certainly ≠ 2.
- In every near-equatorial "−L" row, tr²/det(h) is real and of order 10⁴, i.e. real-hyperbolic, well outside
  [0, 4].

**Predictions.**
- **P1 (all 8 OBSTRUCTION by both routes): HELD.**
- **P2 (Kerr controls clean): HELD.**
- **P3 (each row < 2 min): MISSED narrowly.** Row 7 took 137 s, because of its N = 140 replay.

**Verdict (as registered), per row.** At each (p, E, L, μ²) above, the reduced TS δ=2 geodesic flow H_{E,L} admits
no additional first integral meromorphic in a neighbourhood of the equatorial phase curve Γ, **and the real part of
that Γ includes a bound equatorial orbit**. That includes **Dubeibe et al. 2007's Fig. 1 level**, whose
regular-looking sections were the basis of the "completely integrable" description.
- **Scope, unchanged:** meromorphic integrals; the complex neighbourhood; these points.
- This says nothing about where chaos lies or how large the chaotic layers are. It does not contradict regular
  sections; it rules out the integrability reading of them.
- Γ is the equatorial orbit, while Dubeibe's sections are meridional motion at the same (E, L).

**Bridge V8-mono numerical reproduction (pre-registered, 2026-10-10).**
- **REPRODUCED:** R2 (3.0e−8), R5 (2.4e−10), R8 (7.6e−11).
- **INCONCLUSIVE by the bridge's own gates:** R1, R3, R4, R6, R7.
  - Its complex128 DOP853 transport fails convergence (2e−7 to 1e−5), and for R6/R7 it also fails Abel
    (~1.7e−7). These are exactly the rows with real tr[g,h] ∈ (0, 2) and a real-hyperbolic h of order 1e4.
  - Ungraded: its values agree with these certificates to 6e−8 to 6e−6, and all are clearly ≠ 2.
- The bridge is adding a pre-registered high-precision (mpmath, 30+ digit) transport for those five rows.
- The verdicts above rest on the two certified routes, which are unaffected; the bridge check is corroboration.

**Bridge V8-mono HP (pre-registered high-precision mpmath Taylor transport; dps 30 vs 40, convergence ≤ 1e−22):
ALL 8 ROWS REPRODUCED**, including the five that were INCONCLUSIVE under complex128.
- Agreement is at the ~1e−16 precision of the float targets the bridge holds.
- Checked against the full 25-digit strings: R3 tr[g,h] = 0.6341438643859946198841734… and R6 =
  1.2901346423911607098364738… agree to every digit sent.
- The real-hyperbolic rows come out real to |Im| ~ 1e−30 to 1e−35.
- **The obstruction at the bound-orbit levels, including Dubeibe's, is independently reproduced end to end.**
