# R3 Kerr negative control at matched (E, L_z), outcome as registered (2026-10-20): **no hyperbolic seed**; the covering machinery was not exercised

**Setup (prereg §6.3, B14, A-K20 FINAL a713523):**
- the Kerr limit of F5-R: (M, a) = (89, 80), q = 0, at A-K20's level (E, L_z) = (19/20, 267);
- section {y = 0, p_y > 0};
- my B10-regularised field, S5-gated (`mn_s5_gate_ak20.json`);
- the FROZEN B14 constructor (1da283c), plugged in through `mn_numerics.plug_into_constructor`, unedited.

**K-1** (the constructor exactly as for MN: saddles seeded at A-K20's F5-R UPO section points):
- **None of the 12 seed points lies in Kerr's allowed region at this level.** The p_y lift is imaginary at every one
  (`horseshoe_results/kerr/r3_k1_saddles.json`), so the constructor stops at step 1.
- **Why:** MN's inner bound region x ∈ [1.92, 5.03] on the equator, where A-K20's chaotic core lives, does not exist
  in Kerr. At this level Kerr's equatorial allowed region is only x ∈ [8.01, 30.9]. For MN F5-R the regions are
  [1.23, 1.63] (next to the excluded CTC zone), [1.92, 5.03] and [5.46, 31.1].

**K-2** (seed at Kerr's own unstable orbit of the same (E, L_z) and its separatrix):
- **Not possible at this level.** Kerr's equatorial allowed intervals at p_x = 0 were tracked against E at
  L_z = 267:
  - the bound zone exists up to about E ≈ 0.965;
  - the barrier to the plunge opens only above about E ≈ 1.02.
- So the unstable circular orbit is not bound at E = 19/20. At this level Kerr's allowed region is a single regular
  bound zone with no hyperbolic periodic orbit in it, and there is no separatrix to seed from.

**Which check fails:** constructor step 1 (no hyperbolic seed), in both branches. No covering relation was attempted.

**Assessment:**
- This is consistent with the registered prediction: no ρ > 1 is certified.
- But it is the WEAK form of the negative control. The sweep's caveat applies in full: a broken pipeline would also
  "find no horseshoe" here.
- A Kerr control that exercises steps 2–4 (connection finding and coverings) needs a level at which Kerr HAS a bound
  hyperbolic orbit: an unstable spherical orbit with E < 1, whose separatrix is homoclinic and non-transversal
  (Levin & Perez-Giz 2009). There, the expected failing check is step 2: no transverse crossing with angle ≥ 0.01.
  That is a different level from A-K20's, so it needs its own amendment before running (proposed as B15, not
  registered yet).
