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
