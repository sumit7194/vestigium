"""
iahub v2 validation ladder (PREREG_iahub_v2.md §6, registered 33321aa). Each rung is a guarded child.

  VG0       known-monodromy tests through the native core: reduced Riemann P (1/3,1/5,1/7) as a first-order
            system (exact traces -2cos(pi/3), -2cos(pi/5)); non-reduced Gauss hypergeometric (exact traces and
            dets); exp(2/x^3) pullback near an essential singularity. Every exact value enclosed, >= 10 digits.
  VCTRL     ZV delta=2 equatorial (1,0,4),(1,0,9): certificate MUST be found AND replayed by v1;
            Kerr equatorial p1,p2 x (1,0,4),(1,0,9),(1,1,4) and Kerr axial p1,p2 x (1,4),(1,9): MUST NOT;
            ZV axial (1,4): info.
  VREPRO    the proven axial MN rows (2ce8b41) -- p1,p2 x (1,4),(1,9): certificate MUST be found by v2 AND
            replayed by v1.
Usage: python mr_v2_ladder.py <RUNG>        |   python mr_v2_ladder.py --one <RUNG> out.json
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def rung_vg0():
    import sympy as sp
    import ia_native as IN, ia_hub as IA
    from flint import acb, arb
    z = sp.Symbol("z"); R = sp.Rational
    out = {}
    def e2pi(q):
        return (acb(0, 1)*2*arb.pi()*arb(int(q.p))/int(q.q)).exp()
    def cos_pi(q):
        return (arb.pi()*arb(int(q.p))/int(q.q)).cos()
    def entries(b, P, Q):          # system for y'' + P y' + Q y = 0
        zero, one = b.const(0), b.const(1)
        pn, pd = sp.fraction(sp.together(-P)); qn, qd = sp.fraction(sp.together(-Q))
        return [[(zero, one), (one, one)], [(b.expr(qn, z), b.expr(qd, z)), (b.expr(pn, z), b.expr(pd, z))]]
    def rec(name, M, exp_tr, exp_det=None, steps=None):
        t = IN.tr(M); ok = bool(t.contains(exp_tr))
        if exp_det is not None:
            ok = ok and bool(IN.det(M).contains(exp_det))
        out[name] = dict(trace=str(t), expected=str(exp_tr), contains=ok, digits=IA.radius_digits(t), steps=steps)
    # reduced Riemann P (1/3, 1/5, 1/7): y'' = r y  ->  P = 0, Q = -r
    lam, mu, nu = R(1, 3), R(1, 5), R(1, 7)
    r = ((lam**2 - 1)/(4*z**2) + (mu**2 - 1)/(4*(z - 1)**2) - (lam**2 + mu**2 - nu**2 - 1)/(4*z*(z - 1)))
    b = IN.SLPBuilder()
    ent = entries(b, sp.Integer(0), -r)
    res = IN.run_job(IN.write_job(b, ent, [("P0", IA.loop_points(0.5 + 0.5j, 0, 0.25)),
                                           ("P1", IA.loop_points(0.5 + 0.5j, 1, 0.25))], obst=[0, 1], threads=2))
    rec("Riemann P reduced, around 0", res["P0"]["M"], -2*cos_pi(lam), steps=res["P0"]["steps"])
    rec("Riemann P reduced, around 1", res["P1"]["M"], -2*cos_pi(mu), steps=res["P1"]["steps"])
    # non-reduced Gauss hypergeometric
    a_, b_, c_ = R(1, 5), R(1, 7), R(1, 3)
    P = (c_ - (a_ + b_ + 1)*z)/(z*(1 - z)); Q = -a_*b_/(z*(1 - z))
    b2 = IN.SLPBuilder(); ent2 = entries(b2, P, Q)
    res = IN.run_job(IN.write_job(b2, ent2, [("H0", IA.loop_points(0.5 + 0.5j, 0, 0.25)),
                                             ("H1", IA.loop_points(0.5 + 0.5j, 1, 0.25))], obst=[0, 1], threads=2))
    rec("hypergeometric non-reduced, around 0", res["H0"]["M"], 1 + e2pi(1 - c_), e2pi(1 - c_), res["H0"]["steps"])
    rec("hypergeometric non-reduced, around 1", res["H1"]["M"], 1 + e2pi(c_ - a_ - b_), e2pi(c_ - a_ - b_), res["H1"]["steps"])
    # exp pullback w = exp(2/x^3)
    w = sp.exp(2/z**3); wp = sp.diff(w, z); lp = sp.simplify(sp.diff(wp, z)/wp)
    Pw = -lp + wp*P.subs(z, w); Qw = wp**2*Q.subs(z, w)
    b3 = IN.SLPBuilder(); ent3 = entries(b3, Pw, Qw)
    x1 = complex(sp.N((-sp.I/sp.pi)**R(1, 3), 30))
    res = IN.run_job(IN.write_job(b3, ent3, [("X1", IA.loop_points(x1 + 0.01, x1, 0.01, ngon=32))], bad=[0],
                                  obst=[x1], hmax=0.004, threads=1))
    rec("exp(2/x^3) pullback, around an E=1 root", res["X1"]["M"], 1 + e2pi(c_ - a_ - b_), steps=res["X1"]["steps"])
    out["PASS"] = all(v["contains"] and v["digits"] >= 10 for v in out.values() if isinstance(v, dict))
    return out


def _row(S, expect, replay):
    import mr_v2 as V
    t0 = time.time()
    sing = V.locate(S)
    r = V.search(S, sing, log=lambda m: print(m, flush=True))
    r["located"] = [str(complex(round(c.real, 6), round(c.imag, 6))) for c in sing]
    if r["found"] and replay:
        r["v1_replay"] = V.replay_v1(S, r, sing)
    found = r["found"]
    rep = r.get("v1_replay", {}).get("replayed")
    if expect == "find":
        r["assessment"] = "PASS" if (found and rep) else f"FAIL (found={found}, v1 replay={rep})"
    elif expect == "none":
        r["assessment"] = "PASS" if not found else "FAIL (certificate FOUND on an integrable control)"
    else:
        r["assessment"] = f"INFO (found={found}, v1 replay={rep})"
    r["seconds"] = round(time.time() - t0, 1)
    r.pop("geometry", None) if not found else None
    return r


def rows(rung):
    import mr_v2 as V
    L = []
    if rung == "VCTRL":
        for En, Lz, mu2 in ((1, 0, 4), (1, 0, 9)):
            L.append((f"ZV eq ({En},{Lz},{mu2})", lambda En=En, Lz=Lz, mu2=mu2: V.system_equatorial("zv", None, En, Lz, mu2), "find"))
        for pt in ("p1", "p2"):
            for En, Lz, mu2 in ((1, 0, 4), (1, 0, 9), (1, 1, 4)):
                L.append((f"Kerr {pt} eq ({En},{Lz},{mu2})", lambda pt=pt, En=En, Lz=Lz, mu2=mu2: V.system_equatorial("kerr", pt, En, Lz, mu2), "none"))
            for En, mu2 in ((1, 4), (1, 9)):
                L.append((f"Kerr {pt} axial ({En},{mu2})", lambda pt=pt, En=En, mu2=mu2: V.system_axial("kerr", pt, En, mu2), "none"))
        L.append(("ZV axial (1,4)", lambda: V.system_axial("zv", None, 1, 4), "info"))
    elif rung == "VREPRO":
        for pt in ("p1", "p2"):
            for En, mu2 in ((1, 4), (1, 9)):
                L.append((f"MN {pt} axial ({En},{mu2})", lambda pt=pt, En=En, mu2=mu2: V.system_axial("mn", pt, En, mu2), "find"))
    return L


def run_rung(rung):
    import mr_watchdog as W
    py = sys.executable
    if rung == "VG0":
        outp = os.path.join(HERE, "mr_v2_VG0.json")
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", "VG0", outp], mem_limit_mb=2048,
                          time_limit_s=3600, cwd=HERE, log=os.path.join(HERE, "mr_v2_VG0.log"))
        res = json.load(open(outp)) if g["status"] == "ok" else dict(PASS=False, failed=g["status"])
        res["guard"] = g
        json.dump(res, open(outp, "w"), indent=1, default=str)
        print(json.dumps(res, indent=1, default=str), flush=True)
        return res
    allres = []
    for i, (name, build, expect) in enumerate(rows(rung)):
        outp = os.path.join(HERE, f"mr_v2_{rung}_row{i}.json")
        if os.path.exists(outp):
            os.remove(outp)
        g = W.run_guarded([py, "-u", os.path.abspath(__file__), "--one", f"{rung}:{i}", outp], mem_limit_mb=2048,
                          time_limit_s=10800, cwd=HERE, log=os.path.join(HERE, f"mr_v2_{rung}_row{i}.log"))
        res = json.load(open(outp)) if (g["status"] == "ok" and os.path.exists(outp)) else \
            dict(found=None, assessment=f"FAIL (guard: {g['status']})" if expect != "info" else f"INFO (guard: {g['status']})")
        res.update(name=name, expect=expect, guard=g)
        allres.append(res)
        print(f"{i:>2} {rung} {name:<26} => {res['assessment']:<40} [guard {g['status']}, peak {g['peak_mb']} MB, {g['seconds']} s]", flush=True)
        json.dump(allres, open(os.path.join(HERE, f"mr_v2_{rung}.json"), "w"), indent=1, default=str)
    ok = all(r["assessment"].startswith(("PASS", "INFO")) for r in allres)
    print(f"{rung} {'PASS' if ok else 'FAIL'}", flush=True)
    return allres


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--one":
        task, outp = sys.argv[2], sys.argv[3]
        if task == "VG0":
            res = rung_vg0()
        else:
            rung, i = task.split(":")
            name, build, expect = rows(rung)[int(i)]
            res = _row(build(), expect, replay=(expect in ("find", "info")))
        json.dump(res, open(outp, "w"), indent=1, default=str)
    else:
        run_rung(sys.argv[1])
