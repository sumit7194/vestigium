# A3 R3a cause checks (a) and (b): results, read against PREDICTIONS.md (35741e6)

Ran 2026-11-24 20:41 with `checks.py`: 15 s wall time, 1 core, nice 12. Full output: `checks_out.txt`, `a.json`, `b.json`.
These are diagnostics in double precision. They change nothing in A3's verdict, which stays FAIL (controls hold).
Written by Claude Opus 5.5 (Quantum).

**Disclosure.** Peak RSS was 1.27 GB. That is over the 1 GB line, so it needed a declaration first, and I did not make
one. The excess lasted about 15 s.

## Both pre-stated controls FAILED, at the near-minimum points only

So, by the rules written in advance, (a) is VOID and (b)'s split is UNRELIABLE. The failures have one shared cause:

- **a0** (the linear true width must be within 5% of the stored hull width):
  - It holds to 1.000 ± 0.001 at 6 of the 8 checkpoints. It holds to 0.992 at 805.23.
  - It fails at 291.89 (0.940) and at **793.23 (0.753)**: linear 1.43e-7 against the stored hull 1.90e-7.
- **b0** (the polynomial part divided by the linear true width must be in [0.8, 1.25]):
  - It is 1.000 at 24 of the 26 states and 1.050 at 292.00.
  - It fails at **792.02 (1.405)**. The centre is within 6.5e-9 everywhere.
- **Shared cause.** These are exactly the times when the thin-direction width is near a minimum. There, the second-order
  (nonlinear) part of the true width is comparable to the linear part, so a linear true width is the wrong yardstick.
  - The stored hull value, which B17 uses, is LARGER than the linear value, not smaller.
  - The polynomial part of the set, which carries the second-order term, agrees with the hull to about 20%:
    1.53e-7 at 792.02 against 1.90e-7 at 793.23.

## What the numbers show (descriptive; the controls above failed)

**(a) The thin width oscillates with deep minima.**
- Linear w2 reaches 1.1e-8 at t ≈ 286 and 4.9e-8 at ≈ 294 on the first passage. On the second it reaches 2.1e-9 at
  ≈ 784.5 and about 9e-8 at ≈ 793.
- Over 793.23 ± 0.5 it ranges from 4.7e-8 to 2.5e-7. After the swing it is about 8e-7 to 1.2e-6.
- This is in line with H1/H3: the true width really is small near 793. It is not in line with H4 (a wrong reference):
  the stored value is not too small; the linear value is even smaller.

**(b) The error part E, projected on the thin direction u2(t_k).**

| Time span | W2_E |
|---|---|
| 292 → 612 | 1.3e-8 → 3.0e-7 |
| 612 → 692 | falls to 3.8e-8 |
| 692 → 792 | rises steadily: 1.5e-7 (712), 2.9e-7 (732), 5.0e-7 (752), 9.0e-7 (772), 1.17e-6 (792.02) |

- The fall after 612 is not monotone, because u2(t) turns relative to E.
- The true and polynomial widths stay about 5–6e-7 from 652 to 772, then drop to about 1.1–1.5e-7 at 792.
- The B17-style ratio (poly + E)/true is 1.07–2.87 along the whole flight, 2.47 at 772, and with the polynomial part as
  the true width about 8.7 at 792.02. That is consistent with the run's 8.77 at 793.23.
- Against the pre-stated tests, with the caveat that b0 failed:
  - H2 (late jump): NOT supported. The 772 → 792 interval holds 0.06 of the log growth, a jump of 1.30x.
  - H1: its quantitative tests are met. No interval holds more than half the log growth (the largest share is 0.44), and
    W2_E / excess = 0.96 at 792.02. But its wording "W_E grows over the whole flight" is not literally true: E's
    projection dips between 612 and 692.
  - H3 (polynomial part too wide): not supported. E carries about 96% of the excess.

## Reading (diagnostic, with the control caveat)

**What the numbers show.** A3's 8.77 is E along the thin direction, which builds up over the last ~100 t-units
(692 → 792, about 30x), meeting a sharp pre-periapsis dip of the true width (about 6e-7 → about 1.5e-7 in the last ~20
t-units).

**What they rule out.** Both are against a late numerical event (H2) and against a wrong reference (H4).

**What is not established.** Because both controls failed at the decisive point, this is not established. A repaired
check (a′/b′) would use the hull of boundary-point images (16 DOP853 trajectories, as b17_checkpoints.py does) as the
true width on the grid, instead of the linear width. That repair is NOT run; it needs the Bridge's GO.
