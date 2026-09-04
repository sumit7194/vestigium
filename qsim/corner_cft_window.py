#!/usr/bin/env python3
"""Find the regime where the lattice scalar is actually a CFT, then read a(120).

The BWK16 bound applies to a CFT. The extraction needs BOTH
    R << xi   (else the mass cuts the corner log)   and   xi << N (else the box
    is the real IR cutoff and the softest modes are unregulated).
The committed run had R_max/xi = 0.14 but xi/N = 0.62 -- and the four regulators
all shared that one point, so their 1.85% spread could not see either failure.

This scans (N, m) and reports a(120) with both dimensionless ratios, looking for
a PLATEAU where the number stops moving. Fit window held at the committed
R = 4..14 throughout so nothing but the regime changes."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "fit", "make_regs"))

BOUND = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
WIN = [4, 6, 8, 10, 12, 14]
print(f"bound a(120) >= {BOUND:.7f}   committed 0.0038956\n")
print(f"{'N':>6}{'m':>8}{'xi':>7}{'Rmax/xi':>9}{'xi/N':>7}{'a(120)':>12}"
      f"{'/bound':>9}")
rows = []
for N in (320, 640, 1024):
    for m in (0.04, 0.02, 0.01, 0.005, 0.0025):
        xi = 1.0/m
        GX, GP = kernels(N, make_regs(m)["nn"])
        S = [entropy(hexagon(R, N), N, GX, GP) for R in WIN]
        a = -fit(WIN, S, 6)[1]/6.0
        rows.append(dict(N=N, m=m, Rmax_over_xi=14/xi, xi_over_N=xi/N, a120=a))
        print(f"{N:6d}{m:8.4f}{xi:7.0f}{14/xi:9.3f}{xi/N:7.3f}{a:12.7f}"
              f"{a/BOUND:9.3f}", flush=True)
    print()
json.dump(rows, open("qsim/corner_cft_window.json", "w"), indent=1)

good = [r for r in rows if r["Rmax_over_xi"] < 0.16 and r["xi_over_N"] < 0.35]
print("Points satisfying BOTH Rmax/xi < 0.16 and xi/N < 0.35:")
for r in good:
    print(f"  N={r['N']:5d} m={r['m']:.4f}  a(120)={r['a120']:.7f}"
          f"  ratio to bound {r['a120']/BOUND:.3f}")
if good:
    v = [r["a120"] for r in good]
    print(f"\n  spread across that regime: {(max(v)-min(v))/np.mean(v):.1%}")
    print(f"  mean {np.mean(v):.7f}  vs bound {BOUND:.7f} "
          f"-> {'ABOVE (bound satisfied)' if np.mean(v) > BOUND else 'still BELOW'}")
