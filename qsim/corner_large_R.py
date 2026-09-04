#!/usr/bin/env python3
"""The one limit not yet taken: LARGE R inside a good CFT regime.

Every scan so far held the committed window R=4..14. The m-scan converges to
a(120) ~ 0.00416, still 7.5% under the bound, so the remaining deficit must be
a small-region (lattice/UV) effect rather than a mass effect.

The first diagnostic DID push R up and saw a(120) collapse to negative -- but
that was at N=160, xi/N=0.62, where large regions hit the box. That collapse was
a box artifact and says nothing about the continuum.

Here N=1024, m=0.0025 (xi=400): at R=36, Rmax/xi=0.09 and xi/N=0.39, so BOTH
conditions hold across the whole sweep for the first time."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "fit", "make_regs"))

BOUND = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
N, m = 1024, 0.0025
RS = list(range(4, 37, 2))
print(f"N={N} m={m} xi={1/m:.0f}  xi/N={1/m/N:.2f}  Rmax/xi={RS[-1]*m:.3f}")
print(f"bound a(120) >= {BOUND:.7f}\n")

GX, GP = kernels(N, make_regs(m)["nn"])
S = []
for R in RS:
    s = entropy(hexagon(R, N), N, GX, GP)
    S.append(s)
    print(f"  R={R:3d} sites={3*R*R+3*R+1:5d}  S={s:12.6f}", flush=True)
json.dump({"N": N, "m": m, "R": RS, "S": S}, open("qsim/corner_large_R.json", "w"),
          indent=1)

def a120(rs, ss, rich=False):
    return -fit(rs, ss, 6, rich)[1]/6.0

print("\n" + "="*64)
print("SLIDING WINDOW of 6 -- does a(120) rise toward the bound with R?")
print("="*64)
print(f"  {'window':>10}{'a120 3par':>12}{'a120 4par':>12}{'3par/bound':>12}")
for j in range(0, len(RS)-5):
    rs, ss = RS[j:j+6], S[j:j+6]
    print(f"  {f'{rs[0]}..{rs[-1]}':>10}{a120(rs,ss):12.7f}"
          f"{a120(rs,ss,True):12.7f}{a120(rs,ss)/BOUND:12.3f}")

print("\n" + "="*64)
print("GROWING WINDOW from the large-R end (drops lattice-scale hexagons)")
print("="*64)
print(f"  {'window':>10}{'npts':>6}{'a120 3par':>12}{'a120 4par':>12}{'3par/bound':>12}")
for lo in range(0, len(RS)-3):
    rs, ss = RS[lo:], S[lo:]
    print(f"  {f'{rs[0]}..{rs[-1]}':>10}{len(rs):6d}{a120(rs,ss):12.7f}"
          f"{a120(rs,ss,True):12.7f}{a120(rs,ss)/BOUND:12.3f}")
