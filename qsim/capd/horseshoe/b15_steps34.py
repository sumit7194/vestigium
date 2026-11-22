"""B15c driver (registered: PREREG_chaos_horseshoe_phase2.md, B15c a126a6b + B15c-1 7ca093d). Steps 3-4 for B15's
candidate connections: refine, orbit, frames (step 3); the B14 ladder (step 4); exact-rational hs_cover specs for the
rigorous stage; the hs_cover outcome classifier; the per-chain class and the vacuous-pass-guarded headline.

The FROZEN B14 constructor (hs_construct.py) is NOT edited. Its functions look up P, Pinv and px_of in their module at
call time, so a system is selected by setting those three globals (use_system). HH's own maps are saved at import, before
anything is plugged, so the HH positive control and the planted HH reject run in the same process as Kerr candidates.

refine_connection_scaled is the ONE unfrozen function: a verbatim copy of hs_construct.refine_connection with the coarse
scan's hard-coded HH constant 7.3 made a parameter. It is used ONLY by the diagnostic arm (UNFROZEN / NOT COUNTED). With
lam = 7.3 it must reproduce the frozen function bit for bit (checked by b15c_controls.py).

usage (counted stages; never before b15c_controls.py has PASSED):
  b15_steps34.py constructor T1|T2|T3|ARM      -> horseshoe_results/kerr/b15c/<tier>.json
  b15_steps34.py specs <tier>                  -> exact specs for chains with an accepted ladder entry (S8 gated)
"""
import hashlib, itertools, json, os, re, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import hs_construct as H

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "horseshoe_results"
KERR = RES / "kerr"
OUT = KERR / "b15c"
HH_MAPS = (H.P, H.Pinv, H.px_of)                        # saved BEFORE any plug: the HH system of the frozen module
LADDER = list(itertools.product([0.03, 0.02, 0.015, 0.01], [0.01, 0.005, 0.0025], [0.5, 0.25, 0.1], [0.5, 0.25, 0.1]))
Q_S = 0.740762452760964 * 89 ** 2                       # B15's registered separatrix Carter constant (physical units)
KERR_LIB_SHA = "42ea6c3cb33c6d75f068525750fbddd3718d06b080fbce191075abf2ec8759c2"   # the step 1-2 run's kerr_rs
KERR_HEAD = ["system mn", "prec 128", "order 20", "iter 1", "param k 39/1", "param alpha -5/8", "param beta 0/1",
             "param E 49/50", "param L 445/2", "param level -1/2"]   # level: B15e A1 (the registered B15c header omitted it)
HH_HEAD = ["system hh", "prec 128", "order 20", "iter 1", "param level 1/6"]
RIG_BODY = ["caps 65536 4096", "depth 16 12"]


# ---------------------------------------------------------------------------------------------- systems
_SYS = {"hh": HH_MAPS}
_KERR = {}


def kerr_setup(journal_name="b15c_rust.journal", plunges_name="b15c_rust_plunges.jsonl"):
    """The compiled map exactly as b15_kerr_ck.py sets it up (B15b / B15b-1), behind a NEW journal. Returns the triple."""
    if "maps" in _KERR:
        return _KERR["maps"]
    import kerr_compiled as KC, mn_numerics as MNN, pcache
    sha = hashlib.sha256(Path(KC.RUST).read_bytes()).hexdigest()
    if sha != KERR_LIB_SHA:
        raise SystemExit("HARNESS-ERROR: kerr_rs sha256 %s is not the step 1-2 run's %s" % (sha, KERR_LIB_SHA))
    kerr = KC.CompiledFlow(KC.RUST)
    g4 = json.loads((KERR / "b15b_gates" / "G1_G3_G4.json").read_text())["G4"]
    g4err = max(r[n]["maxrel"] for r in g4 for n in ("rust", "c++") if "maxrel" in r[n])
    kerr.delta_floor = max(1e-6, 100 * g4err)
    OUT.mkdir(parents=True, exist_ok=True)
    pl0 = kerr._plunge

    def plunge_logged(kind, w, sign):
        r = pl0(kind, w, sign); rec = dict(kerr.plunges[-1]); rec.update(kind=kind, w=[float(w[0]), float(w[1])])
        with open(OUT / plunges_name, "a") as fh:
            fh.write(json.dumps(rec, default=float) + "\n"); fh.flush(); os.fsync(fh.fileno())
        return r
    kerr._plunge = plunge_logged
    MNN.plug_into_constructor(kerr)                     # sets H.P / H.Pinv / H.px_of (py_of)
    H.P = lambda w, n=1, jac=False: kerr.P(w, n, jac, tmax=1e6)
    H.Pinv = lambda w: kerr.Pinv(w, tmax=1e6)
    J = pcache.Journal(str(OUT / journal_name)); pcache.wrap(H, J)
    _KERR.update(maps=(H.P, H.Pinv, H.px_of), flow=kerr, journal=J, lib_sha=sha, delta_floor=kerr.delta_floor, g4err=g4err)
    _SYS["kerr"] = _KERR["maps"]
    use_system("hh")                                    # leave the module on HH until a caller selects
    return _KERR["maps"]


def use_system(name):
    H.P, H.Pinv, H.px_of = _SYS[name]


# ---------------------------------------------------------------------------------------------- selection (B15c §1)
def b14_key(c, idx):
    return (abs(c["k_u"]) + abs(c["k_s"]), -c["angle"], idx)


def tiers(crossings, accepts):
    """T1 = B14's choice among the angle >= 0.01 accepts; T2 = the other measured accepts; T3 = extrapolated ones.
    accepts: the G6 summary's list (n, measured). Returns dict of lists of crossing indices, each in B14 order."""
    acc = [i for i, c in enumerate(crossings) if c["angle"] >= 0.01]
    meas = {a["n"]: a["measured"] for a in accepts}
    if sorted(acc) != sorted(meas):
        raise SystemExit("HARNESS-ERROR: the step-2 accepts and the G6 summary's accepts differ")
    order = sorted(acc, key=lambda i: b14_key(crossings[i], i))
    t1 = order[0]
    return dict(T1=[t1], T2=[i for i in order if i != t1 and meas[i]], T3=[i for i in order if i != t1 and not meas[i]])


# ---------------------------------------------------------------------------------------------- step 3 (B15c §2)
def refine_connection_scaled(p, eu, q, es, ku, ks, guess, lam, iters=30, tol=1e-13):
    """UNFROZEN COPY of hs_construct.refine_connection; the only change: 7.3 -> lam in the coarse scans."""
    P, Pinv = H.P, H.Pinv
    Fw = lambda w: (P(w, 1) or (None,))[0]
    def eqs(v):
        a = H._iter(Fw, np.asarray(p) + v[0] * np.asarray(eu), ku)
        b = H._iter(Pinv, np.asarray(q) + v[1] * np.asarray(es), ks)
        return None if a is None or b is None else a - b
    best = None
    for t in np.concatenate([np.geomspace(1e-4, 1e-4 * lam, 40), -np.geomspace(1e-4, 1e-4 * lam, 40)]):
        a = H._iter(Fw, np.asarray(p) + t * np.asarray(eu), ku)
        if a is not None and (best is None or np.linalg.norm(a - guess) < best[0]): best = (np.linalg.norm(a - guess), t)
    best2 = None
    for tau in np.concatenate([np.geomspace(1e-4, 1e-4 * lam, 40), -np.geomspace(1e-4, 1e-4 * lam, 40)]):
        b = H._iter(Pinv, np.asarray(q) + tau * np.asarray(es), ks)
        if b is not None and (best2 is None or np.linalg.norm(b - guess) < best2[0]): best2 = (np.linalg.norm(b - guess), tau)
    v = np.array([best[1], best2[1]])
    for _ in range(iters):
        r = eqs(v)
        if r is None: return None
        if np.linalg.norm(r) < tol: break
        J = np.zeros((2, 2))
        for i in range(2):
            h = 1e-9 * max(1.0, abs(v[i])); e = np.zeros(2); e[i] = h
            rp, rm = eqs(v + e), eqs(v - e)
            if rp is None or rm is None: return None
            J[:, i] = (rp - rm) / (2 * h)
        v = v - np.linalg.solve(J, r)
    r = eqs(v)
    if r is None or np.linalg.norm(r) > 1e-10: return None
    h = H._iter(Fw, np.asarray(p) + v[0] * np.asarray(eu), ku)
    return dict(t=float(v[0]), tau=float(v[1]), h=h, residual=float(np.linalg.norm(r)))


def _jac_at(p, eu, q, es, ku, ks, v):
    """the refine Newton system's FD Jacobian at v, by refine_connection's own formula (data only)"""
    Fw = lambda w: (H.P(w, 1) or (None,))[0]
    def eqs(v):
        a = H._iter(Fw, np.asarray(p) + v[0] * np.asarray(eu), ku)
        b = H._iter(H.Pinv, np.asarray(q) + v[1] * np.asarray(es), ks)
        return None if a is None or b is None else a - b
    J = np.zeros((2, 2))
    for i in range(2):
        h = 1e-9 * max(1.0, abs(v[i])); e = np.zeros(2); e[i] = h
        rp, rm = eqs(v + e), eqs(v - e)
        if rp is None or rm is None: return None
        J[:, i] = (rp - rm) / (2 * h)
    return J


def step3(system, z, eu, es, c, arm_lam=None):
    """B15c §2. Returns a record; record['stop'] is None or 'step 3: refinement failed'."""
    use_system(system)
    ku, ks = abs(int(c["k_u"])), abs(int(c["k_s"]))
    su, ss = (int(np.sign(c["k_u"])) or 1), (int(np.sign(c["k_s"])) or 1)
    z, eu, es = (np.asarray(v, float) for v in (z, eu, es))
    rec = dict(system=system, k_u=ku, k_s=ks, s_u=su, s_s=ss, arm=(arm_lam is not None))
    if arm_lam is None:
        r = H.refine_connection(z, su * eu, z, ss * es, ku, ks, np.asarray(c["point"], float))
    else:
        r = refine_connection_scaled(z, su * eu, z, ss * es, ku, ks, np.asarray(c["point"], float), arm_lam)
    if r is None:
        rec["stop"] = "step 3: refinement failed"; return rec
    t, tau = r["t"], r["tau"]; m = ku + ks
    J = _jac_at(z, su * eu, z, ss * es, ku, ks, np.array([t, tau]))
    X, U, S = [], [], []
    for j in range(m + 1):
        w, u = H.tangent_fwd(z, su * eu, t, j); X.append(w); U.append(u)
        S.append(H.tangent_back(z, ss * es, tau, m - j)[1])
    rec.update(stop=None, t=t, tau=tau, residual=r["residual"], m=m,
               J=(J.tolist() if J is not None else None), condJ=(float(np.linalg.cond(J)) if J is not None else None),
               dist_h_saddle=float(np.linalg.norm(np.asarray(r["h"]) - z)),
               end_gap=float(np.linalg.norm(X[m] - (z + tau * ss * es))),
               X=[x.tolist() for x in X], U=[u.tolist() for u in U], S=[s.tolist() for s in S])
    if system == "kerr":
        dq = [abs(float(H.px_of(*x)) ** 2 - Q_S) for x in X]
        rec.update(dQ_end=dq[m], dQ_max=max(dq))
    return rec


# ---------------------------------------------------------------------------------------------- step 4 (B15c §3)
def ladder(system, z, eu, es, X, U, S, swap=False, stop_at_first=True):
    """B14's ladder as hs_construct_hh_chain2.py builds it; acceptance on the REQUIRED coverings only.
    swap=True exchanges the frame vectors in EVERY set (the planted reject, control 3)."""
    use_system(system)
    z, eu, es = (np.asarray(v, float) for v in (z, eu, es))
    X = [np.asarray(x, float) for x in X]; U = [np.asarray(u, float) for u in U]; S = [np.asarray(s, float) for s in S]
    if swap:
        eu, es = es, eu; U, S = S, U
    m = len(X) - 1; entries = []
    for a0, a, bf0, bf in LADDER:
        N0 = (z, a0 * eu, bf0 * a0 * es)
        idx = [j for j in range(1, m) if H.disjoint(N0, (X[j], a * U[j], bf * a * S[j]))]
        if not idx: continue
        j1, j2 = idx[0], idx[-1]
        chain = list(range(j1, j2 + 1))
        if chain != idx: continue
        N = {0: N0}; N.update({j: (X[j], a * U[j], bf * a * S[j]) for j in chain})
        if not all(H.disjoint(N[i], N[j]) for i in N for j in N if i < j): continue
        req = [(0, 0), (0, j1)] + [(j, j + 1) for j in chain[:-1]] + [(j2, 0)]
        opt = [(j2, j1)]
        det = {f"{i}>{j}": H.sampled_cover(N[i], N[j], n_edge=12, n_int=8) for i, j in req + opt}
        ok = {k: bool(v and v["ok"]) for k, v in det.items()}
        n_ok = sum(ok[f"{i}>{j}"] for i, j in req)
        e = dict(a0=a0, a=a, bf0=bf0, bf=bf, chain=chain, n_ok_required=n_ok, n_required=len(req),
                 failing=[k for k, v in ok.items() if not v], optional_ok=ok[f"{j2}>{j1}"],
                 accepted=(n_ok == len(req)), detail=det)
        entries.append(e)
        if e["accepted"] and stop_at_first: break
    acc = next((e for e in entries if e["accepted"]), None)
    return dict(stop=(None if acc else "step 4: no ladder entry"), accepted=acc, entries=entries)


# ---------------------------------------------------------------------------------------------- rigorous specs (B15c §4)
def q(x):
    x = F(x); return f"{x.numerator}/{x.denominator}"


def R10(v):
    return F(round(float(v) * 10 ** 10), 10 ** 10)


def exact_sets(z, eu, es, X, U, S, entry, swap=False, rot90=None):
    """hs_run.hh2's rationalisation. rot90: None, 'U' (rotate U only), or 'US' (R1's W2: both)."""
    a0, a, bf0, bf, chain = entry["a0"], entry["a"], entry["bf0"], entry["bf"], entry["chain"]
    sets = {"N0": ([R10(v) for v in z], [R10(a0 * v) for v in eu], [R10(bf0 * a0 * v) for v in es])}
    for j in chain:
        sets[f"N{j}"] = ([R10(v) for v in X[j]], [R10(a * v) for v in U[j]], [R10(bf * a * v) for v in S[j]])
    if swap:
        sets = {k: (c, Ss, Uu) for k, (c, Uu, Ss) in sets.items()}
    if rot90:
        rot = lambda v: [-v[1], v[0]]
        sets = {k: (c, rot(Uu), (rot(Ss) if rot90 == "US" else Ss)) for k, (c, Uu, Ss) in sets.items()}
    return sets


def _corners(c, U, S):
    return [tuple(c[k] + su * U[k] + ss * S[k] for k in range(2)) for su, ss in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def convex_disjoint(P, Q):
    for poly in (P, Q):
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            n = (y2 - y1, x1 - x2)
            pa = [n[0] * x + n[1] * y for x, y in P]; pb = [n[0] * x + n[1] * y for x, y in Q]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return True
    return False


def s8(sets):
    names = sorted(sets)
    return {f"{x}|{y}": convex_disjoint(_corners(*sets[x]), _corners(*sets[y])) for i, x in enumerate(names) for y in names[i + 1:]}


def tset(name, c, U, S):
    det = U[0] * S[1] - S[0] * U[1]
    if det == 0:
        return None
    A = ((S[1] / det, -S[0] / det), (-U[1] / det, U[0] / det))
    return "tset " + name + " " + " ".join(q(v) for v in (*c, *U, *S, A[0][0], A[0][1], A[1][0], A[1][1]))


def specs(system, sets, entry, ckdir):
    """{tag: spec text} for the required + optional coverings; None if S8 fails or a frame is singular."""
    ok8 = s8(sets)
    if not all(ok8.values()):
        return dict(stop="S8", s8=ok8)
    T = [tset(k, *v) for k, v in sets.items()]
    if any(t is None for t in T):
        return dict(stop="singular frame", s8=ok8)
    chain = entry["chain"]; j1, j2 = chain[0], chain[-1]
    req = [("N0", "N0"), ("N0", f"N{j1}")] + [(f"N{j}", f"N{j + 1}") for j in chain[:-1]] + [(f"N{j2}", "N0")]
    opt = [(f"N{j2}", f"N{j1}")]
    head = KERR_HEAD if system == "kerr" else HH_HEAD
    out = {}
    for x, y in req + opt:
        body = head + T + RIG_BODY
        key = hashlib.sha256(("\n".join(body + [f"cover {x} {y} 16 16 64"]) + "\n").encode()).hexdigest()[:16]
        out[f"{x}{y}"] = "\n".join(body + [f"checkpoint {Path(ckdir) / f'{x}{y}_{key}.ckpt'}", f"cover {x} {y} 16 16 64"]) + "\n"
    return dict(stop=None, s8=ok8, required=[f"{x}{y}" for x, y in req], optional=[f"{x}{y}" for x, y in opt], specs=out)


def write_specs(chains, spec_dir=None, dry_run=False):
    """chains: [(chain_id, system, exact sets, accepted entry)] in tier order. A chain whose spec set is byte-identical to
    an earlier chain's is a 'duplicate' of it (B15c §1) and gets no specs of its own."""
    seen, out, n = {}, {}, 0
    for cid, system, sets, entry in chains:
        r = specs(system, sets, entry, (spec_dir or OUT / "ckpt") / cid)
        if r["stop"]:
            out[cid] = dict(status=r["stop"], s8=r["s8"]); continue
        # the checkpoint path carries the chain id; compare the spec text with it removed
        key = hashlib.sha256("".join(re.sub(r"^checkpoint .*$", "", r["specs"][k], flags=re.M) for k in sorted(r["specs"])).encode()).hexdigest()
        if key in seen:
            out[cid] = dict(status="duplicate", of=seen[key]); continue
        seen[key] = cid
        out[cid] = dict(status="specs", required=r["required"], optional=r["optional"], key=key)
        if not dry_run:
            d = (spec_dir or OUT / "specs") / cid; d.mkdir(parents=True, exist_ok=True)
            (OUT / "ckpt" / cid).mkdir(parents=True, exist_ok=True)
            for tag, text in r["specs"].items():
                (d / f"{tag}.spec").write_text(text)
        n += len(r["specs"])
    out["n_specs_written"] = n
    return out


# ---------------------------------------------------------------------------------------------- classification (B15c §4, B15c-1)
def classify(lines):
    """one covering's hs_cover stdout -> CERTIFIED / CERTIFIED-FAIL / UNDECIDED / HARNESS-ERROR"""
    lines = [l.rstrip("\n") for l in lines]
    done = "DONE" in lines
    fatal = any(l.startswith("FATAL") for l in lines)
    cov = [l for l in lines if l.startswith("COVER ")]
    covers1 = any(re.search(r"(^|\s)COVERS=1(\s|$)", l) for l in cov)
    orient_cf = any(re.search(r"(^|\s)orient_certified_fail=1(\s|$)", l) for l in cov)
    fp_cert = any(l.startswith("FAILPIECE") and re.search(r"\sCERTIFIED(\s|$)", l) for l in lines)
    if covers1 and (fp_cert or orient_cf):
        return "HARNESS-ERROR"
    if len(cov) > 1:
        return "HARNESS-ERROR"                          # one covering per spec; two COVER lines is a harness fault
    if fatal or not done or not cov:
        return "UNDECIDED"
    if covers1:
        return "CERTIFIED"
    if fp_cert or orient_cf:
        return "CERTIFIED-FAIL"
    return "UNDECIDED"


def chain_class(required_classes):
    if any(c == "HARNESS-ERROR" for c in required_classes):
        return "HARNESS-ERROR"
    if required_classes and all(c == "CERTIFIED" for c in required_classes):
        return "RHO>1"
    if any(c == "CERTIFIED-FAIL" for c in required_classes):
        return "CERTIFIED-FAIL"
    return "UNDECIDED"


STAGES = ["step 3: refinement failed", "step 4: no ladder entry", "S8", "UNDECIDED", "CERTIFIED-FAIL", "RHO>1", "duplicate"]


def headline(chains):
    """chains: {tier: [final status strings]} (a status is one of STAGES, or HARNESS-ERROR). B15c §5's headline."""
    lines = []
    for tier, st in chains.items():
        cnt = {s: st.count(s) for s in STAGES + ["HARNESS-ERROR"]}
        lines.append(f"{tier}: " + " / ".join(f"{s} {cnt[s]}" for s in STAGES) + (f" / HARNESS-ERROR {cnt['HARNESS-ERROR']}" if cnt["HARNESS-ERROR"] else ""))
    allst = [s for st in chains.values() for s in st]
    if any(s == "RHO>1" for s in allst):
        verdict = "F7 STOP: a rigorous rho > 1 on Kerr"
    elif any(s == "HARNESS-ERROR" for s in allst):
        verdict = "INVALID: HARNESS-ERROR (no reading)"
    else:
        n = allst.count("CERTIFIED-FAIL")
        t1 = chains.get("T1", ["(not run)"])[0] if chains.get("T1") else "(not run)"
        verdict = (f"B15 prediction: supported by {n} chains (T1: {t1})" if n else f"B15 prediction: NOT TESTED (T1: {t1})")
    return "\n".join(lines + [verdict])


# ---------------------------------------------------------------------------------------------- counted constructor stage
SEAL_DIR = HERE.parent.parent / "scratch" / "b15c"     # gitignored (qsim/scratch); the run list with planted entries
CONTROLS_PASS = OUT / "controls_PASS.json"


def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def kerr_saddle():
    """B15 step 1 recomputed through the frozen constructor (deterministic map): z must equal the recorded z bit for bit."""
    use_system("kerr")
    rec = json.loads((KERR / "b15_kerr_rust.json").read_text())
    r = H.find_periodic(np.array(rec["seed"]), 1, iters=10, tol=1e-10)
    if r is None:
        raise SystemExit("HARNESS-ERROR: step 1 recompute did not converge")
    z, D = r
    if z.tolist() != rec["step1"]["z"]:
        raise SystemExit("HARNESS-ERROR: step 1 recompute z %r differs from the recorded %r" % (z.tolist(), rec["step1"]["z"]))
    si = H.saddle_info(D)
    return rec, z, si


def hh_pi4():
    ex = json.loads((RES / "construct" / "hh_explore.json").read_text())
    s = ex["saddles"]["Pi4"]
    c = sorted(ex["crossings"]["Pi4->Pi4"], key=lambda c: (abs(c["k_u"]) + abs(c["k_s"]), -c["angle"]))[0]
    return np.array(s["z"]), np.array(s["e_u"]), np.array(s["e_s"]), c


def run_candidate(item, ctx):
    """one entry of a tier's run list -> its record. MapCheckFailed is NOT caught here (the caller stops the run)."""
    kind = item["kind"]
    if kind == "kerr":
        c = ctx["crossings"][item["n"]]
        s3 = step3("kerr", ctx["z"], ctx["e_u"], ctx["e_s"], c, arm_lam=ctx.get("arm_lam"))
        rec = dict(id=item["id"], kind=kind, n=item["n"], angle=c["angle"], step3=s3)
        if s3["stop"]:
            rec["stop"] = s3["stop"]; return rec
        lad = ladder("kerr", ctx["z"], ctx["e_u"], ctx["e_s"], s3["X"], s3["U"], s3["S"])
    elif kind == "hh_swap":                              # planted reject, primary (control 3)
        z, eu, es, c = hh_pi4()
        s3 = step3("hh", z, eu, es, c); rec = dict(id=item["id"], kind=kind, step3=dict(stop=s3["stop"]))
        if s3["stop"]:
            rec["stop"] = "HARNESS-ERROR: HH refinement failed"; return rec
        lad = ladder("hh", z, eu, es, s3["X"], s3["U"], s3["S"], swap=True)
    elif kind == "kerr_t1_swap":                         # planted reject, extra (not deciding)
        t1 = json.loads((OUT / "T1.json").read_text())["records"][0]
        rec = dict(id=item["id"], kind=kind, from_t1_stop=t1.get("stop"))
        if t1["step3"]["stop"]:
            rec["stop"] = "not constructible (T1 stopped at step 3)"; return rec
        s3 = t1["step3"]
        lad = ladder("kerr", ctx["z"], ctx["e_u"], ctx["e_s"], s3["X"], s3["U"], s3["S"], swap=True)
    else:
        raise SystemExit("HARNESS-ERROR: unknown run-list kind %r" % kind)
    rec["ladder"] = lad; rec["stop"] = lad["stop"]
    return rec


def constructor(tier):
    if not CONTROLS_PASS.exists():
        raise SystemExit("REFUSED: b15c_controls.py has not PASSED (B15c §6)")
    cp = json.loads(CONTROLS_PASS.read_text())
    if cp.get("driver_sha256") != file_sha(__file__) or cp.get("verdict") != "PASS":
        raise SystemExit("REFUSED: controls PASS was for a different driver (sha) or not a PASS")
    import kerr_compiled as KC
    kerr_setup()
    rec, z, si = kerr_saddle()
    crossings = rec["step2"]["crossings"]
    acc = json.loads((KERR / "b15_g6_summary.json").read_text())["accepts"]
    T = tiers(crossings, acc)
    ctx = dict(crossings=crossings, z=z, e_u=si["e_u"], e_s=si["e_s"])
    if tier == "ARM":
        t1 = json.loads((OUT / "T1.json").read_text())
        if t1["records"][0].get("stop") != "step 3: refinement failed":
            raise SystemExit("REFUSED: the diagnostic arm runs only if T1 stopped at refinement (B15c §4)")
        ctx["arm_lam"] = abs(float(si["lam_u"]))
        items = [dict(id="ARM-T1", kind="kerr", n=T["T1"][0])]
    elif tier == "T2":
        items = json.loads((SEAL_DIR / "T2_runlist.json").read_text())      # written by b15c_controls.py --seal
        plain = [it["n"] for it in items if it["kind"] == "kerr"]
        if plain != T["T2"]:
            raise SystemExit("HARNESS-ERROR: the sealed T2 run list's Kerr entries are not B14's T2 order")
    else:
        items = [dict(id=f"{tier}-{k}", kind="kerr", n=n) for k, n in enumerate(T[tier])]
    path = OUT / f"{tier}.json"
    done = json.loads(path.read_text()) if path.exists() else dict(tier=tier, records=[])
    have = {r["id"] for r in done["records"]}
    done.update(driver_sha256=file_sha(__file__), lib_sha256=_KERR["lib_sha"], delta_floor=_KERR["delta_floor"],
                saddle=dict(z=z.tolist(), lam_u=float(si["lam_u"]), e_u=si["e_u"].tolist(), e_s=si["e_s"].tolist()),
                unfrozen_not_counted=(tier == "ARM"))
    t0 = time.time()
    for it in items:
        if it["id"] in have:
            continue
        try:
            r = run_candidate(it, ctx)
        except KC.MapCheckFailed as e:
            done["harness_error"] = dict(id=it["id"], error=str(e))
            path.write_text(json.dumps(done, indent=1, default=float))
            raise SystemExit("HARNESS-ERROR at %s: %s (run stopped; nothing recorded as a rejection)" % (it["id"], e))
        r["seconds"] = round(time.time() - t0, 1)
        done["records"].append(r)
        tmp = path.with_suffix(".tmp"); tmp.write_text(json.dumps(done, indent=1, default=float)); os.replace(tmp, path)
        print("%s %s: %s (%.0f s)" % (tier, it["id"], r["stop"] or "LADDER ACCEPTED", r["seconds"]), flush=True)
    done["complete"] = True
    path.write_text(json.dumps(done, indent=1, default=float))
    print("%s complete: %d records" % (tier, len(done["records"])), flush=True)


if __name__ == "__main__":
    {"constructor": lambda: constructor(sys.argv[2])}[sys.argv[1]]()
