"""Tier 2a comparison (TIER2A_PREREG.md). Written BEFORE the independent module was seen. Claude Opus 5.5 (Quantum).
Runs the FROZEN indep/mn_indep.py (its sha must match indep/FREEZE.txt) at the registered points, and compares it with:
  (1) the S2 header gen/mn_field.h (hdr_eval_true, MPFR-160 intervals) at beta in {0, 3/100, -3/100}: H, f0..f3, V;
  (2) mel_gen.H0 (beta = 0) and mel_gen.Hb (d/dbeta at 0);
must-fail: (mf1) the sab header at 3/100 must disagree; (mf2) indep with L -> 1.001 L must disagree on H, V, f2, f3.
Tolerance: |indep - ref| <= rad(ref) + 1e-20 * S_c, S_c = max over points |ref_c| (per component, per beta)."""
import hashlib, importlib.util, json, os, re, subprocess, sys
from fractions import Fraction
import mpmath as mp
HERE = os.path.dirname(os.path.abspath(__file__)); IND = os.path.join(HERE, "indep")
mp.mp.dps = 60
TOL = mp.mpf("1e-20")
E_S, L_S = "0.93528150456799871854", "12.972532035607280691"
BETAS = {"0": "0", "+3/100": "3/100", "-3/100": "-3/100"}


def qstr(s):
    f = Fraction(s); return "%d/%d" % (f.numerator, f.denominator)


def load_points():
    P = []
    for ln in open(os.path.join(HERE, "points.txt")):
        p = ln.split(); P.append((p[0], p[1:5]))
    return P


def hexq(h):
    """MPFR %Ra hex -> mpf (exact at dps 60 for 160-bit mantissas? 160 bits ~ 48 digits: exact enough)"""
    neg = h.startswith("-"); h = h.lstrip("+-")
    m = re.fullmatch(r"0x([0-9a-f]*)\.?([0-9a-f]*)p([+-]?\d+)", h)
    ip, fp, ex = m.group(1) or "0", m.group(2), int(m.group(3))
    v = mp.mpf(int(ip + fp, 16)) * mp.mpf(2) ** (ex - 4 * len(fp))
    return -v if neg else v


def header(binary, beta, pts, alpha="-1/3", L=L_S):
    inp = "4 %s %s %s %s\n" % (alpha, qstr(beta), qstr(E_S), qstr(L))
    inp += "".join(" ".join(qstr(v) for v in p) + "\n" for _, p in pts)
    out = subprocess.run([os.path.join(HERE, binary)], input=inp, capture_output=True, text=True, check=True).stdout
    res, cur = [], {}
    for ln in out.splitlines():
        if ln == "END": res.append(cur); cur = {}; continue
        tag, lo, hi = ln.split(); lo, hi = hexq(lo), hexq(hi)
        if not (mp.isfinite(lo) and mp.isfinite(hi)): raise SystemExit("non-finite header enclosure")
        cur[tag] = ((lo + hi) / 2, (hi - lo) / 2)
    return res


def load_indep():
    src = os.path.join(IND, "mn_indep.py"); sha = hashlib.sha256(open(src, "rb").read()).hexdigest()
    frz = open(os.path.join(IND, "FREEZE.txt")).read()
    if sha not in frz: raise SystemExit("mn_indep.py sha %s not in FREEZE.txt" % sha)
    spec = importlib.util.spec_from_file_location("mn_indep", src); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m, sha


def indep_vals(M, beta, pts, L=L_S):
    out = []
    for _, p in pts:
        x, y, px, py = (mp.mpf(Fraction(v).numerator) / Fraction(v).denominator for v in p)
        b = mp.mpf(Fraction(beta).numerator) / Fraction(beta).denominator
        H = M.H(x, y, px, py, b, mp.mpf(E_S), mp.mpf(L)); f = M.field(x, y, px, py, b, mp.mpf(E_S), mp.mpf(L))
        V = M.H(x, y, 0, 0, b, mp.mpf(E_S), mp.mpf(L))
        out.append(dict(H=mp.mpf(H), V=mp.mpf(V), f0=mp.mpf(f[0]), f1=mp.mpf(f[1]), f2=mp.mpf(f[2]), f3=mp.mpf(f[3])))
    return out


def compare(ind, ref, comps):
    rep = {}
    for c in comps:
        S = max(abs(r[c][0]) for r in ref); worst = mp.mpf(0); nbad = 0
        for a, r in zip(ind, ref):
            d = abs(a[c] - r[c][0]); lim = r[c][1] + TOL * S
            worst = max(worst, d / S if S else d)
            if d > lim: nbad += 1
        rep[c] = dict(S=mp.nstr(S, 6), worst_rel=mp.nstr(worst, 4), n_outside=nbad, ok=(nbad == 0))
    return rep


def main():
    M, sha = load_indep(); pts = load_points(); R = dict(indep_sha=sha, n_points=len(pts), tol="1e-20 x S_c")
    comps = ["H", "V", "f0", "f1", "f2", "f3"]
    R["vs_header"] = {}
    for nm, b in BETAS.items():
        R["vs_header"][nm] = compare(indep_vals(M, b, pts), header("hdr_eval_true", b, pts), comps)
    # (2) Melnikov module
    sys.path.insert(0, os.path.join(HERE, "..", "..", "mn_melnikov")); import mel_gen as MG
    from flint import acb, arb, ctx
    ctx.prec = 200
    def m2mp(z): return mp.mpf(z.real.mid().str(55, radius=False))
    def rad(z): return mp.mpf(float(z.real.rad()))
    h0, hb, i0, ib = [], [], [], []
    for _, p in pts:
        xs, ys, pxs, pys = p
        fx, fy, fpx, fpy = (Fraction(v) for v in p)
        ax, ay = acb(arb(fx.numerator) / fx.denominator), acb(arb(fy.numerator) / fy.denominator)
        apx2, apy2 = acb(arb(fpx.numerator) / fpx.denominator) ** 2, acb(arb(fpy.numerator) / fpy.denominator) ** 2
        aE, aL = acb(arb(E_S)), acb(arb(L_S))
        v0, vb = MG.H0(ax, ay, apx2, apy2, aE, aL), MG.Hb(ax, ay, apx2, apy2, aE, aL)
        h0.append(dict(H=(m2mp(v0), rad(v0)))); hb.append(dict(H=(m2mp(vb), rad(vb))))
        X = [mp.mpf(f.numerator) / f.denominator for f in (fx, fy, fpx, fpy)]
        i0.append(dict(H=mp.mpf(M.H(*X, 0, mp.mpf(E_S), mp.mpf(L_S))))); ib.append(dict(H=mp.mpf(M.dH_dbeta(*X, mp.mpf(E_S), mp.mpf(L_S)))))
    R["vs_mel_gen"] = dict(H0=compare(i0, h0, ["H"]), Hb=compare(ib, hb, ["H"]))
    # must-fail
    R["mf1_sab_header"] = compare(indep_vals(M, "3/100", pts), header("hdr_eval_sab", "3/100", pts), comps)
    Lm = str(mp.mpf(L_S) * mp.mpf("1.001"))
    R["mf2_L_mutation"] = compare(indep_vals(M, "3/100", pts, L=Lm), header("hdr_eval_true", "3/100", pts), ["H", "V", "f2", "f3"])
    ok_main = all(v["ok"] for b in R["vs_header"].values() for v in b.values()) and all(v["H"]["ok"] for v in R["vs_mel_gen"].values())
    mf1 = any(not v["ok"] for v in R["mf1_sab_header"].values()); mf2 = all(not v["ok"] for v in R["mf2_L_mutation"].values())
    R["must_fail_fired"] = dict(mf1=mf1, mf2=mf2)
    R["VERDICT"] = "AGREE" if (ok_main and mf1 and mf2) else ("INVALID" if not (mf1 and mf2) else "DISAGREEMENT (classify: convention test next)")
    json.dump(R, open(os.path.join(HERE, "compare_result.json"), "w"), indent=1, default=str)
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    main()
