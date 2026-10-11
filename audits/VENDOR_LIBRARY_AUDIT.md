# Audit: a vendor numerical-library defect under responsible disclosure, 2026-10-11

A fleet alert reported a defect in a vendor numerical library. It is under responsible disclosure, so its details
are deliberately not given here.

**Audit outcome: not affected.**
- This repository's Python call sites that could reach the affected code were identified.
- They were tested directly, at the exact matrix shapes this code uses, with a fired positive control.
- No result needs re-running.
- The certificates (Arb, MPFR, exact rational arithmetic, Lean) do not use the library at all.

The full audit is kept locally until disclosure is complete.
