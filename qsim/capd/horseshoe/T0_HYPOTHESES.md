# T0: hypotheses of the covering-relation theorem, mapped to certified checks

*Quantum, 2026-10-16. This is gate T0 of `PREREG_chaos_horseshoe_phase2.md` §5. It was written before any control or
target run. Its consequences for the registration are amendment B8, committed in the same commit as this file.*

## Sources (all full text, read by me)

- **Arioli & Zgliczyński 2001** (JDE 171, 173–202), from the user's PDF. I use §4.1:
  - Definitions 1–6 (t-set, f-covering, Inv, transition matrix, admissible sequence, projection π);
  - Lemma 4 (the boundary reduction; not used);
  - Theorems 1 and 2;
  - Lemma 6 (the entropy bound).
- **The theorems' origin.** AZ state that Theorem 1 follows from Theorem 4 of [Z3], and that Theorem 2 extends
  Theorems 5–6 of [Z3] from 2 sets to n sets with "exactly the same" proof. [Z3] is Zgliczyński 1997, Nonlinearity
  10, 243 (verified on Crossref by the Bridge sweep). I have not read [Z3]'s full text; T0 relies on AZ's restatement,
  which is fully stated and self-contained.
- **Kapela–Mrozek–Wilczak–Zgliczyński 2021** (CAPD::DynSys, arXiv:2010.07097), from the arXiv PDF. §4.3 (Theorem 5)
  is the Rössler result: the four edge inequalities (11), plus the trapping region W = Y × Z of their Theorem 2, give
  covering relations by "the method of covering relations [14]", where [14] is again Zgliczyński 1997.
- **Gidea–Zgliczyński 2004** (the multidimensional h-sets) is NOT needed. Every target here has a 2-D section with one
  expanding and one contracting direction (Rössler P²; HH, Kerr and MN at 2 degrees of freedom on an energy level). For
  that case AZ's planar t-set theory is the exact statement.

## The theorem as used

For t-sets N_1,…,N_k ⊂ ℝ², a map f continuous on each |N_i| and injective on N = ∪|N_i|, and the transition matrix
T(j,i) = 1 iff N_i ⟹_f N_j:
1. **(Theorem 1)** Every finite chain of coverings has a point following it through the interiors. Every closed
   chain has a periodic point.
2. **(Def. 6 and Theorem 2)** If the supports are pairwise disjoint, then π: Inv(N, f) → Σ_T is defined, onto, and
   satisfies σ∘π = π∘f.
   - **Continuity of π (my step, not quoted from AZ):** π is continuous, because each coordinate of π is locally
     constant, since the supports are disjoint compacta.
3. **(Lemma 6)** h_top ≥ ln λ_max(T).
   - **How I apply it:** to the compact set Inv(N, f), because Inv is closed in N and f is continuous on N.
   - **Why it holds there:** f|Inv has the SFT (Σ_T, σ) as a topological factor, and h(σ_T) = ln ρ(T).
   - **Hence the claim is worded** as h_top(f|Inv(N, f)) ≥ ln ρ(T). That is the precise form, and it is implied by
     AZ's "h_t(f)".

## Hypothesis → certified check

| # | Hypothesis (AZ wording) | Our check | Where |
|---|---|---|---|
| H1 | N is a t-set (Def. 1): \|N\| a parallelogram, Nˡ and Nʳ disjoint half-planes, edges Nˡ∩\|N\| and Nʳ∩\|N\| non-adjacent edges. Remark 2 allows homeomorphic triples, such as M3. | By construction. The exact rational frames are checked symbolically (exact arithmetic) before any run. | constructor; AZ sets as printed |
| H2 | f is continuous on \|N_i\| | S1. CAPD's `PoincareMap` (2f06098, `PoincareMap_templateMembers.h`) calls `checkTransversability` on every step. It throws "possible nontransversal return" whenever the step's rough enclosure meets the section while ∇s·F contains 0. So every contact with x=0 before and at the counted return is certified transversal, and the counted crossing is the first one in the registered direction (MinusPlus: the sign is tracked from < 0). That is AZ's well-definedness condition (2.1)–(2.2). With all contacts transversal, the return time is a continuous function (implicit function theorem), and so is 𝒫. Any thrown exception means that sub-box FAILS; it is never skipped. | S1, driver |
| H3 | f is injective on N (needed for Inv, Def. 3, and for Lemma 4) | A flow map is injective wherever solutions are unique. Uniqueness holds where the field is locally Lipschitz, which is certified because the field is analytic on every enclosure: it is a finite composition of +, ×, ÷ by certified-nonzero intervals, √ of certified-positive radicands, and exp. This is guaranteed for every enclosure by S4(e) and CAPD's own division and sqrt guards (which throw on 0 or negative). For n > 1, 𝒫ⁿ is a composition of injective maps. | S1/S4 |
| H4 | Def. 2(a): f(\|N_1\|) ⊂ int(N₂ˡ ∪ \|N₂\| ∪ N₂ʳ) | **S2(a), relaxed to exactly this form (B8):** each image-enclosure box B of a piece of \|N_i\| is certified disjoint from the closed set F_j = ℝ² ∖ (N_jˡ ∪ \|N_j\| ∪ N_jʳ). For standard sets this is \|u_j\| ≤ 1 ∧ \|s_j\| ≥ 1. For a compact B, B ∩ F_j = ∅ is equivalent to B ⊂ int(ℝ² ∖ F_j). It is certified on the WHOLE support by subdivision, not via Lemma 4. The stronger form \|s_j\| < 1 is recorded as data. | S2(a) |
| H5 | Def. 2(b): the edge images lie in int(N₂ˡ) and int(N₂ʳ), in either order | S2(b), unchanged: each edge-piece image box is certified inside the open side; the orientation is fixed per covering by the first piece, and every other piece must agree | S2(b) |
| H6 | Def. 6: \|N_i\| ∩ \|N_j\| = ∅ for i ≠ j | **S8 (exact form fixed by B8):** pairwise disjoint SUPPORTS only, certified in exact rational arithmetic (a separating line between two convex parallelograms, or exact polygon intersection for M3). Disjoint images are NOT required by Theorem 2. | S8 |
| H7 | ρ(T) > 1 (for positive entropy) | S3, exact | S3 |
| H8 | f maps into the plane of the section, i.e. the section is a smooth 2-D chart | The section coordinates are (y, p_y) or (x, p_x), with the 4th coordinate lifted by the certified positive root (S9). The energy level is invariant, so the lift is consistent. S9 checks that H(enclosure) contains the level on every step enclosure (a bug detector) and the sign at the return. | S9 |
| H9 | Physical meaning (not a theorem hypothesis): the orbits are geodesics of the valid spacetime region | S4 (MN, Kerr) | S4 |

## Implementation consequence (registered by B8)

The in-flow checks of S4 and S9 need every step enclosure, and `PoincareMap::operator()` does not expose them.
1. **Return time.** After `PoincareMap` returns 𝒫ⁿ(B), with an enclosure [T_lo, T_hi] of the return time, the same
   initial set is re-integrated with `TimeMap` (`stopAfterStep(true)`) to time T_hi. On every step, the enclosure
   `getLastEnclosure()` is checked: the S4 domain conditions and H ∋ level.
2. **Coverage.** T_hi bounds every point's return time, so the union of these enclosures covers every orbit segment
   up to its return. The slight overshoot past the return is checked too, which is conservative.
3. **Branch check at the return.** It is done on the returned enclosure: ẋ or ẏ is certified of the registered sign,
   which CAPD's MinusPlus logic already requires.
4. **Coverage gap.** A sub-box whose `TimeMap` replay throws, or fails a check, FAILS. A sub-box is never passed on
   the `PoincareMap` result alone.

## Open item

- **[Z3]'s own text is unread.** Nothing here depends on it beyond AZ's restatement.
- **Contingency:** if a referee asks, read [Z3] Theorems 4–6 before the paper, and record it.
