#!/usr/bin/env python3
"""Independent confirmation on a DIFFERENT angle and a DIFFERENT shape.

If the diagnosis is right -- committed numbers biased low by an IR regime where
the box outranked the mass, plus a fit window sitting in lattice corrections --
then the SAME correction applied to triangles must move a(60) the same way. A
fix that only repairs the number it was designed around is not a fix."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, triangle, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "triangle", "fit", "make_regs"))

BOUND60 = (1.0/32.0)*np.log(2.0)
N, m = 1024, 0.0025
LS = list(range(8, 73, 4))
print(f"N={N} m={m} xi={1/m:.0f}  xi/N={1/m/N:.2f}  lmax/xi={LS[-1]*m:.3f}")
print(f"bound a(60) >= {BOUND60:.7f}   committed 0.0242324\n")
GX, GP = kernels(N, make_regs(m)["nn"])
S = []
for l in LS:
    s = entropy(triangle(l, N), N, GX, GP)
    S.append(s)
    print(f"  l={l:3d} sites={l*(l+1)//2:5d}  S={s:12.6f}", flush=True)
json.dump({"N": N, "m": m, "l": LS, "S": S}, open("qsim/corner_tri_check.json","w"),
          indent=1)

def a60(ls, ss, rich=False):
    return -fit(ls, ss, 3, rich)[1]/3.0

print("\n" + "="*62)
print("SLIDING WINDOW of 6")
print("="*62)
print(f"  {'window':>12}{'a60 3par':>12}{'a60 4par':>12}{'3par/bound':>12}")
for j in range(0, len(LS)-5):
    ls, ss = LS[j:j+6], S[j:j+6]
    print(f"  {f'{ls[0]}..{ls[-1]}':>12}{a60(ls,ss):12.7f}{a60(ls,ss,True):12.7f}"
          f"{a60(ls,ss)/BOUND60:12.3f}")
print("\n" + "="*62)
print("GROWING WINDOW from the large-l end")
print("="*62)
print(f"  {'window':>12}{'npts':>6}{'a60 3par':>12}{'3par/bound':>12}")
for lo in range(0, len(LS)-3):
    ls, ss = LS[lo:], S[lo:]
    print(f"  {f'{ls[0]}..{ls[-1]}':>12}{len(ls):6d}{a60(ls,ss):12.7f}"
          f"{a60(ls,ss)/BOUND60:12.3f}")
