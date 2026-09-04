#!/usr/bin/env python3
"""Measure the m->0 convergence ratio AT THE PLATEAU instead of importing it.

The m->0 extrapolation that puts a(120) above the bound used r = 3.1 per halving
of m -- measured, but at the FIXED SMALL-R window R=4..14, not at the plateau.
With only two plateau points (m=0.0025, 0.00125) r is unconstrained, and the
conclusion is sensitive to it: r=3.1 gives 1.0033x the bound, r=5 gives 0.9986x.
The bound-satisfied claim flips at r ~ 4.3.

This adds a THIRD plateau point at m=0.005, N=512, chosen so that xi/N = 0.391
matches the 0.39 of the other two -- the series then varies m alone at fixed
geometry, and r is measured rather than assumed."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "fit", "make_regs"))

BOUND = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
N, m = 512, 0.005
RS = list(range(4, 37, 2))
print(f"N={N} m={m} xi={1/m:.0f} xi/N={1/m/N:.3f} (matches 0.39 of the other two)")
GX, GP = kernels(N, make_regs(m)["nn"])
S = []
for R in RS:
    S.append(entropy(hexagon(R, N), N, GX, GP))
    print(f"  R={R:3d}  S={S[-1]:12.6f}", flush=True)
json.dump({"N": N, "m": m, "R": RS, "S": S},
          open("qsim/corner_ratio_measure.json", "w"), indent=1)

def a120(rs, ss, rich=False): return -fit(rs, ss, 6, rich)[1]/6.0
p3 = a120(RS[-6:], S[-6:]); p4 = a120(RS[-6:], S[-6:], True)
print(f"\n  plateau window 26..36: 3par={p3:.7f} 4par={p4:.7f}")

# the three plateau points, xi/N held at 0.39
pts = [(0.005, p3), (0.0025, 0.0043706), (0.00125, 0.0044650)]
print("\n  m        a(120) plateau     increment")
prev = None
incs = []
for mm, v in pts:
    inc = "" if prev is None else f"{v-prev:+.7f}"
    if prev is not None: incs.append(v-prev)
    print(f"  {mm:<9.5f}{v:.7f}   {inc}")
    prev = v
r = incs[0]/incs[1]
print(f"\n  MEASURED ratio per halving at the plateau: r = {r:.2f}")
print(f"  (the value imported from the R=4..14 window was 3.1)")
rem = incs[1]/(r-1.0)
ext = pts[-1][1] + rem
print(f"  extrapolation m->0: {pts[-1][1]:.7f} + {rem:.7f} = {ext:.7f}")
print(f"  bound {BOUND:.7f}  ->  {ext/BOUND:.4f}x  "
      f"{'BOUND SATISFIED' if ext > BOUND else 'STILL BELOW'}")
print(f"\n  4-param at m=0.00125 measured directly: 0.0045195 = "
      f"{0.0045195/BOUND:.4f}x (above, no extrapolation)")
