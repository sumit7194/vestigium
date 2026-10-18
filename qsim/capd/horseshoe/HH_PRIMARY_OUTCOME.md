# HH-PRIMARY outcome: Hénon–Heiles at E = 1/6, Arioli–Zgliczyński 2001 Lemma 5 (5.1), 2026-10-18

**Registration:** `PREREG_chaos_horseshoe_phase2.md` §6.2 (B7) and §6.4. The amendments relevant here are:
- B8: Def. 2(a) form, S8 and S9;
- the ordering disclosure (5d77bee);
- B13 and its addendum: the reboot re-run, depth-cap fix, checkpoints, chunking, and the post-hoc budget change.

**Inputs:**
- AZ 2001 §4.2 t-sets M0–M4, as exact decimals;
- H = (p_x² + p_y²)/2 + (x² + y²)/2 + x²y − y³/3, at h = 1/6;
- Θ₁ = {x = 0, ẋ > 0}, coordinates (y, p_y), with p_x = +√(1/3 − p_y² − y² + 2y³/3);
- P₁ = the first return.

**Engine:** CAPD 2f06098, MPFR 128 bits, Taylor order 20, MpC0TripletonSet, under `proof_guard.h`.
- The S9 in-flow check is run on every step: H ∋ 1/6 on every step enclosure, and p_x > 0 at each return.

## Result

**On the registered first pass (`hh1_*`, 16×16 boxes, 64 pieces per edge, sealed bd7060a):**
- (b) holds for 7 of 7 coverings;
- (a) is NOT certified on any of them at that coarse subdivision;
- W-AZ1 and W-AZ2 are rejected by certified failures.

**After the escalation within the §3.6 caps (disclosed as post hoc): ALL SEVEN coverings of (5.1) are certified.**
The escalation was:
- adaptive bisection (`hh1a`, 921ee47), chosen after seeing partial first-pass results;
- for M1⟹M2 and M3⟹M4, the B13 re-run (`hh1b` / `hh1b2`, 816fdfb + 691d5d8) after a reboot killed their hh1a runs.

| Covering | Run | (a) leaves | Max depth | (a) failures | (b) | Return time P₁ |
|---|---|---|---|---|---|---|
| M0⟹M0 | hh1a | 305 | 4 | 0 | 1 (LR), 128 edge pieces | [6.8484, 7.5045] |
| M0⟹M1 | hh1a | 1010 | 5 | 0 | 1 (LR), 128 edge pieces | [6.8484, 7.5045] |
| M1⟹M2 | hh1b (B13) | 11866 | 9 | 0 | 1 (RL), 128 edge pieces | [7.2435, 9.4090] |
| M2⟹M3 | hh1a | 899 | 5 | 0 | 1 (LR), 128 edge pieces | [6.1436, 7.9296] |
| M3⟹M4 | hh1b (B13) | 20166 | 11 | 0 | 1 (RL), 128 edge pieces | [7.4992, 8.1878] |
| M4⟹M0 | hh1a | 285 | 2 | 0 | 1 (LR), 128 edge pieces | [6.6224, 7.5814] |
| M4⟹M1 | hh1a | 318 | 2 | 0 | 1 (LR), 128 edge pieces | [6.6224, 7.5814] |

**Further checks, all holding:**
- **S8:** the supports of M0–M4 are pairwise disjoint (exact separating axes, `hh1_exact_checks.json`).
- **S9:** every enclosure contained H = 1/6, and p_x > 0 at every return. No exceptions.
- **Return times** lie in [6.14, 9.41], consistent with AZ's reported 6–10.
- **Caps:** no box reached the depth cap (the maximum was 11, against 16), and no covering came near its leaf cap
  (20 166 of 65 536 at most).
- **Determinism:** chunk c1c, re-run after the 2026-10-18 restart, reproduced its pre-restart result exactly.
- **The stronger form** |s| < 1 of (a) does NOT hold for any covering (strong_a = 0). This is recorded as data. It is
  not required by Def. 2(a).

**The entropy consequence.** The transition matrix on (M0…M4) is AZ's A, with characteristic polynomial x(x⁴ − x³ − 1).
ρ(A) = λ_max = 1.380277569…, so with AZ Theorem 2 and Lemma 6 (applied as in T0_HYPOTHESES.md),
**h_top(P₁ | Inv) ≥ ln λ_max = 0.3222846…** AZ's Corollary 6 prints ">1.38027", which is λ, not ln λ (see B7).

**Wording (B7):** "an independent implementation (CAPD/MPFR) **reproduces the covering relations (5.1) of
Arioli–Zgliczyński 2001, Lemma 5**, on their published t-sets, with condition (a) certified on the whole support."
To be stated alongside it:
- the subdivision scheme that certified (a) was chosen after the registered first pass;
- see the budget below.

It is NOT "reproduces their proof": (5.2)–(5.4) and their Lemma 3 are not re-done.

## The budget: both readings, as registered in B13

- **Original registered HH budget (48 core-hours):** about 87 core-hours were spent in total. That is 45.1 recorded
  in the result JSONs, about 26 lost to the 2026-10-17 reboot, and about 16 in the stopped c1 chunk, whose 52 pieces
  were reused. **Under the original budget, M1⟹M2 and M3⟹M4 are "not certified within budget", so HH-PRIMARY is
  PARTIAL, 5/7,** and none of the reproduction wording applies.
- **Under B13 (post hoc, on the user's instructions; the leaf and depth caps unchanged):** 7/7, and the reproduction
  wording above applies.

## Corrections to my own earlier statements

- **The depth cap.** B13 speculated that a persistently failing box "likely explains" the 13 h runtimes of M1⟹M2 and
  M3⟹M4. **That was wrong.** No box ever reached the depth cap (maximum 11), and no (a)-piece failed. The two coverings
  were simply expensive: about 23 and about 32 CPU-hours respectively. The depth-cap fix is still correct, since it
  enforces the registered caps, but it changed nothing here.

## Still open

- **HH-SECONDARY** (my own h-sets, through the frozen constructor): not started. The constructor is not yet written.
- **The Bridge's S6 replay (V14 Q2)** runs on these results blind. It receives only the commit hash and sha256s until
  its decisions are committed.
