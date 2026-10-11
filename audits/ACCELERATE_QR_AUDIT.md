# Audit: Apple Accelerate dgeqrf heap overrun (fleet alert, tabula 59812ec), 2026-10-11

**Exposure:** `sims/.venv` numpy and scipy both link **Accelerate** (`numpy.show_config()`: blas = lapack = accelerate).

## Every call that can reach QR-family LAPACK in `qsim/` and `tools/`

| call site | shape | relevance |
|---|---|---|
| `chl_series.py:188` and `chl_mp.py:153`, the CHL node Newton `np.linalg.lstsq` | **complex** J of 11N × (11N+5) (unknowns 11(N+1)−6, equations 11N). N=26 (Stage 2, V1): 286×291. N=40: 440×445. **N=54 (set B): 594×599, which lies in the reported band.** N=72 (set C): 792×797 | sub-45 check: Stage 2, D-tests, Stage 3a, Plan A V2/V3, V1 |
| `stage3_entanglement_at_scale.py`, `stage3_symmetric.py`, `np.linalg.svd` | square, 2^(N/2) ≤ 1024 | old exploratory scripts, not verdict-relevant now |
| polyfit / lstsq fits (corner_*, k0_scaling, kappa_vs_mutual_info, log_coefficient_boundary, zeno, lrl_secular, chl_corner) and matrix_rank (hexagon) | a few to a few dozen rows | far below the band |

The certificates (Rust/Arb v2, python-flint/Arb v1, exact 2b′, Lean, CAPD/MPFR) call no LAPACK.

## Direct test under Guard Malloc

Method: `DYLD_INSERT_LIBRARIES=/usr/lib/libgmalloc.dylib`, run with `audits/accelerate_gm_lstsq.py` and
`audits/accelerate_gm_svd.py`.

- **Positive control:** the bridge's repro `np.linalg.qr(standard_normal((629, 629)), mode='r')` **crashes**
  (rc 139, SIGSEGV). So Guard Malloc does detect the overrun on this machine. 400×400 is clean.
- **The solver's own shapes:** 11N × (11N+5), complex AND real `lstsq`, for **every N from 20 to 80**, which covers
  all values the code uses (26, 40, 54, 72). Each was run 3 times. **0 crashes.**
- **The SVDs:** 256², 512², 512×1024, 1024² and 256×512, real and complex. **All clean.**

## Verdict

- **CLEAN.** No call in this repo reaches the faulty path at the shapes it uses.
  - The lstsq calls are underdetermined (m < n), which LAPACK's gelsd handles without dgeqrf preprocessing.
  - Their actual shapes, including set B's in-band 594×599, run clean under Guard Malloc. The positive control
    crashes in the same setup.
- Nothing is flagged "Accelerate-exposed". No reruns are needed.
- **Caveat:**
  - The test used random matrices of the exact shapes and dtypes. LAPACK's code path depends on shape, dtype and
    flags, not on the values.
  - Guard Malloc only catches overruns of blocks that the system allocator owns. The positive control shows that
    covers this bug.

Environment: Python 3.13.12, numpy 2.5.0, scipy 1.18.0 (Accelerate), macOS 26.5 arm64.
