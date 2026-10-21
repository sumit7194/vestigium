import subprocess
O = "qsim/capd/horseshoe_results/mn_smoke/"
def true(h):
    out = subprocess.run(["sims/.venv/bin/python", "qsim/capd/horseshoe/tests/true_widths.py", str(h), "250", "292", "1"], capture_output=True, text=True).stdout.split("\n")
    T = {}
    for l in out:
        if l.startswith("t="): p = l.split(); T[round(float(p[1]))] = (float(p[6]), float(p[10]))
    return T
def run(fn, cx, cp):
    R = {}
    for l in open(O + fn):
        if l[0].isdigit():
            p = l.split(); t = float(p[1])
            if abs(t - round(t)) < 0.4 and round(t) not in R: R[round(t)] = (float(p[cx]), float(p[cp]))
    return R
T6, T8 = true(1e-6), true(1e-8)
runs = [("D 4-D 1e-6", "diag_D.out", 7, 8, T6), ("8-D 1e-6", "diag8_A.out", 3, 4, T6), ("E 4-D 1e-8", "diag_E.out", 7, 8, T8)]
RR = [(nm, run(fn, cx, cp), T) for nm, fn, cx, cp, T in runs]
print("set width / true width  (x, px)")
for t in [250, 260, 270, 278, 282, 285, 287, 288, 289, 290, 291, 292]:
    row = "t=%3d " % t
    for nm, R, T in RR:
        row += " | %-11s " % nm + ("%7.1f %7.1f" % (R[t][0] / T[t][0], R[t][1] / T[t][1]) if t in R and t in T else "    -       -  ")
    print(row)
