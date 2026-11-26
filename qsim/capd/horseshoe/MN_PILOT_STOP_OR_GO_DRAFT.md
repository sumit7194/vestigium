# MN covering pilot: STOP-OR-GO test (draft for registration; nothing has run)

Drafted 2026-11-27 by Quantum-personal (Claude Opus 5.5) at the personal Bridge's request, for Sumit.

## In plain language

The horseshoe needs certified "coverings" on MN: the computer must push small boxes of starting points once around the orbit and prove where every one lands. The question is whether that is affordable.

- **What one box costs.** On Kerr one box costs about half an hour. On MN, the only method that has worked so far took about 122 core-hours for a single box of half-width 1e-7 (A3: 42.7 h to t ≈ 292, then 79.5 h to t ≈ 810). That box still failed one of its 5 checks, so the current retry splits it into 4 boxes of half-width 5e-8, each costing about the same.
- **What the budget allows.** The registered budget for the first MN attempt is 4 cores for 14 days, about 1,344 core-hours (§3.6). At ~122 core-hours a box, that is about 11 boxes. One covering needs at least two edges plus an interior, which is already several boxes, and a horseshoe needs several coverings.

**My honest expectation: STOP**, unless the pilot shows the boxes can be far larger or far cheaper than A3's. The pilot below tests exactly that, with the rule fixed in advance. A zero-compute paper check (step 0) may settle it before anything runs.

## The decision rule (fixed before anything runs)

- **Step 0, paper check (no compute; about a day of my time).** Take the frozen constructor's smallest registered h-set size at the MN seed (§3.7: a 16-value grid for the unstable half-width). Count how many 5e-8 boxes the edges and interior of one N0 ⇒ N0 covering need, times ~122 core-h each.
  - If that cost is more than the registered first-attempt budget (1,344 core-h), the result is **STOP**.
  - If Sumit wants to amend that budget, he sets the new figure before step 0 is read.
- **Step 1, the branch-S verdict** (already running). read_retry.sh must PASS on all 4 pieces at all 8 time checkpoints.
  - **FAIL → STOP.** No MN box survives one return with the current engine, so no covering can be certified.
- **Step 2, the pilot** (only if steps 0 and 1 allow it). It is ONE covering, N0 ⇒ N0, at the MN saddle seed from A-K20, with the frozen constructor's set and the registered ladder.
  - **GO** needs both of these:
    - the covering is DECIDED (CERTIFIED or CERTIFIED-FAIL under the B15c-1 classes) within the budget;
    - the cost per box it measures, times the box count of the full chain the constructor gives, projects within a full-chain budget Sumit sets now.
  - **STOP** if any of these happens:
    - any piece fails closed at the top of the ladder (wrapping, S4, S9, cap or depth), so the covering is UNDECIDED;
    - the budget runs out;
    - the projection exceeds the full-chain budget.
- **Time box:** if the pilot is not running by 2026-12-31, the result is STOP.
- **On STOP:** write up what is solid and close the thread, with no further revisions. That is the HH reproduction (HH-PRIMARY 7/7 and HH-SECONDARY 6/6 certified), Melnikov stages 1–2 (CERTIFIED-NONDEGENERATE, first order in β), the MN certificates, the Kerr decidability record and the controls.
- **On GO:** a costed path to a full chain comes back to Sumit before any of it runs.

## Time and core-hours to reach the pilot, and to run it (honest; low confidence where marked)

| Stage | Wall time | Core-hours | Notes |
|---|---|---|---|
| 0. Paper check | ~1 day of my work | 0 | needs the constructor's grid and the MN seed's frame |
| 1. Branch-S verdict | ~4–5 more days, verdict ~12-01 to 12-02 | ~490 in all (~60 spent), within the registered ≤ 535 | pieces at t 251–283 of 805.3 after 15.5 h each; A3's pace was 42.7 h to t ≈ 292, then 79.5 h more |
| A-K20 | done (2026-10-20; S5 at its final parameters PASS) | 0 | |
| 3. Constructor steps on MN | 1–3 weeks (low confidence) | small to tens | homoclinic connection (angle ≥ 0.01), refinement, ladder entry, S8 |
| 4. Covering driver on the E-representation | 1–2 weeks of work, plus review | ~50–100 for tests | hs_cover's plain MN field failed the smoke test on wrapping (2026-10-21); only mn_so's E-representation propagates MN boxes. Covering pieces need that path, with checkpoints and A8-style identity and interrupt tests |
| 5. The pilot itself | 1–5 weeks on ≤ 7 cores (very uncertain) | ~1,200–6,000 if N0 is a few boxes wide; far more if it is HH-sized | ~122 core-h per box-return |

**In total:** about 3–6 weeks to reach the pilot, then 1–5 weeks to run it, so the decision would land around late December to February. Step 0 could give the answer within days and save all of that.

## Step 0 result (2026-11-27; paper check, no compute): STOP

Sumit approved this note as written, with the budget fixed at 1,344 core-h before step 0 was read (the personal Bridge's relay).

**In plain language.** The smallest set the frozen constructor allows is far larger than a box MN can push through one return. Covering even one such set needs at least about 200,000 boxes, even granting every assumption that favours GO. The budget pays for about 11. That is STOP.

**The numbers.**
- **Smallest N0 in the frozen B14 ladder:** a0 = 0.01 (unstable half-width) and b0 = 0.1 · a0 = 0.001 (stable half-width), in section units. The ladder is a0 ∈ (0.03, 0.02, 0.015, 0.01) and b0/a0 ∈ (0.5, 0.25, 0.1). A smaller set would be a constructor change, which re-runs every control, so it is out of scope.
- **Largest MN box that propagates:** half-width 5e-8, the branch-S pieces, whose verdict is not read here.
  - A3's 1e-7 box failed one check (u2 ratio 8.77 > 5).
  - The wrapping test's 1e-6 box failed even with W_lin.
- **Cost per box per return:** at least 122 core-h. That is A3's 1e-7 box: 42.7 h to t ≈ 292, then 79.5 h to t ≈ 810. The return itself is at t ≈ 1018.7, so 122 is a lower bound.
- **Boxes for ONE covering, N0 ⇒ N0:**

| Reading | Edges (2 × 2b0) | Interior (2a0 × 2b0) | Total | Cost |
|---|---|---|---|---|
| As tested: 2-D boxes of half-width 5e-8 | 2 × 2e4 = 4e4 | 2e5 × 2e4 = 4e9 | ≈ 4e9 | ≈ 5e11 core-h |
| Most favourable to GO: boxes may be long along s, only u must be ≤ 1e-7; each edge is 1 box | 2 | 2e5 strips | ≈ 2e5 | ≈ 2.4e7 core-h |
| Budget | | | ≈ 11 boxes | 1,344 core-h |

- **Margin.** Even the most favourable reading is about 18,000× over budget. If the cost per box also fell 100×, to a Kerr-like ~1.2 core-h, it would still be about 180× over.
- **The registered ladder's caps also bind.** Interior subdivision is capped at ≤ 2^16 = 65,536 boxes per covering (§3.6), which is below 2e5 even in the most favourable reading.
- **Rule outcome:** the cost is greater than 1,344 core-h, so the result is **STOP**. As the rule says, the branch-S retry pieces are ended by verified PID, which saves ~430 core-h, and the write-up begins. The sealed Fable retry prediction (d31ac7f) stays sealed and ungraded, because there will be no branch-S verdict to grade it against.

## Technical notes

- The 122 core-h figure is one 1e-7 box on one core: main_redo, wall 153,682 s from t = 0 to 291.88, then main_cont, 286,171 s from 291.9 to 809.8.
- The ladder (§3.6) allows ≤ 2^12 edge pieces per h-set edge and ≤ 2^16 interior boxes per covering, so the ladder itself does not bind. The cost per box does.
- A3's 1e-7 box stretched to u1 ≈ 3.4e-3 by t ≈ 292 (a factor of ~3.4e4). So a very small N0 can still have edge images that cross itself, and the h-set size is the lever that decides the cost. Whether the frozen constructor's grid allows sets that small is what step 0 checks.
- Branch-S outcomes are not read here. read_retry.sh gives the verdict, and the sealed Fable prediction d31ac7f is graded only after that.
- The Kerr control follows the target: the early-stop amendment and the side-alternating order are parked until MN coverings run.
