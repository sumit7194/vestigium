# B15b-1 DRAFT (2026-10-24): plunging orbits and step-size collapse in the compiled B15 maps

**Status: DRAFT. Not registered.** For the Bridge's review, then the user's OK. No B15b gate except G2 has run.
G2 is unaffected, because all its points return.

## What was found

A development check of two returns (kerr_rs_cross.py, 100 points, n = 2, tmax 4000; not a registered gate) hung
for over an hour.

- **The point:** index 44 of that sample, w = (1.84065670, 5.39481249e-4). The first return is fine (T = 696.8). Its
  second return plunges toward the horizon.
- **Diagnosis:** scipy DOP853 with MNFlow's own field and tolerances:
  - x falls to 1.000000 and p_x to −6.9e10;
  - the step size collapses to 1.5e-12 at t ≈ 617;
  - solve_ivp stops with status −1, "Required step size is less than spacing between numbers".
- **Why it hangs:** in this time variable the horizon x = 1 is reached only asymptotically. In the compiled maps,
  t then never reaches tmax, and the h < 1e-300 guard never triggers, so they loop.
- **What MNFlow does:** it returns None ("no return") for this orbit, and it reaches that answer through an
  integrator FAILURE: t_events is empty after status −1. So the registered B15's reference map already reads a
  numerical failure as "no return", for plunges and for any other scipy failure alike. This is recorded as a
  finding about the reference. MNFlow is not changed, since B15 registered it.

## Proposed change (both compiled implementations, each in its own code)

**P1. Domain exit is a geometric "no return" (return code 0).**

- If any accepted step's end state has x − 1 < 0.05, the call returns 0 (no return), and the exit is logged:
  the stats get a domain-exit count, plus the exit's x, p_x and t.
- **Why 0.05:** it is D's registered bound (B9/S4: x − 1 ≥ 0.05). A piece whose orbit leaves D can never be certified
  by hs_cover, so treating its return as absent cannot hide a certifiable horseshoe piece.
- **Why it is geometry, not failure:** the horizon is x = 1. At the B15 level the radial roots are 0.0989M (inside
  the horizon, r₊ = 1.438M), r_s (double) and 46.79M.
  - I do NOT claim from this that no orbit on the section dips below x = 1.05 and comes back, because the
    section's points are off the exact level Q_s.
  - That claim is checked instead, by P3.

**P2. Step-size collapse is a numerical failure (−1).**

- If an accepted step has h < 1e-14·max(1, |t|), the call returns −1 (HARNESS-ERROR), never 0.
- This replaces the h < 1e-300 guard as the operative one. That guard stays as a backstop.

**P3. Check of P1 against the reference (added to G4, criterion fixed now).**

- For EVERY domain exit seen in G1, G2 or G4 (they are logged), run MNFlow from the same start.
- Criterion, two parts:
  - MNFlow must also give no return within tmax, by any route, including its own failure route;
  - the compiled orbit, integrated on from the exit state with domain exit disabled (a diagnostic switch), must reach
    x − 1 < 1e-3, i.e. it really is plunging.
- A domain exit where MNFlow returns is a FAIL of P1. It goes to the Bridge and the user, and the threshold is not
  quietly moved.

**P4. In the counted run.**

- Every domain exit is logged as data, with its start point and the exit state.
- G6 gains one decision: "no return by domain exit", with margin = (0.05 − (x_exit − 1)) relative to the map error.
  This is trivially large, since exits are found by x falling through 1.05, but it is logged for completeness.

## What it does not change

- MNFlow, and the frozen constructor's reading of None (no return).
- Every other B15b gate and criterion.

**Effect on the comparison:** on a plunge, MNFlow (None by failure) and the compiled maps (0, by domain exit)
give the constructor the same answer. They differ only in why. G1 and G4 compare return/no-return; a mismatch is
still a FAIL.

## Question for the Bridge

Is tying P1 to D's 0.05 right? The alternative is a threshold near the horizon (e.g. x − 1 < 1e-3), which is closer
to MNFlow's behaviour but arbitrary. With 0.05, the constructor stage and hs_cover share one domain, which I think
is the more defensible choice.
