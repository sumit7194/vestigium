"""Codegen gate (registered with the MN/Kerr CAPD field): every function in gen/mn_field.h, evaluated by C++ on MPFR
intervals (tests/cg_eval.cpp, 160 bits) at random exact points, must ENCLOSE the 80-digit mpmath value of the same
sympy expression (mn_codegen.build). Cases: F5-R and its Kerr limit at the A-K20 level, and Kerr at the B15 level.
Mutation control: the reference with L -> 1.001 L must be OUTSIDE the enclosure for every output that depends on L
(the forces f2, f3, and H, V; f0 = g^xx p_x and f1 = g^yy p_y do not depend on L). [Criterion corrected 2026-10-20: the
first draft wrongly expected f0, f1 to move as well.]"""
import json, random, subprocess, sys
from fractions import Fraction as F
from pathlib import Path
import sympy as sp, mpmath as mp
import mn_codegen as CG
HERE = Path(__file__).resolve().parent
mp.mp.dps = 80
CASES = {"F5R": ("39", "-5/8", "13394411/1186380", "19/20", "267"), "F5R_KERR": ("39", "-5/8", "0", "19/20", "267"),
         "B15_KERR": ("39", "-5/8", "0", "49/50", "445/2")}


def main(npts=8, seed=20261020):
    X = CG.build()
    names = ["f0", "f1", "f2", "f3", "H", "gpp", "B", "gxx", "gyy", "V"]
    exprs = X["field"] + [X["H"], X["gpp"], X["B"], X["gxx"], X["gyy"], X["V"]]
    syms = (CG.x, CG.y, CG.PX, CG.PY, CG.k, CG.al, CG.beta, CG.E, CG.L)
    fns = [sp.lambdify(syms, e, "mpmath") for e in exprs]
    rnd = random.Random(seed); out = {}
    for tag, cs in CASES.items():
        pts = [(F(rnd.randint(2000, 6000), 1000), F(rnd.randint(-400, 400), 1000), F(rnd.randint(-5000, 5000), 100),
                F(rnd.randint(-5000, 5000), 100)) for _ in range(npts)]
        inp = " ".join(cs) + "\n" + "\n".join(" ".join(str(v) for v in p) for p in pts) + "\n"
        r = subprocess.run([str(HERE / "tests" / "cg_eval")], input=inp, capture_output=True, text=True, check=True)
        blocks = r.stdout.strip().split("END")
        cv = [mp.mpf(F(s).numerator) / F(s).denominator for s in cs]
        ok, mut_out, worst_w = True, 0, 0.0
        for p, blk in zip(pts, blocks):
            enc = {ln.split()[0]: (mp.mpf(float.fromhex(ln.split()[1])) if False else mp.mpf(ln.split()[1]) if not ln.split()[1].startswith(("0x", "-0x")) else _hx(ln.split()[1]),
                                   _hx(ln.split()[2])) for ln in blk.strip().splitlines()}
            pv = [mp.mpf(v.numerator) / v.denominator for v in p]
            for nm, fn in zip(names, fns):
                ref = fn(*pv, *cv); lo, hi = enc[nm]
                if not (lo <= ref <= hi): ok = False; print("NOT ENCLOSED", tag, nm, p, ref, lo, hi)
                worst_w = max(worst_w, float((hi - lo) / max(abs(ref), mp.mpf(10)**-40)))
            cm = list(cv); cm[4] = cv[4] * mp.mpf("1.001")
            for nm, fn in [(n, f) for n, f in zip(names, fns) if n in ("f2", "f3", "H", "V")]:
                ref = fn(*pv, *cm); lo, hi = enc[nm]
                if not (lo <= ref <= hi): mut_out += 1
        out[tag] = dict(all_enclosed=ok, worst_rel_width=worst_w, mutation_outside=f"{mut_out}/{4 * npts}",
                        PASS=ok and mut_out == 4 * npts)
        print(tag, out[tag], flush=True)
    out["GATE"] = all(v["PASS"] for v in out.values())
    (HERE / "mn_codegen_gate.json").write_text(json.dumps(out, indent=1)); print("CODEGEN GATE", "PASS" if out["GATE"] else "FAIL")
    return 0 if out["GATE"] else 1


def _hx(s):
    """exact value of an MPFR %Ra hex string (sign, 0x mantissa, p exponent)"""
    neg = s.startswith("-"); s = s.lstrip("-")
    if s in ("0", "0x0p+0"): return mp.mpf(0)
    mant, ex = s[2:].split("p"); ip, _, fp = mant.partition(".")
    val = mp.mpf(int(ip + fp, 16)) * mp.mpf(2) ** (int(ex) - 4 * len(fp))
    return -val if neg else val


if __name__ == "__main__":
    sys.exit(main())
