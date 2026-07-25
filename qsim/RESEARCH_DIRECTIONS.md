# Research directions for the sister projects (option 3: "poke at genuinely open problems")

Parked 2026-07-05 for later. Context: after building the qsim foundations lab (all
reproductions of known physics — great as a learning tool, not new physics), the
real interest is option 3 — pointing conjecture_machine (and SpaceTime / the
bridge) at genuinely OPEN problems, not textbook reproductions. Option 2 (port the
apps into a teaching tool) is agreed as a LATER move, only if things reach that level.

## Where the machine actually stands (from a fresh capability re-map, §113 / 97 batteries)
- Rediscovered 26 KNOWN solution families flawlessly; found ZERO new ones. Its own
  DECISIONS log (D25) + a 2026-06-23 prior-art audit warn against novelty claims
  (one earlier "rotating-EdGB gap" claim was overturned). So we are not fooling
  ourselves — the contribution so far is the METHOD, not any discovery.
- CAN DO: exact symbolic proofs in 3–14 dimensions, but essentially only for
  non-rotating, spherically symmetric setups (everything depending on one radius
  variable r), plus rotation in special coordinates that stay polynomial (u=cosθ).
- ALREADY BANKED (semi-publishable genre): a 4-coefficient closed-form fit for EdGB
  black holes (modified gravity, known only numerically since 1996), accurate to
  0.53% on SEALED holdout. Literature precedent (Konoplya–Zhidenko) for this genre
  being used/cited like an exact solution.
- WALLS: anything genuinely two-variable (r AND θ, i.e. serious rotation) blows up
  the algebra engine (confirmed by killed 7.5h runs). 4D exact solutions are the
  most-mined turf in physics (Stephani, ~century of work) → blind prospecting there
  is a lottery ticket.

## The filter (a target must pass all four)
1. Fits the one-variable ansatz world (or rational-coordinate stationary).
2. Sits OUTSIDE the exhaustive catalogs (higher-D, modified gravity, coupled matter).
3. Pays out even on FAILURE — their obstruction-extraction turns dead ends into
   theorems ("this can't exist because X").
4. Has a verifier the machine itself runs (Einstein eqs / known ODEs / separable).

## TIER 1 — realistic, instrument-grade

### 1. Consistent-truncation prover → a "flux atlas"  [TOP PICK]
Direct continuation of the §111–113 Kaluza–Klein thread. Rare capability shown:
hand it a hidden-dimension setup, it either proves consistency or EXTRACTS THE
PRECISE OBSTRUCTION. In string/supergravity research this is done by hand, case by
case, and people get it wrong. Next rungs: add FLUXES (field strengths wrapped on
the hidden torus) + the θ-odd twist they already offered, and machine-map WHICH
combinations of twists/fluxes stabilize WHICH moduli, with proofs. Even if each
entry is individually known, an automated prover with three-valued verdicts is a
tool the field lacks. Lowest risk; machinery already tooled; contribution = the
instrument. START HERE.

### 2. Closed-form-approximant factory
Industrialize the EdGB trick across modified-gravity theories whose black holes are
known ONLY numerically — especially SCALARIZATION models (BHs that spontaneously
grow a scalar coat above a coupling threshold; hot since ~2018, relevant to GW
tests). Pipeline each time: shoot numerics → GP fits compact closed form → sealed
holdout. The GW community USES such formulas. Deliverable: a validated formula bank
across 3–4 theories. Nearest thing to "useful to working physicists."

### 3. Hair / no-hair phase diagram
The machine already proved a no-hair theorem by extracting the obstruction.
Scalarization models live on that theorem's boundary — whether hair grows depends on
the coupling function. The ONSET of hair is a one-variable eigenvalue problem
(inside reach). Machine-prove the onset condition across FAMILIES of coupling
functions → a phase diagram with proofs. Corners genuinely not written down.

## TIER 2 — one calibrated moonshot

### 4. The 5D charged rotating black hole
Famous gap: in 5D the rotating BH (Myers–Perry) is exact; the charged rotating one
is exact ONLY with an extra supergravity interaction term (CCLP). In PLAIN
Einstein–Maxwell (no extra term) NO closed form has ever been found — only numerics.
Why not hopeless here: with EQUAL spins in both planes the problem collapses to ONE
variable → inside the walls. Ask: hunt rational-form families for the equal-spin
charged rotating solution; if nothing, EXTRACT THE OBSTRUCTION — a machine-grade
account of why the supergravity term makes it solvable while pure EM resists.
Honest odds of the solution: low (experts suspect none in closed form). Odds the
obstruction is interesting: decent. Bounded — one battery, not a career.

## TIER 3 — sister-project plays

### 5. SpaceTime: complete the trilogy — discover the axion
They found mass, then charge, in the latent. Capstone: generate twisted-torus wave
data, ask whether the bottleneck discovers THREE latents (two sizes + the twist),
and the deep version — whether the latent space's GEOMETRY reproduces the curved
moduli space (hyperbolic plane SL(2,R)/SO(2)) that conjecture_machine just proved in
§113. "Network discovers moduli-space geometry from shadows alone" = publishable-
genre ML-physics demo.

### 6. Three-project pipeline: analog gravity  [FLAGSHIP, later]
Uses EVERYTHING we own. Real physics: sound waves in a flowing quantum fluid obey
the same math as light near a black hole; flowing faster than sound = a sonic
horizon; Steinhauer's lab measured analog Hawking radiation in exactly such systems.
Play: qsim simulates the flowing condensate with a sonic horizon → SpaceTime's
network LEARNS the effective curved metric from wave data alone → conjecture_machine
VERIFIES and classifies the learned metric. Simulate → discover → prove, one artifact
through three machines. As pure research: crowded. As a demonstration of the project
ecosystem: nothing else touches it — and it earns the quantum project a real
research-adjacent role rather than teaching-only.

## Recommended firing order
- #1 NOW (flux atlas — offered θ-rung + fluxes; they're warmed up).
- #2 second (approximant factory — most useful-to-others per unit effort).
- one battery on #4 (bounded moonshot).
- hand SpaceTime #5.
- #6 as flagship once the others are moving.

## Workflow discipline (the thing that separates option 3 from self-deception)
The bottleneck for "is it actually new?" is literature-checking. That job runs from
the quantum-session side: every time a machine result lands, run the prior-art search
BEFORE anyone gets excited. Their own history (the overturned rotating-EdGB claim)
shows why this is non-negotiable.
