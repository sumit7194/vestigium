# CAPD pins (chaos-proof engine; approved by the user 2026-10-11: "yes go ahead with CAPD, skip boost")

- Source: https://github.com/CAPDGroup/CAPD/archive/refs/tags/v6.0.0.tar.gz (CAPD-6.0.0.tar.gz, 1 127 693 bytes)
- sha256: 0ae254cb6477896c3c3f2b8cd1c4a6cb073fb1e1e08f71d0e0bd2587d60c9620 (computed on download; no checksum is
  published)
- Tag v6.0.0 → commit 693998cd6d73a0c4e1b141bfb79fcad1c40c3cbe. Licence GPL-3.0.
- Location: ~/opt/CAPD-6.0.0 (source), ~/opt/CAPD-6.0.0/build, install prefix ~/opt/capd-6.0.0-install. User-local, no
  sudo.
- Tools: cmake 4.4.4 and pkgconf 3.0.7 (brew), Apple clang 21, gmp/mpfr (brew), **boost 1.92.0** (brew bottle
  arm64_tahoe; 358.5 MB in the Cellar, 16 678 files). Added on 2026-10-11 by the user ("yes add boost, rigour first"),
  so that CAPD's own Boost.Test suite runs (-DCAPD_BUILD_TESTS=ON).
- Rigour plan on Apple silicon: native arm64, multiprecision (MPFR) intervals ONLY. The filib/double path is not
  used (CAPD's docs: filib needs Rosetta on Apple silicon; clang rounding untested by the authors). Validation is by
  CAPD's FULL test suite (any failure reported verbatim, none skipped), then our own MPFR rounding sanity tests, the
  published Hénon–Heiles positive control, and the Kerr negative control.

## Patch (2026-10-11): `capd-6.0.0-arm64-nofilib.patch`, applied to the pinned tarball by `build_capd.sh`

**Why.** CAPD v6.0.0's build makes filib mandatory, and `capdExt/filibsrc/CMakeLists.txt` accepts only x86_64
("Unknown or unsupported processor architecture" on arm64). CAPD's own library code already supports Apple arm64:
`archSetting.h` detects `__arm64__ && __APPLE__`, and `DoubleRounding.cpp` has a `CAPD_CPU_ARCH_ARM64` path that sets
rounding through FPCR.

**What.** filib and `-D__USE_FILIB__` are made conditional on x86_64 (top-level CMakeLists, capdExt), and the two
config scripts tolerate a missing filib target. Four build files change; no library source changes.

**Trust rules (bridge).**
1. MPFR multiprecision intervals ONLY in anything proof-bearing. No double intervals, with a compile-time guard in
   our code.
2. CAPD's full ctest, with every result reported. Any failure in interval, MPFR, rounding or ODE-enclosure tests
   disqualifies the build.
3. A differential check of ≥ 10⁵ random MPFR-interval operations against our Arb core. A single non-containment
   disqualifies.
4. ODE controls: an exact analytic solution enclosed; the Hénon–Heiles positive control; Kerr must not certify chaos.
