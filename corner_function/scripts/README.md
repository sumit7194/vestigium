# scripts/

Everything executable in this workspace. Nothing here is required to read the result:
`RESULT.md` is self-contained and `report.md` is the notebook. These are the checks.

## The one that matters for the theorem

- `exp003_spectral.py` → `exp003_output.txt` (frozen output). Evaluates constraints C1–C6 of
  `RESULT.md` §2 on the explicit admissible family at 40 angles for κ/C_T up to 10⁶, and tests
  moment positivity of the published coefficient sequences. **Includes a control that must fail**
  (a deliberately corrupted sequence), so the test is not vacuous. The theorem itself is analytic;
  this is a check, not a step in the proof.

## Measurement of the band (EXP-001)

- `exp001_measure.py` — holographic corner curve from the Hirata–Takayanagi integrals, the
  Bueno–Witczak-Krempa lower bound, free-field tables, and the `../quantum` comparison.
  Controls: σ/C_T → π²/24 and κ/C_T → π²Γ(3/4)⁴/6.
- `exp001_coefficients.py`, `exp001_ecg.py` (Einsteinian cubic gravity curve, trial-function slope),
  `exp001_output.txt`.

## Parked instrument (EXP-004) — do not resume without reading TODO.md

Solver for the Casini–Huerta–Leitao ODE system, validated to 7 digits on four exact smooth-limit
coefficients and on published Rényi-2 values, then extended past the double-precision floor at M ≈ 4.

- `exp004_ch_solver.py` (double precision), `exp004_mp.py` (mpmath, 25+3M digits, N-continuation),
  `exp004_prod.py` (parallel driver), `exp004_run.py`, `exp004_controls.py`, `exp004_mdecay.py`,
  `exp004_analyze.py`.
- Data kept on purpose: `exp004_renyi2_result_n24_24_p15.0_t1.json` (result to M = 15) and
  `exp004_nodes/` (145 checkpoint nodes). The `.log` / `.err` files are kept as failed-run controls —
  a failed run you keep is a control for the fix; a failed run you discard is a rumour.
- Needs `mpmath`. The `.venv/` here is git-ignored and regenerable:
  `python3 -m venv --system-site-packages .venv && .venv/bin/pip install mpmath`

## Source texts (`tools/`)

The papers cited in `references.md` are not stored in this repo. `tools/fetch_sources.sh`
re-downloads the eight that were read in full and converts them with `tools/h2t.py`, which is the
same converter that produced the ar5iv line numbers quoted in `RESULT.md` §9. `tools/ctx.py` greps a
converted text with context lines.
