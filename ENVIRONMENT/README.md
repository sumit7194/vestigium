# Environment and how to reproduce (fleet policy, 2026-10-11)

This repository's code serves as part of mathematical proofs, so someone else has to be able to re-run it. This
folder pins the environment every result ran in.

- **`quantum_env.json`:** the full stamp from `tools/envstamp.py`. It records the interpreter, platform and macOS
  build, Python packages, the BLAS/LAPACK backend and the git commit, plus the native stack: rustc/cargo, the iahub
  Cargo.lock hash, the FLINT versions, Homebrew MPFR/GMP/boost/cmake, the Lean toolchain and Mathlib commit, and the
  CAPD pin. Regenerate it with `sims/.venv/bin/python tools/envstamp.py ENVIRONMENT/quantum_env.json`.
- **`quantum_requirements.lock`:** `uv pip freeze` of the one interpreter used for all runs (`sims/.venv`).

**As stamped (2026-10-11):**
- Machine and OS: Apple arm64, macOS 26.5 (25F71).
- Python: CPython 3.13.12 (Homebrew), with numpy 2.5.0, scipy 1.18.0 (both on Apple Accelerate BLAS/LAPACK), sympy
  1.14.0, mpmath 1.3.0, python-flint 0.9.0 (bundled FLINT 3.6.0).
- Rust: rustc 1.98.1.
- Homebrew: FLINT 3.6.0, MPFR 4.2.2, GMP 6.3.0.
- Lean: v4.35.0-rc3, Mathlib c55e6e78.
- CAPD: master commit 2f06098 (see `qsim/capd/PINS.md`).
- Compiler: Apple clang 21.

## Which stack each independent implementation uses (for paper claims)

| implementation | code | arithmetic | used for |
|---|---|---|---|
| **v1** (`qsim/ia_hub.py`) | Python | python-flint 0.9.0 → **FLINT/Arb 3.6.0 (wheel build)** | reduced-form SL(2) replays; MN axial A5 certificates |
| **v2** (`native/iahub`, Rust + C shim) | Rust 1.98.1 | **FLINT/Arb 3.6.0 (Homebrew build)**, MPFR 4.2.2, GMP 6.3.0 | non-reduced GL(2) certificates |
| **2b′** (`qsim/mr_factor_route.py`) | Python and sympy (exact) | exact rational arithmetic | TS Kovacic route |
| **Lean** (`lean/ZiglinCert`) | Lean 4 v4.35.0-rc3 + Mathlib c55e6e78 | kernel exact ℚ | glue theorems; kernel-checked certificate arithmetic |
| **CAPD** (planned chaos proof) | C++ (CAPD 2f06098) | MPFR 4.2.2 intervals ONLY | covering relations (future) |

**Honest caveat:** v1 and v2 are independent in code, equation form (reduced against non-reduced) and certificate
type (SL(2) against GL(2), different word composition). But **both use the same FLINT/Arb version (3.6.0)**, in
separate builds. A bug in Arb 3.6.0 itself would not be caught by the v1/v2 cross-check. It would be caught by the
Lean kernel re-check of the certificate inequalities (exact ℚ, independent of Arb) **for the arithmetic step only**:
the ODE enclosures still rest on Arb.

## How to reproduce

```bash
# 0. system tools (Homebrew): python@3.13, rust, flint, mpfr, gmp, cmake, pkgconf, boost; elan (Lean)
# 1. Python environment
uv venv --python 3.13 sims/.venv && uv pip install --python sims/.venv/bin/python -r ENVIRONMENT/quantum_requirements.lock
# 2. Rust engine (v2): links /opt/homebrew FLINT/MPFR/GMP (see native/iahub/build.rs)
(cd native/iahub && cargo build --release)
# 3. Lean: glue theorems + every kernel-checked certificate
(cd lean/ZiglinCert && lake exe cache get && lake build && lake build ZiglinCert.Certs.All && lake env lean Axioms.lean)
# 4. Results (each a guarded runner; outputs land beside it in qsim/)
sims/.venv/bin/python qsim/mr_mn_axis.py          # MN axial (A5 certificates)
sims/.venv/bin/python qsim/mr_v2_mneq.py          # MN equatorial v2 (rows; A6/A7 per PREREG_mn_equatorial_v2.md)
sims/.venv/bin/python qsim/mr_v2_ts2.py RUN       # TS δ=2 v2 re-cert
sims/.venv/bin/python qsim/mr_ts2_chaos.py RUN    # TS bound-orbit levels (2b' + v2/v1)
sims/.venv/bin/python qsim/lean_export_all.py     # regenerate certificate boxes (bit-for-bit gate)
sims/.venv/bin/python qsim/lean_check_all.py      # Lean-check every exported certificate
# 5. CAPD (planned chaos-proof engine): pinned tarball -> build -> full ctest
qsim/capd/build_capd.sh
```

**Notes.**
- Exact bit-for-bit reproduction of v1/v2 balls depends on process state. For example, the TS chaos-levels run used
  mpmath dps = 60 left over from its gates (see `PREREG_lean_certificate_arithmetic.md`, Disclosure).
  `qsim/lean_export.py` reproduces those states.
- On a different OS or library version, expect the same verdicts and enclosures containing the same values. Ball
  radii may differ in their last digits.

## Policy

- Every RESULTS/FINDINGS/OUTCOME entry carries an `Environment:` line.
- Entries made before 2026-10-11 are back-filled with the stamp above and marked "back-filled; env assumed
  unchanged since the run".
- Any change since a run is stated where it is known.
