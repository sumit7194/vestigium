# R1 outcome: Rössler a = 5.7, b = 0.2 (pipeline control), 2026-10-16. **PASS**

## Run identity

| Item | Value |
|---|---|
| Registration | `PREREG_chaos_horseshoe_phase2.md` §6.1, §6.4 (with B8). Every rule was committed before this run. |
| Code | `qsim/capd/horseshoe/hs_cover.cpp`, built from commit ffd94bf (binary sha256 prefix a4581d0153de0ec1); runner `hs_run.py` at 017fb8c |
| Arithmetic | MPFR 128 bits, built under `proof_guard.h` (the guard passed) |
| Integrator | Taylor order 20; MpC0TripletonSet |
| Run settings | 4 cores, nice 19 |
| Results | `qsim/capd/horseshoe_results/r1_*.json`, each with its spec and the spec's sha256 |

## (1) Exact port of CAPD's `RosslerChaoticDynamics.cpp`

Same sets, section x = 0 MinusPlus, P², order and subdivisions as the published example; MPFR instead of double.

| Check | Result | Image / note | Time |
|---|---|---|---|
| Trapping, P(W) ⊂ int W, with W = [−10.7, −2.3] × [0.028, 0.034] in 200 pieces | **true** | | 325 s |
| P²(left M) < −8.4 | **true** | y ∈ [−8.5122, −8.4824] | 9.7 s for all four edges |
| P²(right M) > −4.6 | **true** | y ∈ [−4.3928, −4.3735] | |
| P²(left N) > −4.6 | **true** | y ∈ [−4.5417, −4.5391] | |
| P²(right N) < −8.4 | **true** | y ∈ [−8.6517, −8.6510] | |
| Cone condition on M (80 boxes, Q = diag(1, −100)) | **true** | recorded; does not gate | 604 s |
| Cone condition on N (40 boxes) | **true** | recorded; does not gate | 288 s |

Together these give M⟹M, M⟹N, N⟹M and N⟹N.

**Timing difference.** The paper reports under 2 s, in double precision with Hermite–Obreshkov sets. Here MPFR is
used throughout, and CAPD 2f06098's Hermite–Obreshkov sets do not compile with MPFR scalars, so the plain Lohner
tripleton is used. Timing is not a criterion.

## (2) The same sets through the generic AZ Def. 2 code

Frames are given, not constructed. Condition (a) is checked on the whole support (64 × 1 pieces), and (b) on the edges.

| Covering | (a) | (b) | Orientation | Strong form \|s\| < 1 (data) | Return time |
|---|---|---|---|---|---|
| M ⟹ M | ✓ | ✓ | LR | ✓ | [11.327, 11.774] |
| M ⟹ N | ✓ | ✓ | LR | ✓ | [11.327, 11.774] |
| N ⟹ M | ✓ | ✓ | RL | ✓ | [11.571, 12.219] |
| N ⟹ N | ✓ | ✓ | RL | ✓ | [11.571, 12.219] |

**All 4 coverings are certified, matching the example's decisions.** The orientations match too: N's edges flip,
exactly as in the example's inequalities.

## (3) Wrong configurations (§6.4): all REJECTED, each by a CERTIFIED failure, not by budget exhaustion

| Configuration | Coverings that fail (the modified M is M′) | Certified failure |
|---|---|---|
| W1: u and s swapped on M | M′⟹M′, M′⟹N, N⟹M′ | **N⟹M′ (b):** both edge images have u certified in (−1, 1), e.g. [0.194, 0.205], so they lie in neither side. The M′-source pieces also hit CAPD's "possible nontransversal return": the slabs are full-width in y. |
| W2: frame rotated 90° | M′⟹M′, N⟹M′ | **(b):** the edge images have u certified in (−1, 1), e.g. [0.0018, 0.0023] |
| W3: unstable half-width × 1e−3 | M′⟹M′, M′⟹N | **(b):** both edge images are certified inside the SAME side, so neither orientation is possible |

Notes on what does pass:
- **N⟹N passes in W1–W3**, and N⟹M′ passes in W3. N is unchanged there, and for W3 the shrunk M′ still lies across
  the image strip.
- **W2's rotated M′ certifies M′⟹N.** M′ is a tall, thin set (z ∈ 0.031 ± 0.4 at y = −8 ± 0.003), and P² stretches
  it across N in y. That is a valid covering relation for that set. It is not a false positive: Def. 2 is a
  topological condition, satisfied here with certified margins. The configuration is still rejected, because
  M′⟹M′ and N⟹M′ certifiably fail.

## Verdict

**R1 PASS.**
- The example's decisions are reproduced on MPFR.
- My generic Def. 2 code agrees on all four coverings.
- Every wrong configuration is rejected by a certified failing check.

The pipeline gate for R2 (Hénon–Heiles) is open.
