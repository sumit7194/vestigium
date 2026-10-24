# Audit: Apple Accelerate dgeqrf heap overrun (fleet alert), 2026-10-11; disclosure closed 2026-10-24

A fleet alert reported a heap overrun in Apple Accelerate's QR factorisation (dgeqrf). It was reported to Apple, who
classified it as a reliability defect, not a security issue. It is fixed in macOS 27.0.1. Verified here on 2026-10-24
(macOS 27.0.1, build 26A434): the reproducer exits rc 0 under Guard Malloc, where before the update it crashed (rc 139).

**Audit outcome (2026-10-11): not affected.**
- This repository's Python call sites that could reach the affected code were identified.
- They were tested directly, at the exact matrix shapes this code uses, with a fired positive control.
- No result needs re-running.
- The certificates (Arb, MPFR, exact rational arithmetic, Lean) do not use the library at all.

The original audit text and its Guard Malloc scripts are in this repository's history (commits 829ec37 and 17af42f;
redacted in b1883d5 during the disclosure). The history is not rewritten.
