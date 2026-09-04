#!/usr/bin/env python3
"""Why is a(120 deg) below the BWK16 bound?

The bound a(th) >= (pi^2 C_T/3) log[1/sin(th/2)] has no fitted parameter and no
threshold; for a real scalar (C_T = 3/(32 pi^2)) the prefactor is exactly 1/32,
so a_min(120) = (1/32) log(2/sqrt 3) = 0.0044950. The committed value is
0.0038956 -- 13.3% BELOW something that cannot be below it. That is a defect in
the extraction, and this script finds which one.

DESIGN: reuse the ORIGINAL code, not a re-derivation. The source of
corner_angles.py is exec'd up to its measurement block, so kernels(), entropy()
and hexagon() here are byte-identical to the ones that produced the number.

The suspect is the fit window. HEX = [4,6,8,10,12,14] is SIX points carrying
3-4 parameters over ln R in [1.39, 2.64] -- a lever arm of 1.25 -- and the
smallest hexagon has 61 sites. This sweeps R far past 14 and watches a(120) as
a function of the window, which the original never did.

Raw S(R) is written to disk. Its absence is itself a defect: the committed JSON
kept only fitted coefficients, so this question could not be asked without a
re-run."""
import json, re, sys
import numpy as np

src = open("qsim/corner_angles.py").read()
cut = src.index("# ================================ measurement")
ns = {}
exec(compile(src[:cut], "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, triangle, fit = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "triangle", "fit"))

BOUND120 = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
BOUND60  = (1.0/32.0)*np.log(2.0)

N, m, REG = 160, 0.01, "nn"
RS = list(range(4, 33, 2))
print(f"N={N} m={m} (xi={1/m:.0f}) regulator={REG}")
print(f"hexagons R={RS[0]}..{RS[-1]}  (max {len(hexagon(RS[-1], N))} sites)")
print(f"bound a(120) >= {BOUND120:.7f}   committed value 0.0038956\n")

GX, GP = kernels(N, ns["make_regs"](m)[REG])
S = []
for R in RS:
    s = entropy(hexagon(R, N), N, GX, GP)
    S.append(s)
    print(f"  R={R:3d}  sites={len(hexagon(R,N)):5d}  S={s:12.6f}", flush=True)

json.dump({"N": N, "m": m, "regulator": REG, "R": RS, "S": S,
           "bound_a120": BOUND120},
          open("qsim/corner_bound_diag.json", "w"), indent=1)

def a120(rs, ss, rich=False):
    return -fit(rs, ss, 6, rich)[1]/6.0

print("\n" + "="*70)
print("REPLICATION of the committed window")
print("="*70)
i14 = RS.index(14)
rep3 = a120(RS[:i14+1], S[:i14+1])
rep4 = a120(RS[:i14+1], S[:i14+1], True)
print(f"  R=4..14  3-param a(120) = {rep3:.7f}   committed 0.0038960 (nn)")
print(f"  R=4..14  4-param a(120) = {rep4:.7f}   committed 0.0035869 (nn)")
print(f"  -> {'REPLICATED' if abs(rep3-0.003895975) < 2e-6 else '*** DOES NOT REPLICATE ***'}")

print("\n" + "="*70)
print("GROWING WINDOW  R=4..Rmax   (does it converge above the bound?)")
print("="*70)
print(f"  {'Rmax':>5}{'npts':>6}{'ln range':>10}{'a120 3par':>12}{'a120 4par':>12}"
      f"{'3par/bound':>12}")
for j in range(2, len(RS)):
    rs, ss = RS[:j+1], S[:j+1]
    v3, v4 = a120(rs, ss), a120(rs, ss, True)
    print(f"  {rs[-1]:5d}{len(rs):6d}{np.log(rs[-1])-np.log(rs[0]):10.2f}"
          f"{v3:12.7f}{v4:12.7f}{v3/BOUND120:12.3f}")

print("\n" + "="*70)
print("SLIDING WINDOW  6 consecutive R   (isolates WHERE the bias lives)")
print("="*70)
print(f"  {'window':>12}{'a120 3par':>12}{'a120 4par':>12}{'3par/bound':>12}")
for j in range(0, len(RS)-5):
    rs, ss = RS[j:j+6], S[j:j+6]
    v3, v4 = a120(rs, ss), a120(rs, ss, True)
    print(f"  {f'{rs[0]}..{rs[-1]}':>12}{v3:12.7f}{v4:12.7f}{v3/BOUND120:12.3f}")

print("\n" + "="*70)
print("DROP THE SMALLEST HEXAGONS  (R=4 has 61 sites; R=6 has 127)")
print("="*70)
print(f"  {'window':>12}{'npts':>6}{'a120 3par':>12}{'3par/bound':>12}")
for lo in range(0, 6):
    rs, ss = RS[lo:], S[lo:]
    v3 = a120(rs, ss)
    print(f"  {f'{rs[0]}..{rs[-1]}':>12}{len(rs):6d}{v3:12.7f}{v3/BOUND120:12.3f}")
