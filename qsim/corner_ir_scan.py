#!/usr/bin/env python3
"""Is the a(120) deficit an IR artifact of the box, or physics?

The committed run used N=160, m=0.01 -> xi=100, i.e. the correlation length is
0.62 of the BOX. The k=0 mode has omega=m, so GX(k=0)=1/(2m)=50: the softest
modes are barely regulated and the box, not the mass, is the real IR cutoff.

If that is the cause, a(120) at a FIXED fit window must MOVE with N and m. If it
is physics, it must not. The four regulators in the committed run all share one
(N, m, window), so their 1.85% spread cannot see this at all."""
import json
import numpy as np

src = open("qsim/corner_angles.py").read()
ns = {}
exec(compile(src[:src.index("# ============================ measurement")
                 if "# ============================ measurement" in src
                 else src.index("# ================================ measurement")],
             "corner_angles.py[functions]", "exec"), ns)
kernels, entropy, hexagon, fit, make_regs = (ns[k] for k in
    ("kernels", "entropy", "hexagon", "fit", "make_regs"))

BOUND = (1.0/32.0)*np.log(2.0/np.sqrt(3.0))
WIN = [4, 6, 8, 10, 12, 14]          # the committed window, held fixed
WIDE = [4, 6, 8, 10, 12, 14, 16, 18, 20]

print(f"bound a(120) >= {BOUND:.7f}; committed 0.0038956 (13.3% below)\n")
print(f"{'N':>6}{'m':>8}{'xi':>7}{'xi/N':>7}{'a120 R4-14':>13}{'/bound':>9}"
      f"{'a120 R4-20':>13}{'/bound':>9}")
rows = []
for N, m in [(160, 0.01), (240, 0.01), (320, 0.01), (480, 0.01),
             (320, 0.02), (320, 0.04), (320, 0.005)]:
    GX, GP = kernels(N, make_regs(m)["nn"])
    S = {R: entropy(hexagon(R, N), N, GX, GP) for R in WIDE}
    a14 = -fit(WIN,  [S[R] for R in WIN],  6)[1]/6.0
    a20 = -fit(WIDE, [S[R] for R in WIDE], 6)[1]/6.0
    rows.append(dict(N=N, m=m, a14=a14, a20=a20))
    print(f"{N:6d}{m:8.3f}{1/m:7.0f}{1/m/N:7.2f}{a14:13.7f}{a14/BOUND:9.3f}"
          f"{a20:13.7f}{a20/BOUND:9.3f}", flush=True)
json.dump(rows, open("qsim/corner_ir_scan.json", "w"), indent=1)

f = [r["a14"] for r in rows if r["m"] == 0.01]
print(f"\nAt fixed m=0.01, varying N alone: a(120) spans "
      f"{min(f):.7f}..{max(f):.7f}  = {(max(f)-min(f))/np.mean(f):.1%}")
g = [r["a14"] for r in rows if r["N"] == 320]
print(f"At fixed N=320, varying m alone: a(120) spans "
      f"{min(g):.7f}..{max(g):.7f}  = {(max(g)-min(g))/np.mean(g):.1%}")
print(f"\nCommitted across-REGULATOR spread was 1.85% -- all four regulators")
print(f"shared one (N, m, window), so that spread was blind to the above.")
