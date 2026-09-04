#!/usr/bin/env python3
"""Close the last few percent: halve m again at the PLATEAU window.

At N=1024, m=0.0025 the plateau gives a(120)=0.004371, still 2.8% under the
bound. The earlier fixed-window m-scan converged from below with each halving of
m adding ~1/3 of the previous increment. This takes one more halving -- which
needs N=2048 to keep xi/N in range -- and extrapolates."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "fit", "make_regs"))

BOUND = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
N, m = 2048, 0.00125
RS = list(range(4, 37, 2))
print(f"N={N} m={m} xi={1/m:.0f} xi/N={1/m/N:.2f} Rmax/xi={RS[-1]*m:.3f}")
print(f"bound {BOUND:.7f}\n", flush=True)
GX, GP = kernels(N, make_regs(m)["nn"])
S = []
for R in RS:
    S.append(entropy(hexagon(R, N), N, GX, GP))
    print(f"  R={R:3d}  S={S[-1]:12.6f}", flush=True)
json.dump({"N": N, "m": m, "R": RS, "S": S},
          open("qsim/corner_m_extrap.json", "w"), indent=1)

def a120(rs, ss, rich=False): return -fit(rs, ss, 6, rich)[1]/6.0
print(f"\n  {'window':>10}{'a120 3par':>12}{'a120 4par':>12}{'3par/bound':>12}")
best = None
for j in range(0, len(RS)-5):
    rs, ss = RS[j:j+6], S[j:j+6]
    v3, v4 = a120(rs, ss), a120(rs, ss, True)
    if best is None or abs(v3-v4) < best[0]: best = (abs(v3-v4), rs[0], rs[-1], v3, v4)
    print(f"  {f'{rs[0]}..{rs[-1]}':>10}{v3:12.7f}{v4:12.7f}{v3/BOUND:12.3f}")
print(f"\n  3par/4par crossing at window {best[1]}..{best[2]}: "
      f"3par={best[3]:.7f} 4par={best[4]:.7f} (differ {best[0]:.1e})")
prev = 0.0043706                      # N=1024, m=0.0025 plateau
d = best[3] - prev
print(f"\n  m=0.0025 plateau {prev:.7f} -> m=0.00125 plateau {best[3]:.7f}"
      f"  (delta {d:+.7f})")
print(f"  geometric extrapolation m->0 (ratio 3.1/halving): "
      f"{best[3] + d/3.1/(1-1/3.1):.7f}")
print(f"  bound {BOUND:.7f}")
