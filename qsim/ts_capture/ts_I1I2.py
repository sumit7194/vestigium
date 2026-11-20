"""ts_I1I2.py -- C-I1 / C-I2 of the TS capture-edge recipe under Arb (PREREG_I1_I2.md, REGISTERED 9f6a805).
From the STATEMENTS (V24 PREREGISTRATION.md), not from the Bridge's code. Metric: quantum's TS2 package
(ts2_metric_components_t1o3.txt, p = 4/5, q = 3/5), sigma = 1. E = 97/100, L = 41/8.
Outputs go ONLY to the gitignored qsim/scratch/ts_capture/ (the Bridge's decision; TS results to the Bridge only).
Usage: ts_I1I2.py   -> qsim/scratch/ts_capture/I1I2.json (and stdout).   Written by Claude Opus 5.5 (session "Quantum")."""
import json, sys, time
from pathlib import Path
import sympy as sp
from sympy.printing.pycode import PythonCodePrinter
from flint import arb, ctx
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent))
import mr_ts2 as T

OUT = HERE.parent / "scratch" / "ts_capture"; OUT.mkdir(parents=True, exist_ok=True)
X, Y = T.X, T.Y; S = sp.Symbol("s", real=True)
E, L = sp.Rational(97, 100), sp.Rational(41, 8)


class P(PythonCodePrinter):
    def _print_Pow(self, e, rational=False):
        b, ex = e.as_base_exp()
        if ex.is_Integer: return "(%s)**(%d)" % (self._print(b), int(ex))
        raise ValueError("non-integer power %s" % e)
    def _print_Rational(self, e): return "(ONE*%d/%d)" % (e.p, e.q)
    def _print_Integer(self, e): return "(ONE*%d)" % int(e)
    def _print_Float(self, e): raise ValueError("float %s" % e)
    def _print_Symbol(self, s): return s.name


def compile_(name, ex, args):
    reps, (red,) = sp.cse([ex], symbols=sp.numbered_symbols("t"), optimizations="basic")
    pr = P(); src = ["def %s(%s):" % (name, ", ".join(args))]
    src += ["    %s = %s" % (s, pr.doprint(v)) for s, v in reps] + ["    return %s" % pr.doprint(red)]
    ns = dict(ONE=arb(1)); exec("\n".join(src), ns); return ns[name]


def build():
    comps = T._read_components(str(Path(T.PKG) / "ts2_metric_components_t1o3.txt"))
    g = {k: sp.sympify(v).subs(T.SIG, 1) for k, v in comps.items()}
    gi = T._inverse(comps, 1)
    S0_flat = sp.cancel(g["g_xx"] * (X**2 - 1) - g["g_yy"] * (1 - Y**2)) == 0
    F = sp.cancel(g["g_xx"] * (X**2 - 1))
    W = gi["tt"] * E**2 - 2 * gi["tphi"] * E * L + gi["phiphi"] * L**2
    V = sp.cancel(F * (W + 1) / 2)
    S0_even = sp.cancel(V - V.subs(Y, -Y)) == 0
    n, d = sp.fraction(V)
    ns = sp.Poly(n, Y); ds = sp.Poly(d, Y)
    assert all(m[0] % 2 == 0 for m in ns.monoms()) and all(m[0] % 2 == 0 for m in ds.monoms()), "odd powers of y"
    to_s = lambda p: sum(c * S**(m[0] // 2) for m, c in zip(p.monoms(), p.coeffs()))
    Vs = sp.cancel(to_s(ns) / to_s(ds))
    G = sp.cancel((1 - S) * Vs)
    Gn, Gd = sp.fraction(G)
    G_no_axis_pole = sp.cancel(Gd.subs(S, 1)) != 0                 # G has no pole at the axis s = 1
    dVx = sp.cancel(sp.diff(Vs, X)); dVs = sp.cancel(sp.diff(Vs, S))
    return dict(G=compile_("G", G, ["x", "s"]), dVx=compile_("dVx", dVx, ["x", "s"]), dVs=compile_("dVs", dVs, ["x", "s"]),
                V=compile_("V", Vs, ["x", "s"]), S0_flat=bool(S0_flat), S0_even=bool(S0_even), G_no_axis_pole=bool(G_no_axis_pole))


def check(f, deriv, x0, x1, s0, s1, sign=+1, depth=24):
    """bisection: a box is DECIDED if G > 0 (outside Hill) or sign*deriv > 0. Returns counts, undecided, violations."""
    stack = [(arb(x0), arb(x1), arb(s0), arb(s1), 0)]; dec_out = dec_in = 0; und = []; viol = []; minlb = None
    while stack:
        a, b, c, d, k = stack.pop()
        xb = (a + b) / 2 + arb(0, ((b - a) / 2).upper()); sb = (c + d) / 2 + arb(0, ((d - c) / 2).upper())
        G = f["G"](xb, sb)
        if G.is_finite() and G > 0: dec_out += 1; continue
        D = deriv(xb, sb)
        if D.is_finite() and sign * D > 0:
            dec_in += 1; lb = float((sign * D).lower()); minlb = lb if minlb is None or lb < minlb else minlb; continue
        if D.is_finite() and sign * D < 0 and G.is_finite() and G < 0:
            viol.append([float(a), float(b), float(c), float(d)]); continue
        if k >= depth: und.append([float(a), float(b), float(c), float(d)]); continue
        if (b - a) / max(float(x1 - x0), 1e-300) >= (d - c):                   # split the relatively longer side
            m = (a + b) / 2; stack += [(a, m, c, d, k + 1), (m, b, c, d, k + 1)]
        else:
            m = (c + d) / 2; stack += [(a, b, c, m, k + 1), (a, b, m, d, k + 1)]
    return dict(decided_outside=dec_out, decided_inside=dec_in, undecided=len(und), violations=len(viol),
                min_lower_bound=minlb, undecided_sample=und[:5], violation_sample=viol[:5])


def main():
    ctx.prec = 128; t0 = time.time(); f = build()
    res = dict(S0_flat=f["S0_flat"], S0_even=f["S0_even"], G_no_axis_pole=f["G_no_axis_pole"], build_s=round(time.time() - t0, 1))
    print("S0", res, flush=True)
    runs = [("I1", f["dVx"], 1.5, 9.49, +1, 40), ("I2", f["dVs"], 9.3, 77.1, +1, 24),
            ("NEG_I1_to_9.6", f["dVx"], 1.5, 9.6, +1, 24), ("NEG_I2_reversed", f["dVs"], 9.3, 77.1, -1, 24)]
    for name, dv, x0, x1, sg, dep in runs:            # A1 (post-result): I1 at depth 40
        t1 = time.time(); r = check(f, dv, x0, x1, 0, 1, sg, depth=dep); r["depth"] = dep; r["seconds"] = round(time.time() - t1, 1); res[name] = r
        print(name, {k: v for k, v in r.items() if not k.endswith("sample")}, flush=True)
    ok = res["S0_flat"] and res["S0_even"] and res["G_no_axis_pole"]
    p = lambda n: res[n]["undecided"] == 0 and res[n]["violations"] == 0
    neg = lambda n: res[n]["undecided"] > 0 or res[n]["violations"] > 0
    res["verdict"] = ("CONFIRMED-ARB" if ok and p("I1") and p("I2") and neg("NEG_I1_to_9.6") and neg("NEG_I2_reversed") else
                      "FALSIFIED" if res["I1"]["violations"] or res["I2"]["violations"] else "INCONCLUSIVE or a control/gate failure")
    (OUT / "I1I2.json").write_text(json.dumps(res, indent=1)); print("VERDICT", res["verdict"])


if __name__ == "__main__":
    main()
