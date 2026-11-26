# Kerr negative control: rethink note (2026-11-27; no runs)

Written by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request, after Sumit's decision to pause the 5 Air kerr_e chunks. It is a note for Sumit, not a registration. Nothing here changes any job. I have not opened the sealed Fable Kerr prediction (fd22a7f), and nothing below depends on it.

## (a) Can the control stop at the first certified failure? What is the cheapest sound design?

**Under the registered readings, yes: the first certified failure decides the chain.**
- B15c §4 and B15c-1 give the per-chain rule: ρ > 1 only if EVERY required covering is CERTIFIED.
- So one CERTIFIED-FAIL covering fixes the chain as CERTIFIED-FAIL. Nothing after it can change the class, and F7 can no longer trigger on that chain.
- Stopping there loses nothing the registered reading uses.

**But the registered class needs the end of the run.**
- CERTIFIED-FAIL = `DONE` + `COVERS` ≠ 1 + a certified FAILPIECE or `orient_certified_fail=1`. The HARNESS-ERROR guard reads the same COVER line.
- An early stop therefore needs a labelled amendment, registered before any further record is read.
- Proposed wording: a covering is CERTIFIED-FAIL at the first complete EP record (ending ` #`) that has `cert_fail` > 0 and a matching `EF … CERTIFIED` line in the checkpoint. The same applies to a certified orientation contradiction in the landing counts (d0/d1) summed over complete EP records.
- The harness guard becomes: the out file has no `COVERS=1`, and that EP record's EF lines are present.
- All other Kerr chunks then stop. They are paused, or ended only on Sumit's word.

**Where a certified failure can come from.**
- On the twin, (a) pieces never certified a failure. They failed uncertified, at the cap or depth, which is why B15d-2 put edges first. So the decisive certificates are edge ones: a leaf certified not to leave N_j's u-range, or orientation.
- Orientation needs side-1 landings. hs_cover runs all 64 side-0 pieces of a chunk first (hs_cover.cpp:490), so no orientation contradiction can appear before piece 65 of a chunk.
- For N1N2 on the Mac mini that is about 3.7 + 64 × 4.0 h ≈ 11 d after its start, so around 12-07. On the Air it would be 2–4 weeks.

**Cheapest design that still guards against an unsound pipeline.** It has three parts, and all three need registration first:
1. **Early stop** as above.
2. **Order, not a subset.** Run first the coverings where integrability predicts failure: the closing coverings back toward N0 (N5⇒N0, N5⇒N1). Stop at the first CERTIFIED-FAIL. Only if those CERTIFY do the other coverings run, which is the path toward an F7 STOP. Every covering still runs if no certified failure appears, so the F7 check is kept. A subset would lose it.
3. **Edge order inside a chunk.** Alternate side 0 and side 1, or run side 1's first piece early, so that an orientation contradiction can show within about 2 pieces (~8–16 h on a Mac-mini core) instead of about 65.
   - This needs a new edge-order command, so a new binary with A8-style identity and interrupt tests.
   - A running chunk can't switch binary, so it applies only to new launches.

**What the Kerr control does and does not guard.**
- It catches an unsound pipeline only if the fault makes every required covering certify. It does not catch a single false certificate.
- The stronger soundness guards are:
  - the §6.4 wrong-configuration controls (W1–W3 must be REJECTED);
  - the B15e twin (swap CERTIFIED-FAIL);
  - the A-series identity and interrupt tests;
  - on MN, the second implementation (S6).
- So an early stop costs little guard power.

## (b) What does "pieces pass" mean for a negative control? Where must Kerr fail?

**What a passing record means.** An EP record such as `4 0 0 0 4` reads: 4 leaves, 0 fails, 0 certified fails, all 4 certified landings on one side.
- That is a local fact about one piece of one u-edge: its image leaves N_j's u-range on one side.
- Integrability does not forbid it. Transport along the separatrix stretches an edge just as a covering would.
- So passing pieces are expected, and they are evidence neither way.

**What has already finished.** The N0⇒N0 and N0⇒N1 edge chunks finished before the outage. Their outputs are in b15d/kerr_e/ and are classified only by the B15d-2/-3 reading.
- Both have `COVERS=1`, orient LR and RL, 128 leaves, no fails, return time [695.5, 700.8].
- They are edge-only (`chunk_a=[0,0)`); their (a) parts are kerr_a chunks, which have not run.
- §6.3 expects exactly this: self-coverings near the hyperbolic point are allowed and give a periodic point, not entropy.

**Where Kerr must fail.**
- S3 (ρ > 1) is exact integer arithmetic on A, and the chain fixes A. It cannot fail by itself: if every required covering certifies, ρ > 1 follows. So the failure must be in a covering: S2(a) stable band, S2(b) edges or orientation, S1, S4 or S9.
- My expectation, which is reasoning and not registered:
  - **The stable band, S2(a).** Carter's Q is conserved. Across a chain set, Q varies mainly along s, because the sets straddle the separatrix with S⊥ normal to it. So a covering N_i ⇒ N_j needs Q-range(image) = Q-range(N_i) to sit strictly inside N_j's band. Around the cycle N0 → N1 → … → N5 → N0, that strict nesting cannot hold all the way round, so S2(a) fails somewhere.
  - **The return into N0.** In integrable Kerr, W^u = W^s. The image of N5 comes back along N0's stable direction, not across its u-range, so S2(b) fails there: an edge leaf certified not to leave, or an orientation contradiction.
- **Risk.** If the failure is in (a), the twin record suggests it would come out uncertified (cap or depth). That is UNDECIDED, which reads "tool limit on Kerr", NOT support. A month or more of Kerr compute could end there. Only a failure in the edges or orientation gives CERTIFIED-FAIL.

**Could Kerr pass everywhere? Not with a sound pipeline.**
- Q-level curves are invariant, so the return map's topological entropy is 0. The base map on Q-levels is the identity, and each fibre map is a 1-D homeomorphism.
- Certified coverings with ρ(A) > 1 imply entropy ≥ log ρ > 0.
- So "passes everywhere" means the pipeline is unsound or the run is not really Kerr (as with the B15e A1 param-level bug class). That is the §6.3 / F7 STOP, as intended.

## (c) What would it take to get the MN target to a rigorous chain first?

**Where things stand.**
- **Kerr:** B15c ended NOT TESTED (73230b5): no Kerr chain reached a decided covering under the frozen constructor. B15d then fixed sets on the unfrozen arm's chain, which is the kerr_e/kerr_a work.
- **MN:**
  - The MN smoke test failed on 2026-10-21 from wrapping: the p_y lift was ~500× too wide, and the field's interval form over-widens 10–1.7e3× because of the β terms, against Kerr's 1–50×.
  - The so_mn line since then built the E-representation. The B17 return was certified with W_lin at t = 291.885 in the wrapping test.
  - Branch-S retry pieces mm/mp/pm/pp are running now, ≤ 535 core-h, with the verdict from read_retry.sh. Fable's sealed prediction d31ac7f is graded only after that.
  - Melnikov stage 2 is CERTIFIED-NONDEGENERATE (77073c2), first order in β.

**Steps to a rigorous MN chain:**
1. **The branch-S verdict:** a certified MN saddle-orbit return. This is in progress, and it is what the freed cores should serve.
2. **A-K20:** the MN point, E, L_z, section, λ and seeds, as committed. The B11/B12 primary is p2 at (37/40, 3).
3. **The frozen constructor on MN:**
   - step 2, a homoclinic connection with angle ≥ 0.01;
   - steps 3–4, refinement and a ladder entry;
   - then S8.
   - The result is a chain with an accepted ladder entry, which Kerr's B15c never reached.
4. **Rigorous hs_cover on MN**, with the S4, S5 and S9 gates. The binding unknown is whether hs_cover can decide MN coverings at all under MN's interval blow-up. The cheapest early answer is a small covering pilot on MN, the analogue of the kerr_a pilot rule, before any full chain runs.
5. **The second implementation (S6)** on whatever certifies.

**Why the control should follow the target.**
- §6.3 says Kerr runs with "everything else the same as the MN run": the frozen constructor, ladder, budget and settings.
- If the control runs ahead and MN later needs a different precision, depth or binary, the control has to run again anyway.
- So: register the redesign in (a) now if wanted, but run it once MN has a chain whose coverings are actually running, on the same binary and settings.
- N1N2 stays the one running sample meanwhile. Its first side-1 piece, the first chance of an orientation verdict, lands around 12-07.

## The paused Air chunks

The 5 chunks were paused at 00:30:00 Air time by SIGSTOP. air_guard was held by SIGSTOP, so it cannot SIGCONT them. They hold 2, 0, 1, 1 and 0 EP records (N4N5, N2N3, N5N0, N5N1, N3N4).
- Their in-progress pieces are kept in memory while paused.
- The 30 d alarm keeps counting.
- If a chunk is resumed after 2026-12-26 12:59:19, the pending SIGALRM ends it at once (exit 124). It loses only the piece in progress; its EP records stand.
