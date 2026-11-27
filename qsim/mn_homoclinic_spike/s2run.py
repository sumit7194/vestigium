"""S2 driver (PREREG.md A1-A11). Float guesses and approximate inverses only; every decision is made by capd/s2_main
(MPFR intervals). Per-stage checkpoints in s2/<label>/ (a finished stage's .json is not redone).
Usage: python s2run.py <label> <field true|sab> <beta>          (fp -> cone -> bvp)
       python s2run.py meet <label_of_beta0_run>                 (control ii, reuses that run's fp and cone)
Written by Claude Opus 5.5 (Quantum), 2026-11-27."""
import sys, os, json, time, subprocess, re, numpy as np, mpmath as mp
import s1, s2f
mp.mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__)); CAPD = os.path.join(HERE, "capd")
DELTA = "1e-9"; KSHIFT = 4; RMIN = "1e-19"


def d17(v): return repr(float(v))
def d40(v): return mp.nstr(mp.mpf(v), 40, min_fixed=-mp.inf, max_fixed=mp.inf) if not isinstance(v, str) else v


def flow_for(field, beta):
    if field == "sab":
        orig = s1.G.mine; s1.G.mine = s2f.mine_sab
        try: return s1.flow(beta)
        finally: s1.G.mine = orig
    return s1.flow(beta)


def run(binname, mode, spec, out):
    with open(spec) as fh: pass
    t0 = time.time()
    r = subprocess.run([os.path.join(CAPD, binname), mode, spec], capture_output=True, text=True)
    open(out, "w").write(r.stdout + ("\nSTDERR\n" + r.stderr if r.stderr.strip() else ""))
    print("  %s %s rc %d (%.0f s)" % (mode, os.path.basename(spec), r.returncode, time.time() - t0), flush=True)
    if r.returncode not in (0, 3): raise RuntimeError("s2_main failed: " + r.stdout[-500:])
    return r.stdout, r.returncode


def mids(txt, tag):
    vals = {}
    for m_ in re.finditer(r"^%s\[(\d+)\](?:\[(\d+)\])? \[(\S+),(\S+)\] mid (\S+)$" % re.escape(tag), txt, re.M):
        key = int(m_.group(1)) if m_.group(2) is None else (int(m_.group(1)), int(m_.group(2)))
        vals[key] = (m_.group(3), m_.group(4), m_.group(5))
    return vals


def writespec(fn, d):
    with open(fn, "w") as fh:
        for k, v in d.items():
            fh.write(k + " " + " ".join(v if isinstance(v, (list, tuple)) else [v]) + "\n")


def base(beta): return dict(beta=beta_str(beta), prec="128", order="20", tol="1e-24", rmin=RMIN)
def beta_str(beta): return {0.0: "0", 0.03: "3/100"}[beta]


def stage_fp(D, binname, f, beta):
    js = os.path.join(D, "fp.json")
    if os.path.exists(js): return json.load(open(js))
    fp, err, lam, vu, vs, J, T = s1.fixed_point(f)
    A = np.linalg.inv(J - np.eye(2)); Ts = T - 2.0
    sp = dict(base(beta), Tstop=d17(Ts), w=[d17(fp[0]), d17(fp[1])], A=[d17(a) for a in A.ravel()])
    writespec(os.path.join(D, "fp_pt.spec"), dict(sp, pointonly="1"))
    txt, _ = run(binname, "fp", os.path.join(D, "fp_pt.spec"), os.path.join(D, "fp_pt.out"))
    F = mids(txt, "F"); Fv = [mp.mpf(F[i][2]) for i in range(2)]
    w = [mp.mpf(d17(fp[0])), mp.mpf(d17(fp[1]))]
    w2 = [w[i] - sum(mp.mpf(d17(A[i][j])) * Fv[j] for j in range(2)) for i in range(2)]
    sp["w"] = [d40(w2[0]), d40(w2[1])]
    writespec(os.path.join(D, "fp.spec"), sp)
    txt, rc = run(binname, "fp", os.path.join(D, "fp.spec"), os.path.join(D, "fp.out"))
    res = re.search(r"^RESULT fp (\S+) rho (\S+)", txt, re.M)
    DP = mids(txt, "DPfp"); DPm = np.array([[float(DP[(i, j)][2]) for j in range(2)] for i in range(2)])
    ev, V = np.linalg.eig(DPm); iu = int(np.argmax(np.abs(ev)))
    u = np.real(V[:, iu]); s = np.real(V[:, 1 - iu]); u = u / np.linalg.norm(u) * np.sign(u[0]); s = s / np.linalg.norm(s) * np.sign(s[0])
    out = dict(result=res.group(1), rho=res.group(2), w=sp["w"], Tstop=sp["Tstop"], u=[d17(u[0]), d17(u[1])], s=[d17(s[0]), d17(s[1])],
               lam=float(np.real(ev[iu])), float_fp=[float(fp[0]), float(fp[1])], float_vu=list(map(float, vu)), float_vs=list(map(float, vs)), T=float(T))
    json.dump(out, open(js, "w"), indent=1)
    if out["result"] != "CERTIFIED": raise RuntimeError("S2-1 fp FAILED")
    return out


def stage_cone(D, binname, beta, fpr):
    js = os.path.join(D, "cone.json")
    if os.path.exists(js): return json.load(open(js))
    sp = dict(base(beta), Tstop=fpr["Tstop"], c=fpr["w"], rho=fpr["rho"], T=[fpr["u"][0], fpr["s"][0], fpr["u"][1], fpr["s"][1]], delta=DELTA)
    writespec(os.path.join(D, "cone.spec"), sp)
    txt, rc = run(binname, "cone", os.path.join(D, "cone.spec"), os.path.join(D, "cone.out"))
    m_ = re.search(r"^RESULT cone CERTIFIED L (\S+) rhop (\S+) deltastar (\S+)", txt, re.M)
    out = dict(result="CERTIFIED" if m_ else "FAIL", txt=txt.splitlines()[-4:])
    if m_: out.update(L=m_.group(1), rhop=m_.group(2), deltastar=m_.group(3))
    json.dump(out, open(js, "w"), indent=1)
    if not m_: raise RuntimeError("S2-2 cone FAILED")
    return out


def float_sym(f, fpr, beta):
    """the float R-symmetric half BVP solution (as s2f.sym) with kshift = KSHIFT, in the RIGOROUS frame (c, u~)."""
    fp = np.array(fpr["float_fp"]); vu = np.array(fpr["float_vu"]); lam = fpr["lam"]
    su, n = s2f.zero_s(0.03)
    z = fp + su * vu; pts = [z]
    for i in range(n): z = s1.Pstep(f, z)[0]; pts.append(z)
    m0 = int(np.argmax([p[0] for p in pts])); m = m0 + KSHIFT; c0 = su / lam ** KSHIFT
    z = fp + c0 * vu; Z = []
    for i in range(m - 1): z = s1.Pstep(f, z)[0]; Z.append(z)
    X = np.concatenate([[c0], np.ravel(Z)]); Dm = 2 * m - 1
    for it in range(14):
        w = [fp + X[0] * vu] + list(X[1:].reshape(m - 1, 2)); R = np.zeros(Dm); Jm = np.zeros((Dm, Dm)); Js = []; Ts = []
        for i in range(m):
            o = s1.Pstep(f, w[i]); Js.append(o[2]); Ts.append(o[1])
            if i < m - 1: R[2 * i:2 * i + 2] = o[0] - w[i + 1]
            else: R[Dm - 1] = o[0][1]
        Jm[0:2, 0] = Js[0] @ vu
        for i in range(m - 1):
            col = 1 + 2 * i; Jm[2 * i:2 * i + 2, col:col + 2] = -np.eye(2)
            if 2 * i + 2 < Dm - 1: Jm[2 * i + 2:2 * i + 4, col:col + 2] = Js[i + 1]
            else: Jm[Dm - 1, col:col + 2] = Js[i + 1][1]
        if np.max(np.abs(R)) < 1e-14: break
        X = X - np.linalg.solve(Jm, R)
    # express node 0 in the rigorous frame: w_u(u) = c + u u~ ; the float endpoint fp + s_u vu -> u = s_u (+ the small frame offset, fixed by the refinement)
    return X, Jm, Ts, m


def stage_bvp(D, binname, f, beta, fpr, cr):
    js = os.path.join(D, "bvp.json")
    if os.path.exists(js): return json.load(open(js))
    if os.path.exists(os.path.join(D, "bvp.spec")):          # resume: the refined spec exists; only the certifying pass runs
        m = int(open(os.path.join(D, "bvp.spec")).read().split("\nm ")[1].split()[0])
        txt, rc = run(binname, "bvp", os.path.join(D, "bvp.spec"), os.path.join(D, "bvp.out"))
        res = re.search(r"^RESULT bvp krawczyk (\S+) v_x (\S+) v_px (\S+)", txt, re.M)
        out = dict(m=m, krawczyk=res.group(1) if res else "FAIL", v_x=res.group(2) if res else None, v_px=res.group(3) if res else None,
                   p=mids(txt, "p"), v=mids(txt, "v"), kline=[l for l in txt.splitlines() if l.startswith(("KRAWCZYK", "SIGNTEST", "BALL"))])
        json.dump(out, open(js, "w"), indent=1); return out
    X, Jm, Ts, m = float_sym(f, fpr, beta)
    A = np.linalg.inv(Jm)
    sp = dict(base(beta), c=fpr["w"], T=[fpr["u"][0], fpr["s"][0], fpr["u"][1], fpr["s"][1]], L=cr["L"], rhop=cr["rhop"], deltastar=cr["deltastar"],
              m=str(m), ubar=d17(X[0]), z=[d17(v) for v in X[1:]], tstop=[d17(t - 2.0) for t in Ts], A=[d17(a) for a in A.ravel()])
    writespec(os.path.join(D, "bvp_pt.spec"), dict(sp, pointonly="1"))
    txt, _ = run(binname, "bvp", os.path.join(D, "bvp_pt.spec"), os.path.join(D, "bvp_pt.out"))
    F = mids(txt, "F"); Fv = [mp.mpf(F[i][2]) for i in range(2 * m - 1)]
    Xm = [mp.mpf(sp["ubar"])] + [mp.mpf(v) for v in sp["z"]]
    Am = [[mp.mpf(d17(A[i][j])) for j in range(2 * m - 1)] for i in range(2 * m - 1)]
    X2 = [Xm[i] - mp.fsum(Am[i][j] * Fv[j] for j in range(2 * m - 1)) for i in range(2 * m - 1)]
    sp["ubar"] = d40(X2[0]); sp["z"] = [d40(v) for v in X2[1:]]
    writespec(os.path.join(D, "bvp.spec"), sp)
    txt, rc = run(binname, "bvp", os.path.join(D, "bvp.spec"), os.path.join(D, "bvp.out"))
    res = re.search(r"^RESULT bvp krawczyk (\S+) v_x (\S+) v_px (\S+)", txt, re.M)
    out = dict(m=m, krawczyk=res.group(1) if res else "FAIL", v_x=res.group(2) if res else None, v_px=res.group(3) if res else None,
               p=mids(txt, "p"), v=mids(txt, "v"), kline=[l for l in txt.splitlines() if l.startswith(("KRAWCZYK", "SIGNTEST", "BALL"))],
               float_ratio=None)
    json.dump(out, open(js, "w"), indent=1)
    return out


def main_chain(label, field, beta):
    D = os.path.join(HERE, "s2", label); os.makedirs(D, exist_ok=True)
    binname = "s2_main_sab" if field == "sab" else "s2_main"
    t0 = time.time(); print("S2 chain %s field %s beta %g" % (label, field, beta), flush=True)
    f = flow_for(field, beta)
    fpr = stage_fp(D, binname, f, beta); print("  fp", fpr["result"], "rho", fpr["rho"], flush=True)
    cr = stage_cone(D, binname, beta, fpr); print("  cone", cr["result"], "L", cr.get("L"), "deltastar", cr.get("deltastar"), flush=True)
    br = stage_bvp(D, binname, f, beta, fpr, cr); print("  bvp", br["krawczyk"], "v_x", br["v_x"], "v_px", br["v_px"], flush=True)
    print("DONE %s %.0f s" % (label, time.time() - t0), flush=True)


def float_meet(f, fp, vu, m, c, cp, Zf, Zb, g, xh, it=16):
    """float meeting system in s2_main's meet order: X = (c, z_1..z_{m-1}, z'_1..z'_{m-1}, c', alpha), dim 4m - 1;
    equations: forward links, links from w_u(c'), meeting (2), phase x(z_{m-1}) = xh."""
    Rm = np.diag([1.0, -1.0]); D = 4 * m - 1; ob = 1 + 2 * (m - 1); rb = 2 * (m - 1); mr = 4 * (m - 1)
    X = np.concatenate([[c], np.ravel(Zf), np.ravel(Zb), [cp, 0.0]])
    for k in range(it):
        c_ = X[0]; Zf_ = X[1:ob].reshape(m - 1, 2); Zb_ = X[ob:ob + 2 * (m - 1)].reshape(m - 1, 2); cp_, al = X[-2], X[-1]
        R = np.zeros(D); Jm = np.zeros((D, D))
        Of = [s1.Pstep(f, w) for w in [fp + c_ * vu] + list(Zf_)]; Ob = [s1.Pstep(f, w) for w in [fp + cp_ * vu] + list(Zb_)]
        for i in range(m - 1):
            R[2 * i:2 * i + 2] = Of[i][0] - Zf_[i]; R[rb + 2 * i:rb + 2 * i + 2] = Ob[i][0] - Zb_[i]
            cz, czp = 1 + 2 * i, ob + 2 * i
            Jm[2 * i:2 * i + 2, cz:cz + 2] = -np.eye(2); Jm[rb + 2 * i:rb + 2 * i + 2, czp:czp + 2] = -np.eye(2)
            if i < m - 2: Jm[2 * i + 2:2 * i + 4, cz:cz + 2] = Of[i + 1][2]; Jm[rb + 2 * i + 2:rb + 2 * i + 4, czp:czp + 2] = Ob[i + 1][2]
        Jm[0:2, 0] = Of[0][2] @ vu; Jm[rb:rb + 2, D - 2] = Ob[0][2] @ vu
        R[mr:mr + 2] = Of[m - 1][0] - Rm @ Ob[m - 1][0] - al * g
        czl, czpl = 1 + 2 * (m - 2), ob + 2 * (m - 2)
        Jm[mr:mr + 2, czl:czl + 2] = Of[m - 1][2]; Jm[mr:mr + 2, czpl:czpl + 2] = -Rm @ Ob[m - 1][2]; Jm[mr:mr + 2, D - 1] = -g
        R[D - 1] = Zf_[-1][0] - xh; Jm[D - 1, czl] = 1.0
        if np.max(np.abs(R)) < 1e-14 and k > 0: break
        X = X - np.linalg.solve(Jm, R)
    return X, Jm, [o[1] for o in Of], [o[1] for o in Ob], float(np.max(np.abs(R)))


def main_meet(label0, frac=0.25, kdeep=4):
    D0 = os.path.join(HERE, "s2", label0); D = os.path.join(HERE, "s2", "meet_ii"); os.makedirs(D, exist_ok=True)
    js = os.path.join(D, "meet.json")
    if os.path.exists(js): print(open(js).read()); return
    if os.path.exists(os.path.join(D, "meet.spec")):          # resume: only the certifying pass
        txt, rc = run("s2_main", "meet", os.path.join(D, "meet.spec"), os.path.join(D, "meet.out"))
        r_ = re.search(r"^RESULT meet krawczyk (\S+) klemma (\S+)", txt, re.M)
        out = dict(krawczyk=r_.group(1) if r_ else "FAIL", klemma=r_.group(2) if r_ else "FAIL",
                   lines=[l for l in txt.splitlines() if l.startswith(("KRAWCZYK", "KLEMMA", "RESULT", "BALL", "FAMILY"))])
        json.dump(out, open(js, "w"), indent=1); print("  meet", out["krawczyk"], "klemma", out["klemma"], flush=True); return
    while not os.path.exists(os.path.join(D0, "cone.json")): time.sleep(30)
    fpr = json.load(open(os.path.join(D0, "fp.json"))); cr = json.load(open(os.path.join(D0, "cone.json")))
    print("S2 control (ii) meet (free c + phase condition), reusing", label0, "fp", fpr["result"], "cone", cr["result"], flush=True)
    f = flow_for("true", 0.0); fp = np.array(fpr["float_fp"]); vu = np.array(fpr["float_vu"]); lam = fpr["lam"]
    Rm = np.diag([1.0, -1.0]); su, n = s2f.zero_s(0.03)
    z = fp + su * vu; pts = [z]
    for i in range(n): z = s1.Pstep(f, z)[0]; pts.append(z)
    m0 = int(np.argmax([p[0] for p in pts]))
    grid = [su * lam ** (j / 48) for j in range(-96, 48)]; Yg = []
    for cg in grid:
        z = fp + cg * vu; ch = []
        for i in range(m0):
            o = s1.Pstep(f, z); z = o[0] if o is not None else np.array([np.nan, np.nan]); ch.append(z)
        Yg.append(ch)
    j = 96 + int(round(frac * 48)); c = grid[j]; yf = Yg[j][-1]
    jb = int(np.nanargmin([np.linalg.norm(Rm @ Yb[-1] - yf) for Yb in Yg]))
    g = s2f.Kgrad(yf); g = g / np.linalg.norm(g)
    xh = Yg[j][-2][0]                                   # the phase: x of the forward chain's last node
    Xs, Js, _, _, res_s = float_meet(f, fp, vu, m0, c, grid[jb], Yg[j][:-1], Yg[jb][:-1], g, xh)
    print("  shallow: m %d c %.4e c' %.4e alpha %.2e |F| %.1e cond %.2e" % (m0, Xs[0], Xs[-2], Xs[-1], res_s, np.linalg.cond(Js)), flush=True)
    m = m0 + kdeep; cd = Xs[0] / lam ** kdeep; cpd = Xs[-2] / lam ** kdeep
    def chain(c_):
        z = fp + c_ * vu; Z = []
        for i in range(m - 1): z = s1.Pstep(f, z)[0]; Z.append(z)
        return Z
    X, Jm, Ts, Tsp, res = float_meet(f, fp, vu, m, cd, cpd, chain(cd), chain(cpd), g, xh)
    A = np.linalg.inv(Jm); Dm = 4 * m - 1; ob = 1 + 2 * (m - 1)
    print("  deep: m %d c %.4e c' %.4e alpha %.2e |F| %.1e cond %.2e ||A||_inf %.2e" % (m, X[0], X[-2], X[-1], res, np.linalg.cond(Jm), np.max(np.sum(np.abs(A), 1))), flush=True)
    sp = dict(base(0.0), c=fpr["w"], T=[fpr["u"][0], fpr["s"][0], fpr["u"][1], fpr["s"][1]], L=cr["L"], rhop=cr["rhop"], deltastar=cr["deltastar"],
              m=str(m), c0=d17(X[0]), cprime=d17(X[-2]), xmid=d17(xh), xrad="1e-15", z=[d17(v) for v in X[1:ob]], zp=[d17(v) for v in X[ob:ob + 2 * (m - 1)]],
              g=[d17(g[0]), d17(g[1])], tstop=[d17(t - 2.0) for t in Ts], tstopp=[d17(t - 2.0) for t in Tsp], A=[d17(a) for a in A.ravel()])
    writespec(os.path.join(D, "meet_pt.spec"), dict(sp, pointonly="1"))
    txt, _ = run("s2_main", "meet", os.path.join(D, "meet_pt.spec"), os.path.join(D, "meet_pt.out"))
    F = mids(txt, "F"); Fv = [mp.mpf(F[i][2]) for i in range(Dm)]
    Xm = [mp.mpf(sp["c0"])] + [mp.mpf(v) for v in sp["z"]] + [mp.mpf(v) for v in sp["zp"]] + [mp.mpf(sp["cprime"]), mp.mpf(0)]
    Am = [[mp.mpf(d17(A[i][k])) for k in range(Dm)] for i in range(Dm)]
    X2 = [Xm[i] - mp.fsum(Am[i][k] * Fv[k] for k in range(Dm)) for i in range(Dm)]
    if abs(X2[-1]) > mp.mpf("1e-25"): print("  note: refined alpha-bar %s (alpha-bar = 0 is used in s2_main)" % mp.nstr(X2[-1], 5), flush=True)
    sp["c0"] = d40(X2[0]); sp["z"] = [d40(v) for v in X2[1:ob]]; sp["zp"] = [d40(v) for v in X2[ob:ob + 2 * (m - 1)]]; sp["cprime"] = d40(X2[-2])
    writespec(os.path.join(D, "meet.spec"), sp)
    txt, rc = run("s2_main", "meet", os.path.join(D, "meet.spec"), os.path.join(D, "meet.out"))
    r_ = re.search(r"^RESULT meet krawczyk (\S+) klemma (\S+)", txt, re.M)
    out = dict(m=m, krawczyk=r_.group(1) if r_ else "FAIL", klemma=r_.group(2) if r_ else "FAIL",
               lines=[l for l in txt.splitlines() if l.startswith(("KRAWCZYK", "KLEMMA", "RESULT", "BALL", "FAMILY"))])
    json.dump(out, open(js, "w"), indent=1); print("  meet", out["krawczyk"], "klemma", out["klemma"], flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "meet": main_meet(a[1]); raise SystemExit(0)
    main_chain(a[0], a[1], float(a[2]))
