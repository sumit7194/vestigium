# Wrapping test: result (read against WRAPPING_TEST.md §4, fixed before any run)

Run 2026-11-17 23:59 → 2026-11-18 10:25 (runner log: run.log). Read 2026-11-18.

## Controls: all pass
- K00 and K01 (hook off/on) are byte-identical to so_mn/kr_ref.
- All 21 segments are IDENTICAL (runs/*/CHECK.txt): the grid saves are byte-identical; DIAG, PROJ and CHECKPOINT lines match the original fix-test logs.
- The chains join exactly: wrap_adjoint.py refuses a chain otherwise, and it wrote A, B and CA.
- F ≥ 1 for every covector at every checkpoint: the smallest is 6.43 (A, u2 at 290.85).
- D1c is effectively a point: its largest relative width is 3.7e-27 (CA), so using mid(D1c) loses nothing measurable.

## Primary reading (chain A, u2, t 291.8852): **WRAPPING**
- F = W_box / W_lin = 2.2903e-06 / 9.7643e-08 = **23.46**, which is ≥ 10.
- B17 with P + W_lin **PASSES**:
  - u1 ratio 1.000;
  - u2 ratio 1.504 ≤ 5;
  - fake 7.22e-07 against 4.758e-06 (ratio 0.759).
- With the run's own box, the same checkpoint FAILS, as in the fix test: u2 12.67; fake 3.71e-05, ratio 39.0.

Per §4, the next step is a better E representation (a doubleton/tripleton, shrink-wrapping or a pinned thin column), designed and registered with the Bridge **before** any subdivision. This licenses designing one. It is not a claim: a real implementation lands between W_box and W_lin (§4 caveats).

## Secondary (informational, no verdict)
- **Chain C+A, the long window from 287.77:**
  - At 291.8852: u2 F = 59.6, and B17 with W_lin passes (u2 1.202; fake ratio 0.599).
  - At 290.8497: u2 F = 32.2.
  - So chain A's start parallelepiped already carried wrapping from before t 290. As expected, chain A's F is a lower estimate.
- **Chain A at 290.8497:** u2 F = 6.43. Both the box and W_lin pass there.
- **Chain B (W0 1e-6) at 290.8497:**
  - u2 F = 7.43.
  - B17 FAILS even with W_lin: u2 13.99, fake ratio 10.2.
  - At W0 1e-6, a wrapping-free representation alone would not save this checkpoint, so W0 1e-7 (or subdivision there) is still needed.
- **Where W_lin's u2 injections come from:**
  - At 291.8852, DDE (2.50e-08) dominates P2 (9.51e-09); P0 and P1 are ~1e-32.
  - The injections peak in the 291.25–291.75 bins.
  - DDE is computed from the run's own (wrapped) e, so W_lin is slightly pessimistic (§4 caveat). With a better E, that term would shrink as well.
- **Which columns carry the u2 leak at 291.8852:** box column 1 holds 77.5% and column 0 22.5%. This is two columns; a pinned-column or doubleton design should target both.

## Files
- The analyses: result_A.txt, result_B.txt, result_CA.txt.
- Per-segment checks and logs: runs/*/CHECK.txt and out; grid saves: st*.
- The dumps (16 MB, MPFR hex) stay local and gitignored; their sha256 hashes are in dump_sha256.txt.
