# B15b DRAFT, revision 2 (2026-10-24): a compiled map for the B15 constructor stage

**Status: DRAFT. Not registered.** Revision 2 takes in the Bridge's review of revision 1. Corrections to that review
are marked "Correction".

- **Before anything is used:** no counted B15 run uses a compiled map until this text, as finally reviewed, is in
  PREREG_chaos_horseshoe_phase2.md with the user's OK, and gates G0–G5 have passed. G6 runs alongside the counted run.
- **State of the Python B15:** b15_kerr.py, the original NON-checkpointed script, PID 24176, has been running for
  about 4 days.
  - It finished step 1, and its W^u arcs (26,047 points in 300,804 s).
  - It is **still running.** It will be stopped at the macOS 27.0.1 update (the user's decision) and not relaunched.
  - Its arc points exist only in that process's memory. No journal was written, so none can be reused.

## Why

The Python B15 (MNFlow, scipy DOP853) averaged about 11.5 s per W^u arc point. The compiled maps take about 4.5 ms
per return with the Jacobian, near the saddle.

## What changes, and what does not

- **Changes:** only the implementation of P, Pinv and py_of that the frozen B14 constructor calls through
  `mn_numerics.plug_into_constructor`. The adapter is `kerr_compiled.CompiledFlow`, with MNFlow's signatures and
  return conventions.
- **Unchanged:**
  - hs_construct.py;
  - every B14 and B15 threshold;
  - TMAX = 1e6;
  - the seed, the step logic, and the registered prediction;
  - pcache journalling, which is now used, so the run is checkpointed.
- **Primary implementation:** `kerr_rs` (Rust).
- **Second implementation:** `kerr_p.cpp` (C++, Boost.Odeint). It has the same field and C ABI, and is used for
  cross-checks only.
- **Reference:** MNFlow.

**Integrator and event changes, required before the gates.** These follow the Bridge's points 2 and 3. Each
implementation gets them through its own code.

- **E1. Event located in the step's local variable.** Bisection runs on θ = (t − t0)/h ∈ [0, 1] of the accepted step,
  to |Δθ| ≤ 4e-16. That is relative to the step, not to t.
- **E2. Step to the event.** One real integrator step of length θ*·h is taken from the accepted step's start, and
  that state is used, not the interpolant. Its error estimate must pass the same tolerance, or the step is halved
  and repeated.
- **E3. Logged for every crossing:**
  - the bound |ẏ|·h·Δθ;
  - the difference between the interpolated and the stepped state;
  - the event time.
- **E4. The return time** is accumulated as Σ(t0 + θ*·h) in compensated (Kahan) summation, so the ulp of t does not
  enter the state. Only T itself carries it.

MNFlow locates events with brentq (xtol = rtol = 4·EPS in t) on DOP853's dense output, which is 7th order. Its event
state is therefore an interpolant, and its t-resolution is ~1e-16·t. This is recorded as a property of the
reference, not changed.

## Disclosure: a bug in kerr_p.cpp, found by the second implementation

As committed in 18c33e0, kerr_p.cpp's slide-back correction ran in place. The i = 1 iteration zeroed V[1] before the
p_x and p_y rows used it:

- det DP came out 0.57–0.61 instead of 1;
- the DP entries were off by up to 1.3e-2;
- the x row was unaffected.

The Rust port copies the y row first. It matched central finite differences to about 1e-8, with det DP = 1.000000.
The fix is in ce3a599. **No counted result used kerr_p's DP.**

## Field provenance (common mode)

All three implementations evaluate expressions from one sympy source:

- the C++ and Rust code is generated from it after CSE;
- MNFlow lambdifies it.

SHA-256 prefixes at revision 2:

| File | SHA-256 prefix |
|---|---|
| mn_codegen.py | 6034250777bd41c0 |
| gen/mn_field.h | 4c1c7b57bcbead23 |
| kerr_rs/src/mn_field.rs | 7ae5ec20f8da42e0 |
| mn_codegen_rs.py | 9e242873f870d538 |
| mn_numerics.py | 4728b71569201e31 |

The registered text records the hashes at registration.

**Correction:** I find no "V15 Ricci-flat" validation of this source in the repo. The vacuum checks on record are
for the supplied metrics of the MR and TS work, and are pointwise. This source's gate is the B10 codegen gate,
which checks C++ against mpmath of the same sympy expressions, so it is not independent of the source.

For B15 the system is Kerr, which gives a source-independent physics check: G0b below.

## Gates

Criteria are fixed here, before any gate output is read.

**G0. Field accuracy in double, along the real excursion.**

- Points: 100 states sampled at equal arc length along two compiled W^u orbits from the G4 rule, covering
  x ∈ [1.05, 110] and the y range they visit.
- Compared: the generated field (Rust, C++, and MNFlow's lambdified field) against 50-digit mpmath of the same sympy
  expressions, at the same double inputs.
- Criterion: |Δf_i| ≤ 1e-12·‖f_ref‖∞ for every component at every point. Componentwise relative errors are also
  reported, but a component near zero cannot carry a relative criterion.
- On a failure: a rewritten far-field form, never a looser gate.
- **Correction to the review:** the excursion turns at 46.79M. That is r ≈ 4164 in the field's M = 89 units, so
  x = (r − M)/k ≈ 104.5, not r ≈ 4.7e7. The concern still stands at x ~ 100, with high-degree polynomials in x,
  just less extreme.

**G0b. Kerr integrals, independent of the sympy source.**

- Along the same orbits, check H = −½ and Carter's constant Q. Q comes from the textbook Kerr expression in
  Boyer–Lindquist coordinates, mapped by r = M + k x and cos θ = y, with the momenta transformed accordingly.
- Criterion: relative drift ≤ 1e-10 per return, for each compiled map.
- This is the only check here that can see a source-level field error.

**G1. Against MNFlow.**

- Run: `kerr_p_gate.py 12 2000 <lib>`, for kerr_rs and the fixed kerr_p, after E1–E4.
- Criterion: max relative difference ≤ 1e-10 in py, P, T, DP and Pinv. A return mismatch is a FAIL.
- The gate run started on 2026-10-24 loaded the unfixed kerr_p.dylib. It is a demonstration of the bug, not G1.

**G2. Cross-implementation.**

- Run: `kerr_rs_cross.py 200 2000 1`, after E1–E4.
- Criterion: ≤ 1e-10 in everything, with 0 mismatches.
- **Disclosed:** the pre-E1–E4 version has already been run:

  | Quantity | Worst relative difference |
  |---|---|
  | P | 2.2e-11 |
  | DP | 7.9e-13 |

  So G2 is not blind.

**G3. Symplectic check.**

- Criterion: |det DP − 1| ≤ 1e-8 at every G1, G2 and G4 point, for both libraries and MNFlow.

**G4. Long returns, with the criterion unscaled.**

- **Points, fixed now:**
  - seeds z* + s·e_u, for s ∈ {1e-4, 1e-3}, on both branches;
  - each iterated with kerr_rs until it comes back within 0.01 of z*, or until 200 returns;
  - from each of the 4 orbits, the first iterate past x = 2, 5, 10, 20, 50, 100, plus the iterate with the largest T.
    That gives ≤ 28 points. Ties go by iterate index.
  - These are not constructor outputs. **Correction:** no journal of the main run exists, and the kill-test journal
    only reaches x ≤ 2.24 and T ≤ 730.
- **Compared:** one return by kerr_rs, kerr_p and MNFlow (tmax 1e6).
- **Criterion:** ≤ 1e-10 relative in P, T and DP, unscaled.
- **Reference accuracy:** MNFlow self-convergence (rtol = atol = 1e-11, 1e-12, 1e-13) at the 3 points with the
  largest T. The reference is accepted only if its 1e-12 value is within 1e-11 relative of its 1e-13 value. A
  reference that fails this cannot gate.
- **On a failure:** self-convergence of each implementation at rtol = atol = 1e-11, 1e-12, 1e-13, 1e-14 on the failing
  points, to measure each one's actual error.
  - If a real floor appears, it gets its own registered amendment, with the measured error model and its cause.
  - Otherwise the tolerance is tightened and the whole gate set is rerun.
  - No scaled criterion.

**G5. End-to-end step 1.**

- Run: `find_periodic` from the seed with kerr_rs.
- Criterion: z within 1e-9 of the recorded Python step 1, and λ_u within 1e-8 relative of 62.62026858030255.
- This is a validation, since the Python step 1 is known.

**G6. Decision margins (runs alongside the counted run).**

- The constructor stays frozen. Margins are computed by a read-only wrapper and from the recorded data, not by
  editing hs_construct.
- **The decisions:**
  - Newton convergence (step 1);
  - the saddle classification;
  - each crossing's angle against the 0.01 minimum;
  - each angle against 10·θ_floor;
  - the accept/reject of a connection.
- eps, K and dmax are construction parameters, not comparisons. They are not decisions and get no margin.
- **Criterion:** margin ≥ 10 × (map error × local gain).
  - The map error is the measured G4 self-convergence error at the matching T.
  - The local gain is ‖DP‖ composed over the returns from the arc's initial segment to the decision point, taken
    from the map's own Jacobians; near the saddle that is about 62 per return.
- **A thin margin** is flagged. The calls feeding it are recomputed at rtol = atol = 1e-14, and the decision must be
  unchanged. Any decision that changes is reported as a result, not silently replaced.

**On any failure:** fix the implementation or tighten the tolerances, and rerun all of G0–G5. A criterion is never
relaxed (B16 and the rigour rule). A criterion change is a new registered amendment, with its reason.

## The run (after G0–G5)

- Script: b15_kerr_ck.py with B15_MAP=rust (default MNFlow), under pcache.
- New journal and JSON names. The Python step 1 is compared (G5), not reused.
- Resources: one process, not low-priority. No wall-time cap (B16).
