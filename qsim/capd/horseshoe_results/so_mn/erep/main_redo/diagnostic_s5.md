# main_redo: section-5 diagnostic (descriptive, NOT a criterion)

Written by Claude Opus 5.5, 2026-11-21, after the registered reading (PASS, 7d56c34), at the Bridge's request.

- **What is compared.** The run's u2 error width against the float scorer's Z1sym estimate, at each checkpoint. The
  scorer files are `../../wrap_test/escore_A.txt` and `escore_CA.txt`.
- **How the run's error width is obtained.** The run prints only the total projection width W2 (its PROJ line). The
  polynomial part P is taken from the scorer as P = (printed B17 u2 ratio) × tu2 − Z1sym. The ratio is printed to 3
  decimals, which gives P an uncertainty of ±0.0005·tu2. The run's error width is then W2 − P.
- **Agreement check.** Chains A and CA give the same P to within that rounding, at both checkpoints.

| t | chain | run W2 | P | run error width | Z1sym (float) | ratio |
|---|---|---|---|---|---|---|
| 290.8497 | A  | 6.23723e-7 | 6.1619e-7 | 7.54e-9 ± 3.1e-10 | 4.712e-8 | 0.160 (0.153–0.166) |
| 290.8497 | CA | 6.23723e-7 | 6.1569e-7 | 8.03e-9 ± 3.1e-10 | 8.339e-9 | 0.963 (0.926–1.000) |
| 291.8852 | A  | 2.10763e-7 | 1.9763e-7 | 1.314e-8 ± 1.0e-10 | 7.484e-8 | 0.176 (0.174–0.177) |
| 291.8852 | CA | 2.10763e-7 | 1.9761e-7 | 1.315e-8 ± 1.0e-10 | 1.380e-8 | 0.953 (0.946–0.960) |

**Reading.**
- All ratios are well below the investigation threshold of 10.
- The run matches the CA-chain estimate to about 5%. The CA chain's window starts at step 1306, with REDO on from
  287.756; it is the chain closest to this run.
- The run is about 6× tighter than the A-chain estimate. The A chain starts at step 1712, from the wrapped box E. That
  is the effect E_REP_PREREG §3 predicted ("any mid-run start inherits the wrapped box").
