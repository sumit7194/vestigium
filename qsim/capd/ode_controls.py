"""Checker for the CAPD ODE controls (registered in qsim/capd/ODE_CONTROLS.md). Reads tests/odectl.out (CAPD MPFR
enclosures, exact %Ra endpoints) and verifies that every exact value, enclosed by Arb at 1024 bits (refined to 4096
on ambiguity), lies certainly inside CAPD's enclosure. Then runs the fired controls: (i) collapse every CAPD
interval to its upper endpoint, which must be rejected; (ii) the wrong-equation trace must certainly EXCLUDE the
true trace.  Usage: ode_controls.py [odectl.out]"""
import json, random, sys
from pathlib import Path
from flint import arb, acb, ctx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from diffcheck import parse_ra   # exact %Ra -> arb (validated in DIFFCHECK.md)

def load(path):
    d = {}
    for ln in open(path):
        if ln.startswith("#") or not ln.strip(): continue
        t, k, lo, hi = ln.split()
        L, H = parse_ra(lo), parse_ra(hi)
        assert L[0] == "fin" and H[0] == "fin", ln
        d.setdefault(t, {})[k] = (L[1], H[1])
    return d

def inside(iv, v):
    lo, hi = iv
    if lo <= v and v <= hi: return True
    if v < lo or v > hi: return False
    return None

def samples(iv, n, R):
    lo, hi = iv
    out = [lo, hi]
    for _ in range(n):
        u = arb(R.getrandbits(40)) / arb(2) ** 40
        s = lo + (hi - lo) * u
        out.append(s if (lo <= s and s <= hi) else lo)
    return out

def required(d):
    """list of (test, key, exact-value thunk); thunks are re-evaluated at each precision"""
    req = []
    R = random.Random(20261011)
    # R1 harmonic: rotation; corners + 16 interior points
    for T in (1, 10, 100):
        t = "R1_t%d" % T; b0, b1 = d[t]["box0"], d[t]["box1"]
        pts = [(x, y) for x in b0 for y in b1]
        for _ in range(16):
            ux, uy = R.getrandbits(40), R.getrandbits(40)
            pts.append(("u", ux, uy))
        def mk(pt, T=T, b0=b0, b1=b1, comp=0):
            def f():
                if pt[0] == "u":
                    x = b0[0] + (b0[1] - b0[0]) * arb(pt[1]) / arb(2) ** 40
                    y = b1[0] + (b1[1] - b1[0]) * arb(pt[2]) / arb(2) ** 40
                else: x, y = pt
                c, s = arb(T).cos(), arb(T).sin()
                return x * c + y * s if comp == 0 else -x * s + y * c
            return f
        for pt in pts:
            req.append((t, "x", mk(pt, comp=0))); req.append((t, "y", mk(pt, comp=1)))
    # R2 x' = x^2 at t = 3/2: x0/(1 - x0 t) and d/dx0 = 1/(1 - x0 t)^2, endpoints + 8 interior
    b = d["R2"]["box0"]
    us = [None, None] + [R.getrandbits(40) for _ in range(8)]
    for i, u in enumerate(us):
        def x0f(i=i, u=u):
            if i == 0: return b[0]
            if i == 1: return b[1]
            return b[0] + (b[1] - b[0]) * arb(u) / arb(2) ** 40
        T = arb(3) / 2
        req.append(("R2", "x", lambda x0f=x0f, T=T: x0f() / (1 - x0f() * T)))
        req.append(("R2", "dxdx0", lambda x0f=x0f, T=T: 1 / (1 - x0f() * T) ** 2))
    # R3 Hopf: polar exact
    b0, b1 = d["R3"]["box0"], d["R3"]["box1"]
    pts = [(x, y) for x in b0 for y in b1] + [("u", R.getrandbits(40), R.getrandbits(40)) for _ in range(16)]
    for pt in pts:
        def mk(pt=pt, comp=0):
            def f():
                if pt[0] == "u":
                    x = b0[0] + (b0[1] - b0[0]) * arb(pt[1]) / arb(2) ** 40
                    y = b1[0] + (b1[1] - b1[0]) * arb(pt[2]) / arb(2) ** 40
                else: x, y = pt
                r0sq = x * x + y * y; th0 = acb(x, y).arg(); T = arb(2)
                r = (1 + (1 / r0sq - 1) * (-2 * T).exp()) ** (-arb(1) / 2)
                th = th0 + T
                return r * th.cos() if comp == 0 else r * th.sin()
            return f
        req.append(("R3", "x", mk(comp=0))); req.append(("R3", "y", mk(comp=1)))
    # R4 Jacobian of the rotation
    for T in (1, 10):
        t = "R4_t%d" % T
        req += [(t, "D00", lambda T=T: arb(T).cos()), (t, "D01", lambda T=T: arb(T).sin()),
                (t, "D10", lambda T=T: -arb(T).sin()), (t, "D11", lambda T=T: arb(T).cos())]
    # complex monodromy: M = W0 diag(lambda^k) W0^{-1}, W0 = [[1,1],[r1,r2]]
    def euler_M(k):
        r1, r2 = arb(1) / 3, -arb(1) / 4
        l1 = (2 * acb.pi() * 1j * r1 * k).exp(); l2 = (2 * acb.pi() * 1j * r2 * k).exp()
        # W0 diag W0^{-1}; W0^{-1} = [[r2, -1], [-r1, 1]] / (r2 - r1)
        den = r2 - r1
        M = [[(l1 * r2 - l2 * r1) / den, (-l1 + l2) / den],
             [(r1 * r2 * (l1 - l2)) / den, (-r1 * l1 + r2 * l2) / den]]
        return M
    def ident(k=None): return [[acb(1), acb(0)], [acb(0), acb(1)]]
    def mreq(test, Mf):
        out = []
        for i in range(2):
            for j in range(2):
                for part in ("re", "im"):
                    out.append((test, "M%d%d%s" % (i, j, part), lambda i=i, j=j, part=part: getattr(Mf()[i][j], "real" if part == "re" else "imag")))
        def tr(): M = Mf(); return M[0][0] + M[1][1]
        def de(): M = Mf(); return M[0][0] * M[1][1] - M[0][1] * M[1][0]
        out += [(test, "trre", lambda: tr().real), (test, "trim", lambda: tr().imag),
                (test, "detre", lambda: de().real), (test, "detim", lambda: de().imag),
                (test, "tr2detre", lambda: (tr() ** 2 / de()).real), (test, "tr2detim", lambda: (tr() ** 2 / de()).imag)]
        return out
    for t in ("M1_A", "M1_B"):
        if t in d: req += mreq(t, lambda: euler_M(1))
    if "M2_comm" in d: req += mreq("M2_comm", ident)
    if "M3_AA" in d: req += mreq("M3_AA", lambda: euler_M(2))
    if "M4_noSing" in d: req += mreq("M4_noSing", ident)
    if "M5_airy" in d: req += mreq("M5_airy", ident)
    return req

def judge(iv, f):
    for wp in (1024, 4096):
        with ctx.workprec(wp):
            v = inside(iv, f())
        if v is not None: return v
    return None

def main(path):
    d = load(path)
    req = required(d)
    res = {"fail": [], "undecided": [], "n": 0, "per_test": {}}
    for (t, k, f) in req:
        if t not in d or k not in d[t]: res["fail"].append((t, k, "MISSING")); continue
        v = judge(d[t][k], f); res["n"] += 1
        pt = res["per_test"].setdefault(t, {"n": 0, "ok": 0}); pt["n"] += 1
        if v is True: pt["ok"] += 1
        elif v is False: res["fail"].append((t, k, "NOT CONTAINED"))
        else: res["undecided"].append((t, k))
    # fired control (i): collapse to the upper endpoint
    coll = {"n": 0, "rejected": 0, "exact_upper": 0, "per_test": {}}
    for (t, k, f) in req:
        if t not in d or k not in d[t]: continue
        hi = d[t][k][1]
        v = judge((hi, hi), f); coll["n"] += 1
        c = coll["per_test"].setdefault(t, 0)
        if v is False: coll["rejected"] += 1; coll["per_test"][t] = c + 1
        elif v is True: coll["exact_upper"] += 1
    # fired control (ii): wrong p must EXCLUDE the true trace
    ctrl2 = None
    if "CTRL_wrong_p" in d:
        with ctx.workprec(1024):
            r1, r2 = arb(1) / 3, -arb(1) / 4
            trx = (2 * acb.pi() * 1j * r1).exp() + (2 * acb.pi() * 1j * r2).exp()
        ex_re = inside(d["CTRL_wrong_p"]["trre"], trx.real) is False
        ex_im = inside(d["CTRL_wrong_p"]["trim"], trx.imag) is False
        ctrl2 = bool(ex_re or ex_im)
    tests_all_reject = all(coll["per_test"].get(t, 0) >= 1 for t in res["per_test"])
    frac = coll["rejected"] / max(1, coll["n"] - coll["exact_upper"])
    verdict = ("PASS" if not res["fail"] and not res["undecided"] and tests_all_reject and frac >= 0.9 and ctrl2
               else "FAIL")
    summary = dict(verdict=verdict, values_checked=res["n"], failures=res["fail"], undecided=res["undecided"],
                   per_test=res["per_test"], collapse_control=dict(n=coll["n"], rejected=coll["rejected"],
                   exact_upper=coll["exact_upper"], fraction=round(frac, 4), every_test_rejected=tests_all_reject,
                   per_test=coll["per_test"]), wrong_equation_control_excludes_true_trace=ctrl2,
                   tests_present=sorted(d))
    print(json.dumps(summary, indent=1, default=str))
    return summary

if __name__ == "__main__":
    s = main(sys.argv[1] if len(sys.argv) > 1 else HERE / "tests" / "odectl.out")
    json.dump(s, open(HERE / "ode_controls_result.json", "w"), indent=1, default=str)
