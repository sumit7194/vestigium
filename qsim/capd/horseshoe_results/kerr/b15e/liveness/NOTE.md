# Liveness samples, 2026-11-26 15:01–15:06 (kerr_e N1N2 on the Mac mini, kerr_e N2N3 on the Air)

Asked for by the personal Bridge to tell "slow" from "stuck". No chunk had written its first edge record: N1N2 had run 3 h 31 min (PID 32284, hs_cover_b15e2 77eb34a6), and the Air chunks 2 h 02 min (N2N3 is PID 8602, hs_cover_b15e2s df234aa2).

How the samples were taken: with read-only macOS `sample <pid> 5`, twice per process about 4 min apart, and no signal sent. The files are n1n2_s1.txt (15:01:58), n1n2_s2.txt (15:06:10), air_n2n3_s1.txt (15:02:04) and air_n2n3_s2.txt (15:06:16).

What they show:
- In all four samples the main thread is three cover_b frames deep, which is bisection depth 2 of the first top-level edge piece. Under that it runs image(), CAPD's rigorous integrator, and Taylor/autodiff arithmetic at MPFR 128 bits. There is no tight loop.
- N1N2 moved on between its two samples: from the Poincaré-map call (PoincareMap) to the energy-level replay (TimeMap) that image() runs next.
- N2N3 was inside the Poincaré-map call in both of its samples, with different stack counts. Two samples are not enough to tell one long call from the next sub-piece.

Why no record yet: the binary prints no progress. Its only stderr text is the usage line, and stderr goes to the .out. An EP record is written only after a whole top-level edge piece finishes, its bisection tree included, and the spec allows depth 12 and a cumulative 2 × 4096 leaves. That fits the earlier 48 h timeouts of N1N2 and N2N3 (23–25 Nov, old binary).

Verdict: SLOW, NOT STUCK. Nothing was changed, and the chunks keep running. Recorded by Claude Opus 5.5 (Quantum-personal).
