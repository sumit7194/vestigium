# Amendment: SO_FIXED_REDO becomes part of the registered second-order step

Status: REGISTERED. The Bridge AGREED as proposed on 2026-11-19 (7e28f7d). The text below is unchanged from the proposal. This is gate 8 ("a registered
amendment") of SECOND_ORDER_STEP_DESIGN.md §7.

Sumit decided, relayed by the Bridge on 2026-11-19: YES to a Z-sym run with SO_FIXED_REDO=1. This amendment comes first;
the run's own registration is E_REP_PREREG.md Amendment A2.

Written by Claude Opus 5.5 (session "Quantum").

## 1. What it is

The switch is `so::SO_FIXED_REDO`, set by the environment variable `SO_FIXED_REDO`. The code is `tests/so_set.h`, around
L184–197, added in 12c5f0a and unchanged since.

After CAPD's step controller has picked the step h for the hull call (on K) and the thin call (on x), both calls are
REDONE by fresh solvers. These solvers have step control OFF and the step set to exactly that h (`turnOffStepControl`,
`setStep`). The redone enclosures (phi, remainder and enclosure, for hull and thin) replace the controlled ones.

The redo carries three BUG checks, and any of them throws (C-steps):
- the redone step must equal h, for both calls;
- the Taylor parts (phi) must equal the controlled calls' Taylor parts coefficient by coefficient;
- the thin call's value y must equal the controlled call's.

So the redo changes only the remainder and enclosure boxes, never h or the Taylor polynomial.

## 2. Why it is rigorous

Each redone call is an ordinary CAPD `encloseCnMap` at a fixed step. Its phi + rem encloses the flow and its
derivatives over [t, t + h] from K (or from x), exactly as the controlled call's does. The step design's update uses
only "some valid enclosure at step h". So swapping one valid enclosure for another valid one, at the same h and with the
same Taylor part, keeps every inclusion in SECOND_ORDER_STEP_DESIGN.md §3 and in E_REP_PREREG.md §2. Nothing else in the
step reads which call produced the boxes.

## 3. Why it is needed (the mechanism, from the record)

- **Mechanism, c3a1b5e.** At the spike step before step 1322, the CONTROLLED hull call gave a second-order remainder
  (box2) of 6.40e-12. A fresh fixed-step call at the same h gave 1.57e-13, 41× smaller, with an identical Taylor part.
  795ba68 showed this is not a bookkeeping artefact: the controlled call's remainder is valid but much wider.
- **Effect without the switch.** The REDO-off runs blow up through the swing:
  - so_mn/run_1e-7.out: maxE 1.29e-5 at step 1400, then 6.8e-4 and 2.6e-2, then "THREW at step 1465 t=289.0486:
    S4: x - 1 < 0.05 possible";
  - so_mn/rerun_diag/run2_1e-7.out reproduces it.
- **Effect with the switch.** In fix_test/RAMP_WINDOW_RESULT.txt (eba5620), the criterion fixed with the Bridge before
  the run was MET through the old ramp window:
  - box2 stayed within 1.03× of its local median;
  - there was no period-2 pattern;
  - the maxE W0 exponent was 3.05;
  - the controller had shrunk h on 40 of 80 steps, where the controlled box2 would have been up to 2.2e6× larger;
  - there were 0 Taylor mismatches.
- **The full fix test, 8c21b7c (fix_test/FULL_RESULT.txt).** The swing passed with no spikes or runaway. B17 passed at
  290.8497 for 1e-7 (u2 1.50) and failed at 291.8852 (u2 12.67). The wrapping test later attributed that failure to
  wrapping (c22d325).
- **Identity with the switch OFF.** kr_ref is bit-identical (fix_test/VALIDATION.txt).

## 4. What is registered

1. For MN second-order-step runs that count, SO_FIXED_REDO=1 is part of the registered step, from this amendment on.
2. The binary default stays OFF. Identity controls against the older REDO-off references (kr_ref, T1) still run with it
   OFF and must stay byte-identical.
3. Runs already registered with REDO OFF keep their registrations and their outcomes. The Z-sym main run (E_REP_PREREG.md,
   PID 37679) is read as registered. This amendment does not change its reading.
4. Every run's launch record states the switch value.

## 5. Not covered

- The amendment says nothing about why CAPD's controlled call returns the wider remainder; that is CAPD internals. It
  rests only on both enclosures being valid.
- Cost: the redo adds two fixed-step Cn calls per step. Measured cost is reported with the run.
