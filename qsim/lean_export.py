"""Item 2 (PREREG_lean_certificate_arithmetic.md, 344400c): regenerate certifying loops with the frozen code and export
the g, h boxes as exact dyadic rationals for the Lean kernel check.

Gate: the regenerated certificate quantities must reproduce the RECORDED midrad strings exactly (bit-for-bit);
otherwise nothing is exported for that certificate.

Usage:  python lean_export.py <family> <row> <v1|v2>
  families: ts2 (PREREG_ts2_v2 rows 0-5), tschaos (PREREG_ts2_chaos_levels rows 0-7),
            mneq (PREREG_mn_equatorial_v2 rows 0-5), mnaxv2 (VREPRO ladder rows 0-3)
"""
import json, os, sys, time
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OUTDIR = os.path.join(os.path.dirname(HERE), "lean_export")


# ---------------------------------------------------------------------------------------------- sources
def source(family, row):
    """-> (S, sing, v2cert dict, v1 record dict, v1 N, kerr_or_target tag)"""
    import mr_v2 as V
    if family == "ts2":
        import mr_v2_ts2 as T
        P, (En, L, mu2) = T.ROWS[row]
        S, _ = T.system(P, En, L, mu2)
        d = json.load(open(os.path.join(HERE, f"mr_v2_ts2_row{row}.json")))
        return S, V.locate_a6(S), d, d["v1_replay"], 100
    if family == "tschaos":
        import mr_ts2_chaos as C
        name, key, p, (En, L, mu2), kind = C.ROWS[row]
        S, _ = C.system(key, En, L, mu2)
        b = json.load(open(os.path.join(HERE, f"mr_ts2_chaos_row{row}.json")))["route_b"]
        N = int(max(b["v1_replay_by_N"], key=int))
        return S, V.locate_a6(S), b, b["v1_replay"], N
    if family == "mneq":
        import mr_v2_mneq as M
        p, (En, L, mu2) = M.ROWS[row]
        S = V.system_equatorial("mn", p, En, L, mu2)
        if row in (0, 3):                                    # frozen-policy rows: V.locate, plain row file
            d = json.load(open(os.path.join(HERE, f"mr_v2_mneq_row{row}.json")))
            return S, V.locate(S), d, d["v1_replay"], 100
        d = json.load(open(os.path.join(HERE, f"mr_v2_mneq_row{row}_a6.json")))
        v1 = d["v1_replay"]
        return S, V.locate_a6(S), d, v1, int(v1.get("N", 100))
    if family == "mnaxv2":
        import mr_v2_ladder as LD
        name, build, expect = LD.rows("VREPRO")[row]
        S = build()
        d = json.load(open(os.path.join(HERE, f"mr_v2_VREPRO_row{row}.json")))
        return S, V.locate(S), d, d["v1_replay"], 100
    raise ValueError(family)


# ---------------------------------------------------------------------------------------------- exact boxes
def _arb_rect(a):
    """arb ball -> (lo, hi) exact Fractions with [lo, hi] = [mid - rad, mid + rad] (contains the ball exactly)."""
    m, e = a.mid().man_exp(); rm, re_ = a.rad().man_exp()
    two = Fraction(2)
    mid = Fraction(int(m)) * two ** int(e)
    rad = Fraction(int(rm)) * two ** int(re_)
    return mid - rad, mid + rad


def box(Y):
    return [[{"re": [str(q) for q in _arb_rect(Y[i][j].real)], "im": [str(q) for q in _arb_rect(Y[i][j].imag)]}
             for j in range(2)] for i in range(2)]


def readback_ok(Y, B):
    """Committed cross-check: each original ball lies inside its exported rectangle."""
    from flint import arb
    for i in range(2):
        for j in range(2):
            for part, a in (("re", Y[i][j].real), ("im", Y[i][j].imag)):
                lo, hi = (Fraction(s) for s in B[i][j][part])
                lo_a = arb(lo.numerator) / arb(lo.denominator)
                hi_a = arb(hi.numerator) / arb(hi.denominator)
                if not (bool((a - lo_a) >= 0) and bool((hi_a - a) >= 0)):
                    return False
    return True


# ---------------------------------------------------------------------------------------------- regeneration
def _compose(word, cache, mul):
    parts = word.split("*")
    Y = cache[parts[0]]
    for p_ in parts[1:]:
        Y = mul(Y, cache[p_])
    return Y


def regen_v2(S, sing, d):
    import mr_v2 as V, ia_native as IN, ia_hub as IA
    b, entries = V.compile_system(S)
    obst = list(sing) + [complex(c) for c in S["bad"]]
    names = sorted(set(d["g"].split("*") + d["h"].split("*")))
    geo = d["geometry"]
    loops = [(n, IA.loop_points(complex(*geo[n]["base"]), complex(*geo[n]["center"]), geo[n]["radius"])) for n in names]
    job = IN.write_job(b, entries, loops, bad=S["bad"], obst=obst, threads=min(3, len(loops)))
    res = IN.run_job(job); os.remove(job)
    cache = {n: res[n]["M"] for n in names}
    g, h = _compose(d["g"], cache, IN.matmul), _compose(d["h"], cache, IN.matmul)
    ok, info = IN.certificate_gl2(g, h)
    rec = {k: d[k] for k in ("w_g_midrad", "w_h_midrad", "tr_comm_midrad")}
    new = {k: info[k] for k in rec}
    return g, h, ok, rec, new


def regen_v1(S, sing, d, v1rec, N):
    import mr_v2 as V, ia_hub as IA, ia_native as IN, multiprocessing as mpr
    r1 = S["reduced"]()
    rc = IA.RationalFn(S["to_expr"](r1, "P"), S["to_expr"](r1, "Q"), S["var"], S["bad"])
    obst = list(sing) + [complex(c) for c in S["bad"]]
    dmin = lambda q: min(abs(q - c) for c in obst)
    names = sorted(set(d["g"].split("*") + d["h"].split("*")))
    V._RCTX.update(rc=rc, dmin=dmin, geo=d["geometry"], N=N)
    with mpr.get_context("fork").Pool(processes=min(3, len(names))) as pool:
        got = dict(pool.map(V._replay_worker, names))
    cache = {n: [[V._de_ball(got[n][i][j]) for j in range(2)] for i in range(2)] for n in names}
    g, h = _compose(d["g"], cache, IA._matmul), _compose(d["h"], cache, IA._matmul)
    ok, info = IA.certificate(g, h)
    c = IA.tr(IA._matmul(IA._matmul(g, h), IA._matmul(IA.inv(g), IA.inv(h))))
    new = dict(tr_g_midrad=IN.midrad(IA.tr(g)), tr_h_midrad=IN.midrad(IA.tr(h)), tr_comm_midrad=IN.midrad(c))
    rec = {k: v1rec[k] for k in new}
    return g, h, ok, rec, new


def regen_kerr(S, sing, b):
    """Integrable control: the first two recorded Kerr generators (no certificate exists). Gate: their tr^2/det
    strings reproduce the recorded generator_w exactly."""
    import mr_v2 as V, ia_native as IN, ia_hub as IA
    bb, entries = V.compile_system(S)
    obst = list(sing) + [complex(c) for c in S["bad"]]
    names = list(b["generator_w"])[:2]
    geo = b["geometry"]
    loops = [(n, IA.loop_points(complex(*geo[n]["base"]), complex(*geo[n]["center"]), geo[n]["radius"])) for n in names]
    job = IN.write_job(bb, entries, loops, bad=S["bad"], obst=obst, threads=2)
    res = IN.run_job(job); os.remove(job)
    g, h = res[names[0]]["M"], res[names[1]]["M"]
    rec = {n: b["generator_w"][n] for n in names}
    new = {n: str(IN.tr(res[n]["M"])**2/IN.det(res[n]["M"])) for n in names}
    return g, h, names, rec, new


def run(family, row, which):
    t0 = time.time()
    if family == "kerrctl":                                  # tschaos control rows 8, 9 (Kerr-WP)
        import mr_ts2_chaos as C, mr_v2 as V
        name, key, p, (En, L, mu2), kind = C.ROWS[row]
        S, _ = C.system(key, En, L, mu2)
        b = json.load(open(os.path.join(HERE, f"mr_ts2_chaos_row{row}.json")))["route_b"]
        g, h, names, rec, new = regen_kerr(S, V.locate_a6(S), b)
        out = dict(family=family, row=row, which="v2", N=140, g_word=names[0], h_word=names[1], certificate_ok=False,
                   control="integrable Kerr: check must be FALSE", gate_bit_for_bit=(rec == new), recorded=rec,
                   regenerated=new, seconds=round(time.time() - t0, 1))
        if rec == new:
            Bg, Bh = box(g), box(h)
            out.update(readback=(readback_ok(g, Bg) and readback_ok(h, Bh)), G=Bg, H=Bh)
        os.makedirs(OUTDIR, exist_ok=True)
        json.dump(out, open(os.path.join(OUTDIR, f"kerrctl_{row}_v2.json"), "w"), indent=1)
        print(f"kerrctl row {row}: bit_for_bit={rec == new} readback={out.get('readback')} [{out['seconds']} s]", flush=True)
        return out
    S, sing, d, v1rec, N = source(family, row)
    if which == "v2":
        g, h, ok, rec, new = regen_v2(S, sing, d)
    else:
        g, h, ok, rec, new = regen_v1(S, sing, d, v1rec, N)
    gate = (rec == new) and ok
    out = dict(family=family, row=row, which=which, N=(N if which == "v1" else 140), g_word=d["g"], h_word=d["h"],
               certificate_ok=bool(ok), gate_bit_for_bit=(rec == new), recorded=rec, regenerated=new,
               seconds=round(time.time() - t0, 1))
    if gate:
        Bg, Bh = box(g), box(h)
        out.update(readback=(readback_ok(g, Bg) and readback_ok(h, Bh)), G=Bg, H=Bh)
    os.makedirs(OUTDIR, exist_ok=True)
    fn = os.path.join(OUTDIR, f"{family}_{row}_{which}.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"{family} row {row} {which}: certificate_ok={ok} bit_for_bit={rec == new} "
          f"readback={out.get('readback')} [{out['seconds']} s]", flush=True)
    if rec != new:
        print("  recorded  :", rec, "\n  regenerated:", new, flush=True)
    return out


if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]), sys.argv[3])
