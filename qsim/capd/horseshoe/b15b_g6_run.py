"""b15b_g6_run.py -- B15b gate G6, part 3: the DRIVER that applies the G6 decision functions (b15b_g6.py, toys PASS
9e5b94b) to a counted B15 run's own records. Read-only: the frozen constructor is never edited or re-run.
Inputs (defaults: the rust run's names, b15_kerr_ck.py with B15_MAP=rust):
  run JSON (step 1 / step 2 records), pcache journal (every P / Pinv call and result), saved arcs (npz),
  plunge log (B15b-1 P5), the gate results (G1_G3_G4.json + the MNFlow reference rows) for the error model,
  and a map object for FRESH Jacobians (the local gain) and for the 1e-14 / 1e-13 recomputes of thin decisions.
Usage: b15b_g6_run.py [--run-json F] [--journal F] [--arcs F] [--plunges F] [--out F]

What it does (PREREG "G6. Decision margins"; B15B_G6_DESIGN.md points 1-6; B15b-1 P5; B15b-2):
 1. Completeness. D1 is replayed from the journal (find_periodic's loop); the arcs are rebuilt by b15b_g6.arcs_replica
    from journal hits only and must equal the saved arcs BIT FOR BIT; the D4 / D6 / D7 counts must equal the run's.
    Any mismatch: G6 INCOMPLETE (never PASS); by B15b-2 rule 5 any D8 accept is then UNRESOLVED.
 2. Error model (point 3). e_map(T) = 3 x max(the G4 cross-implementation difference in T's decade bin, the G4c
    convergence estimate), absolute (relative x max(1, |x|, |px|)). T beyond the largest G4-compared T: "error
    unmeasured", FLAGGED, never extrapolated (the largest bin is used for the arithmetic only).
    A point at level k with orbit q_0..q_k (rebuilt from the journal) carries
      e_k = sum_{j<k} ||DF(q_{k-1}) .. DF(q_{j+1})||_2 e_map(T_j) + ||DF(q_{k-1}) .. DF(q_0)||_2 (e_z + t e_vec),
    DF = DP (W^u) or DP^-1 (W^s, DP taken at q_{j+1}), from FRESH map Jacobians at the run's tmax and tolerance;
    e_z, e_vec = the start-point errors from step 1 (Newton residual / sigma_min(DP - I); |dDP| / eigenvalue gap).
 3. Decisions with margins, via b15b_g6: D1 d1_newton, D2 d2_saddle, D4 seg_decision (every recorded crossing, plus a
    NEAR-MISS scan of every segment pair whose extended parameter box reaches [0, 1]) and vertex_risk, D5 skip-near-z,
    D6 d6_angle, D7 d7_redflag, D8 d8_connection with the B15b-2 chord rule, D3 / P5 the plunge slack (logged).
 4. Thin decisions: the feeding calls are recomputed at rtol = atol = 1e-14 (and 1e-13 for the error, by
    self-convergence, x 3). The 1e-14 decision is used, both are reported, a change is FLAGGED; thin again at 1e-14
    (10 x its own error) -> UNRESOLVED, and the step outcome is UNRESOLVED.
Verdict: INCOMPLETE | UNRESOLVED (with the decisions named) | PASS (complete, no unresolved decision; flags listed).
Non-rigorous (the constructor stage). Written by Claude Opus 5.5 (session "Quantum"), 2026-11-20."""
import argparse, glob, json, math, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import b15b_g6 as G

OUT = HERE.parent / "horseshoe_results" / "kerr"
TMAX = 1e6; TOL_RUN = 1e-12; NEWTON_TOL = 1e-10; SKIP = 1e-3


def jkey_P(w, n=1, jac=False):
    return ("P", np.asarray(w, dtype=np.float64).tobytes(), tuple(sorted(dict(n=n, jac=jac).items())))


def jkey_Pinv(w):
    return ("Pinv", np.asarray(w, dtype=np.float64).tobytes(), ())


def error_model(gates_dir):
    g = json.loads((gates_dir / "G1_G3_G4.json").read_text()); tasks = {t["id"]: t for t in json.loads((gates_dir / "tasks.json").read_text())}
    ref = {}
    for p in glob.glob(str(gates_dir / "mnflow_*.jsonl")):
        for l in open(p):
            if l.strip(): r = json.loads(l); ref[r["id"]] = r
    bins, Ts = {}, []
    for r in g["G4"]:
        v = ref.get(r["id"], {}).get("value")
        if not v or tasks[r["id"]]["call"] != "P": continue
        T = v[2]; Ts.append(T); mag = max(1.0, abs(v[0]), abs(v[1]))
        d = max(r[n].get("maxrel", 0.0) for n in ("rust", "c++")) * mag
        b = int(math.floor(math.log10(T))); bins[b] = max(bins.get(b, 0.0), d)
    conv = max([x["maxrel_vs_1e12"] for x in g["G4c"]] + [0.0]) * 3.0
    dp = max(r[n].get("maxrel", 0.0) for r in g["G1"] + g["G4"] for n in ("rust", "c++") if n in r)
    return dict(bins=bins, conv=conv, Tmax=max(Ts), dp_rel=dp)


def e_map(model, T):
    """(absolute one-return error, measured?)"""
    measured = T is not None and np.isfinite(T) and 0 < T <= model["Tmax"]
    b = int(math.floor(math.log10(T))) if (T is not None and np.isfinite(T) and T > 0) else max(model["bins"])
    base = model["bins"].get(b, max(model["bins"].values()))
    return 3.0 * max(base, model["conv"] * 2.5), bool(measured)      # x 2.5: the conv estimate is relative, |x| <= 2.5


class Run:
    """the run's records plus lookups"""
    def __init__(self, run, mem, arcs, plunges, model, flow):
        self.run, self.mem, self.arcs, self.plunges, self.model, self.flow = run, mem, arcs, plunges, model, flow
        self.jac = {}; self.misses = []

    def F(self, forward):
        def fP(q):
            k = jkey_P(q, 1, False)
            if k not in self.mem: self.misses.append(("P", tuple(q))); return None
            v = self.mem[k]; return None if v is None else v[0]
        def fPinv(q):
            k = jkey_Pinv(q)
            if k not in self.mem: self.misses.append(("Pinv", tuple(q))); return None
            return self.mem[k]
        return fP if forward else fPinv

    def Pfull(self, w, n=1):
        """H.P(w, 1) as manifold_arcs calls it, from the journal: (w2, T) or None"""
        k = jkey_P(w, 1, False)
        if k not in self.mem: self.misses.append(("P", tuple(w))); return None
        return self.mem[k]

    def DP(self, w, tol=TOL_RUN):
        key = (np.asarray(w, float).tobytes(), tol)
        if key not in self.jac:
            r = self.flow.P(np.asarray(w, float), 1, jac=True, tmax=TMAX, rtol=tol, atol=tol)
            self.jac[key] = None if r is None else (np.asarray(r[2], float), float(r[1]))
        return self.jac[key]


def orbit(R, z, e, sign, t, k, forward):
    F = R.F(forward); q = np.asarray(z, float) + sign * t * np.asarray(e, float); orb = [q]
    for _ in range(k):
        q = F(q)
        if q is None: return None
        orb.append(q)
    return orb


def point_error(R, orb, forward, t, e_z, e_vec):
    mats, Ts, meas = [], [], True
    for j in range(len(orb) - 1):
        r = R.DP(orb[j]) if forward else R.DP(orb[j + 1])
        if r is None: return float("inf"), False                 # a fresh Jacobian failed: no gain, cannot bound
        Dj, Tj = r; mats.append(Dj if forward else np.linalg.inv(Dj)); Ts.append(Tj)
    err = 0.0
    for j in range(len(mats)):
        prod = np.eye(2)
        for m in mats[j + 1:]: prod = m @ prod
        ej, mj = e_map(R.model, Ts[j]); err += np.linalg.norm(prod, 2) * ej; meas &= mj
    full = np.eye(2)
    for m in mats: full = m @ full
    return err + np.linalg.norm(full, 2) * (e_z + t * e_vec), meas


def recompute_orbit(flow, z, e, sign, t, k, forward, tol):
    q = np.asarray(z, float) + sign * t * np.asarray(e, float); orb = [q]
    for _ in range(k):
        if forward:
            r = flow.P(q, 1, jac=False, tmax=TMAX, rtol=tol, atol=tol); q = None if r is None else np.asarray(r[0])
        else:
            q = flow.Pinv(q, tmax=TMAX, rtol=tol, atol=tol)
        if q is None: return None
        orb.append(np.asarray(q, float))
    return orb


def g6(R, z_dir=None):
    rep = dict(model=dict(bins={str(k): v for k, v in R.model["bins"].items()}, conv=R.model["conv"], Tmax=R.model["Tmax"],
                          dp_rel=R.model["dp_rel"]), flags=[], unresolved=[], decisions={}, counts={}, complete=True, notes=[])
    def flag(s): rep["flags"].append(s)
    def incomplete(s): rep["complete"] = False; rep["notes"].append("INCOMPLETE: " + s)
    run = R.run
    # ---- D1: find_periodic replayed from the journal (same loop, same tol)
    w = np.array(run["seed"], float); res, Ts, z, D = [], [], None, None
    jac_calls = [k for k in R.mem if k[0] == "P" and dict(k[2]).get("jac")]
    for _ in range(10):
        v = R.mem.get(jkey_P(w, 1, True))
        if v is None: incomplete("D1: a Newton call missing from the journal"); break
        w2, T, Dm = v; F = w2 - w; res.append(float(np.linalg.norm(F))); Ts.append(T)
        if res[-1] < NEWTON_TOL: z, D = w, np.asarray(Dm, float); break
        dw = np.linalg.solve(np.asarray(Dm) - np.eye(2), -F); lam = 1.0     # find_periodic's line search, on the map's lift
        while lam > 1e-3:
            if np.isfinite(R.flow.py_of(*(w + lam * dw))): break
            lam /= 2
        w = w + lam * dw
    if len(res) != len(jac_calls): incomplete("D1: %d replayed iterations vs %d journalled jac calls" % (len(res), len(jac_calls)))
    if z is None or list(z) != list(run["step1"]["z"]): incomplete("D1: the replayed z is not the run's step-1 z"); return finish(rep)
    eT = max(e_map(R.model, T)[0] for T in Ts)
    d1 = G.d1_newton(res, NEWTON_TOL, eT); rep["decisions"]["D1"] = d1
    for T in Ts:
        if not e_map(R.model, T)[1]: flag("D1: a Newton return beyond the G4-measured T")
    # ---- D2: saddle on DP(z) +- its error (G4's DP differences, relative x max(1, |entry|), x 3)
    dD = [[3 * R.model["dp_rel"] * max(1.0, abs(D[i][j])) for j in range(2)] for i in range(2)]
    d2 = G.d2_saddle(D.tolist(), dD); rep["decisions"]["D2"] = d2
    # thin D1 / D2: recompute the converged call at 1e-14 and 1e-13
    if d1["tol_too_tight"]: flag("D1: tol < 10 e_map")
    if any(x["thin"] for x in d1["iterations"]) or d2["thin"]:
        r14 = R.flow.P(z, 1, jac=True, tmax=TMAX, rtol=1e-14, atol=1e-14); r13 = R.flow.P(z, 1, jac=True, tmax=TMAX, rtol=1e-13, atol=1e-13)
        e14 = 3 * float(np.linalg.norm(r14[0] - r13[0])); dD14 = 3 * np.abs(np.asarray(r14[2]) - np.asarray(r13[2]))
        n14 = G.d1_newton([float(np.linalg.norm(r14[0] - z))], NEWTON_TOL, e14)["iterations"][0]
        s14 = G.d2_saddle(np.asarray(r14[2]).tolist(), dD14.tolist())
        rep["decisions"]["D1D2_1e-14"] = dict(newton=n14, saddle=s14)
        if n14["thin"]: rep["unresolved"].append("D1 thin at 1e-14")
        if s14["thin"]: rep["unresolved"].append("D2 thin at 1e-14")
        if n14["converged"] != d1["iterations"][-1]["converged"] or s14["robust"] != d2["robust"]: flag("D1/D2: the 1e-14 decision differs")
    # ---- step-1 start-point errors for the arcs
    ev, V = np.linalg.eig(D); ev, V = ev.real, V.real
    iu, is_ = (0, 1) if abs(ev[0]) > abs(ev[1]) else (1, 0)
    e_u = V[:, iu] / np.linalg.norm(V[:, iu]); e_s = V[:, is_] / np.linalg.norm(V[:, is_])
    e_z = res[-1] / np.linalg.svd(D - np.eye(2))[1][-1] + eT
    e_vec = float(np.linalg.norm(np.array(dD))) / abs(ev[iu] - ev[is_])
    # ---- replica of the arcs from the journal: must be bit-identical to the saved arcs
    au, mu, du = G.arcs_replica(R.Pfull, R.F(False), z, e_u, ev[iu], True, K=5, eps=1e-4)
    as_, ms, ds = G.arcs_replica(R.Pfull, R.F(False), z, e_s, 1 / ev[is_], False, K=5, eps=1e-4)
    saved_u = [(k, R.arcs["u_%d_%d" % (k, i)]) for i, (k, _) in enumerate(au) if "u_%d_%d" % (k, i) in R.arcs]
    saved_s = [(k, R.arcs["s_%d_%d" % (k, i)]) for i, (k, _) in enumerate(as_) if "s_%d_%d" % (k, i) in R.arcs]
    same = not R.misses and G.arcs_equal(au, saved_u) and G.arcs_equal(as_, saved_s) and \
           len([k for k in R.arcs if k.startswith("u_")]) == len(au) and len([k for k in R.arcs if k.startswith("s_")]) == len(as_)
    rep["counts"].update(replica_bit_identical=bool(same), journal_misses=len(R.misses))
    if not same: incomplete("the replica does not reproduce the saved arcs bit for bit (B15b-2 rule 5)")
    # ---- per-point errors for every arc point (fresh Jacobians along each point's own orbit)
    def errs(arcs_, metas, forward, e_dir):
        out = []
        for (k, A), m in zip(arcs_, metas):
            row = []
            for t in m["ts"]:
                orb = orbit(R, z, e_dir, m["sign"], float(t), m["k"], forward)
                row.append((float("inf"), False) if orb is None else point_error(R, orb, forward, float(t), e_z, e_vec))
            out.append(row)
        return out
    EU, ES = errs(au, mu, True, e_u), errs(as_, ms, False, e_s)
    CU = [G.chord_mask(m, du) for m in mu]; CS = [G.chord_mask(m, ds) for m in ms]
    rep["counts"].update(drops_u=sum(len(v) for v in du.values()), drops_s=sum(len(v) for v in ds.values()),
                         chord_segments=int(sum(c.sum() for c in CU) + sum(c.sum() for c in CS)))
    # ---- crossings, exactly as the constructor computed them, then each decision with its margin
    import hs_construct as HS
    allc = HS.crossings(au, as_, min_angle=0.0, skip_near=[z])
    rep["counts"].update(D4_crossings=len(allc), run_crossings=run["step2"]["n_crossings_all"])
    if len(allc) != run["step2"]["n_crossings_all"]: incomplete("D4 count %d vs the run's %d" % (len(allc), run["step2"]["n_crossings_all"]))
    rows = []
    for n, (pt, ang, ku, ks) in enumerate(allc):
        hit = None
        def cands(A):                                                    # segments whose bounding box holds pt
            lo, hi = np.minimum(A[:-1], A[1:]), np.maximum(A[:-1], A[1:]); tol = 1e-12 * (1 + np.abs(pt))
            return np.nonzero(((lo <= pt + tol) & (pt - tol <= hi)).all(axis=1))[0]
        for ai, (kk, U) in enumerate(au):
            if kk != ku or len(U) < 2: continue
            for bj, (kk2, S) in enumerate(as_):
                if kk2 != ks or len(S) < 2: continue
                for i in cands(U):
                    for j in cands(S):
                        r = HS._seg_intersect(U[i], U[i + 1], S[j], S[j + 1])
                        if r is not None and abs(r[1] - ang) <= 1e-15 * max(1.0, ang) and np.allclose(r[0], pt, rtol=0, atol=1e-14): hit = (ai, int(i), bj, int(j)); break
                    if hit: break
                if hit: break
            if hit: break
        if hit is None: incomplete("crossing %d not located" % n); continue
        ai, i, bj, j = hit; U, S = au[ai][1], as_[bj][1]
        eU = max(EU[ai][i][0], EU[ai][i + 1][0]); eS = max(ES[bj][j][0], ES[bj][j + 1][0])
        meas = EU[ai][i][1] and EU[ai][i + 1][1] and ES[bj][j][1] and ES[bj][j + 1][1]
        lU, lS = float(np.linalg.norm(U[i + 1] - U[i])), float(np.linalg.norm(S[j + 1] - S[j]))
        d4 = G.seg_decision(U[i], U[i + 1], S[j], S[j + 1], eU, eS); vr = G.vertex_risk(U, S, j, eU, eS)
        d6 = G.d6_angle(float(ang), eU, lU, eS, lS)
        rc = run["step2"]["crossings"][n]; th = rc["theta_floor"]
        dth = th * 2 * (eU / lU + eS / lS) + (eU + eS) * th / max(lU + lS, 1e-300)   # the same e through kappa-hat and l
        d7 = G.d7_redflag(float(ang), th, d6["dangle"], dth)
        dz = float(np.linalg.norm(pt - z)); d5thin = abs(dz - SKIP) < G.THIN_FACTOR * (eU + eS + e_z)
        chord = bool(CU[ai][i] or CS[bj][j])
        row = dict(n=n, k_u=int(ku), k_s=int(ks), angle=float(ang), on_chord=chord, eU=eU, eS=eS, measured=bool(meas),
                   D4=d4, vertex=vr, D5_thin=bool(d5thin), D6=d6, D7=d7, theta_floor=th)
        thin = d4["thin"] or vr["zero_count_risk"] or d5thin or d6["thin"] or d7["thin"]
        if not meas: flag("crossing %d: error unmeasured (a return beyond the G4 range)" % n)
        if thin:
            row["recompute_1e-14"] = rec = recompute_crossing(R, z, e_u, e_s, mu[ai], ms[bj], i, j)
            if rec.get("thin", True): rep["unresolved"].append("crossing %d thin at 1e-14" % n)
            if rec.get("accepted") is not None and rec["accepted"] != d6["accepted"]: flag("crossing %d: the 1e-14 D6 decision differs" % n)
        if chord and d6["accepted"]: flag("crossing %d: D6 accept on a CHORD -> UNRESOLVED (B15b-2 rule 2)" % n)
        rows.append(row)
    rep["decisions"]["crossings"] = rows
    nacc = sum(r["D6"]["accepted"] for r in rows); nred = sum(r["D7"]["red"] for r in rows)
    rep["counts"].update(D6_accepts=nacc, run_D6=run["step2"]["n_at_or_above_0p01"], D7_red=nred, run_D7=run["step2"]["n_red_flags"])
    if nacc != run["step2"]["n_at_or_above_0p01"] or nred != run["step2"]["n_red_flags"]: incomplete("D6/D7 counts differ from the run's")
    # ---- D4 near-miss scan: segment pairs the run did NOT record whose extended parameter box reaches [0, 1]
    near = []                                                            # vectorised over S, as hs_construct.crossings
    for ai, (ku, U) in enumerate(au):
        if len(U) < 2: continue
        eUs = np.array([max(EU[ai][q][0], EU[ai][q + 1][0]) for q in range(len(U) - 1)])
        for bj, (ks, S) in enumerate(as_):
            if len(S) < 2: continue
            m = 10 * (eUs.max() + max(x[0] for x in ES[bj]))
            if (U[:, 0].max() + m < S[:, 0].min() or S[:, 0].max() + m < U[:, 0].min() or
                    U[:, 1].max() + m < S[:, 1].min() or S[:, 1].max() + m < U[:, 1].min()): continue
            C, Dd = S[:-1], S[1:]; s_ = Dd - C; sn = np.linalg.norm(s_, axis=1)
            eSs = np.array([max(ES[bj][q][0], ES[bj][q + 1][0]) for q in range(len(S) - 1)])
            for i in range(len(U) - 1):
                a_, b_ = U[i], U[i + 1]; r = b_ - a_; nr = np.linalg.norm(r)
                den = r[0] * s_[:, 1] - r[1] * s_[:, 0]; ca = C - a_
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = (ca[:, 0] * s_[:, 1] - ca[:, 1] * s_[:, 0]) / den
                    u = (ca[:, 0] * r[1] - ca[:, 1] * r[0]) / den
                    ang = np.abs(den) / (nr * sn); dt = (eUs[i] / nr + eSs / sn) / np.maximum(ang, 1e-300)
                edge = np.minimum(np.minimum(t, 1 - t), np.minimum(u, 1 - u))
                strict = (np.abs(den) > 1e-18) & (edge >= 0)
                cand = (np.abs(den) > 1e-18) & ~strict & (np.abs(edge) < G.THIN_FACTOR * dt)
                for j in np.nonzero(cand)[0]:
                    # the Bridge (2026-11-20, G6 choice 3): recompute wherever the near-miss could become a crossing with
                    # angle >= min(0.01, 10 theta_floor) -- B15's prediction is about the RED-FLAG level, so a missed red
                    # flag below 0.01 must not slip through. theta_floor at the lines' intersection, by the run's floor_at.
                    da = eUs[i] / nr + eSs[j] / sn[j]; pt_ = a_ + t[j] * r; th_ = theta_floor_at(pt_, au, as_)
                    thr = min(0.01, 10 * th_) if np.isfinite(th_) else 0.0
                    near.append(dict(u=(ai, i), s=(bj, int(j)), angle=float(ang[j]), t=float(t[j]), uu=float(u[j]), theta_floor=float(th_),
                                     threshold=float(thr), could_accept=bool(ang[j] + G.THIN_FACTOR * da >= 0.01),
                                     could_flag=bool(ang[j] + G.THIN_FACTOR * da >= thr), on_chord=bool(CU[ai][i] or CS[bj][j])))
    rep["decisions"]["near_misses"] = near
    for x in near:
        if x["could_flag"]:
            rec = recompute_crossing(R, z, e_u, e_s, mu[x["u"][0]], ms[x["s"][0]], x["u"][1], x["s"][1]); x["recompute_1e-14"] = rec
            if rec.get("thin", True): rep["unresolved"].append("near-miss %s/%s thin at 1e-14" % (x["u"], x["s"]))
            if rec.get("exists"):
                red = rec.get("angle") is not None and np.isfinite(x["theta_floor"]) and rec["angle"] > 10 * x["theta_floor"]
                rec["red_flag"] = bool(red)
                flag("near-miss %s/%s EXISTS at 1e-14 (angle %.3g%s)" % (x["u"], x["s"], rec.get("angle") or float("nan"),
                                                                       ", a RED FLAG the run did not record" if red else ""))
    # ---- D3 / B15b-1 P5
    nones = sum(1 for v in R.mem.values() if v is None)
    rep["decisions"]["D3"] = dict(journal_nones=nones, plunge_records=len(R.plunges),
                                  min_slack=[min((p.get(k) for p in R.plunges if p.get(k) is not None), default=None) for k in ("slack_R", "slack_y")])
    if len(R.plunges) > nones: incomplete("more plunge records than journalled None results")
    # ---- D8 with B15b-2
    cand = [dict(accepted=r.get("recompute_1e-14", {}).get("accepted", r["D6"]["accepted"]) if r.get("recompute_1e-14") else r["D6"]["accepted"],
                 thin=bool(r.get("recompute_1e-14", {}).get("thin")) if r.get("recompute_1e-14") else False, on_chord=r["on_chord"]) for r in rows]
    cand += [dict(accepted=bool(x.get("recompute_1e-14", {}).get("exists") and x["recompute_1e-14"].get("accepted")),
                  thin=bool(x.get("recompute_1e-14", {}).get("thin")), on_chord=x["on_chord"]) for x in near if x["could_flag"]]
    d8 = G.d8_connection(cand); rep["decisions"]["D8"] = d8
    if not rep["complete"] and d8["outcome"] == "CONNECTION": d8["outcome"] = "UNRESOLVED (G6 INCOMPLETE, B15b-2 rule 5)"
    return finish(rep)


def floor_at(pt, arcs):
    """theta_floor's ingredients at pt, VERBATIM from b15_kerr_ck.py (the run's own definition): (distance, l, kappa)"""
    best = None
    for _, A in arcs:
        if len(A) < 3: continue
        d = np.linalg.norm((A[:-1] + A[1:]) / 2 - pt, axis=1); i = int(np.argmin(d))
        if best is None or d[i] < best[0]:
            j0, j1 = max(i - 1, 0), min(i + 1, len(A) - 2)
            seg = lambda j: A[j + 1] - A[j]
            t1, t2 = seg(j0), seg(j1); l = np.linalg.norm(seg(i))
            turn = abs(np.arctan2(t1[0] * t2[1] - t1[1] * t2[0], t1 @ t2))
            span = np.linalg.norm(A[j1 + 1] - A[j0]) or 1.0
            best = (d[i], l, turn / span)
    return best


def theta_floor_at(pt, au, as_):
    fu, fs = floor_at(pt, au), floor_at(pt, as_)
    return (fu[2] + fs[2]) / 2 * (fu[1] + fs[1]) if fu and fs else float("nan")


def recompute_crossing(R, z, e_u, e_s, mU, mS, i, j):
    """recompute the 4 endpoints of segment pair (U i..i+1, S j..j+1) at 1e-14 and 1e-13 (self-convergence error x 3)
    and re-decide D4 / D6 with that error"""
    o = {}
    for tol in (1e-14, 1e-13):
        pts = []
        for m, q, fwd, ed in ((mU, i, True, e_u), (mU, i + 1, True, e_u), (mS, j, False, e_s), (mS, j + 1, False, e_s)):
            orb = recompute_orbit(R.flow, z, ed, m["sign"], float(m["ts"][q]), m["k"], fwd, tol)
            if orb is None: return dict(thin=True, note="an orbit was lost at %g" % tol)
            pts.append(orb[-1])
        o[tol] = pts
    e = [3 * float(np.linalg.norm(a - b)) for a, b in zip(o[1e-14], o[1e-13])]
    a, b, c, d = o[1e-14]; eU, eS = max(e[0], e[1]), max(e[2], e[3])
    d4 = G.seg_decision(a, b, c, d, eU, eS)
    if d4.get("parallel"): return dict(thin=True, exists=None, accepted=None, errors=e)
    d6 = G.d6_angle(d4["angle"], eU, float(np.linalg.norm(b - a)), eS, float(np.linalg.norm(d - c)))
    return dict(exists=d4["strict"], accepted=bool(d4["strict"] and d6["accepted"]), thin=bool(d4["thin"] or d6["thin"]),
                angle=d4["angle"], errors=e)


def finish(rep):
    rep["notes"].append("The error used at 1e-14 is a self-convergence ESTIMATE (1e-14 vs 1e-13, x 3), not a bound (the Bridge, 2026-11-20).")
    if not rep["complete"]: rep["verdict"] = "INCOMPLETE"
    elif rep["unresolved"]: rep["verdict"] = "UNRESOLVED (%s)" % "; ".join(rep["unresolved"])
    else: rep["verdict"] = "PASS (%d flags)" % len(rep["flags"])
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-json", default=str(OUT / "b15_kerr_rust.json")); ap.add_argument("--journal", default=str(OUT / "b15_rust.journal"))
    ap.add_argument("--arcs", default=str(OUT / "b15_rust_arcs.npz")); ap.add_argument("--plunges", default=str(OUT / "b15_rust_plunges.jsonl"))
    ap.add_argument("--out", default=str(OUT / "b15_g6.json")); a = ap.parse_args()
    import pcache, kerr_compiled as KC
    run = json.loads(Path(a.run_json).read_text()); J = pcache.Journal(a.journal)
    pl = [json.loads(l) for l in open(a.plunges)] if Path(a.plunges).exists() else []
    flow = KC.CompiledFlow(KC.RUST); flow.delta_floor = run.get("delta_floor", 1e-6)
    R = Run(run, J.mem, dict(np.load(a.arcs)), pl, error_model(OUT / "b15b_gates"), flow)
    rep = g6(R); Path(a.out).write_text(json.dumps(rep, indent=1, default=float)); print("G6", rep["verdict"], "| D8:", rep["decisions"].get("D8"))


if __name__ == "__main__":
    main()
