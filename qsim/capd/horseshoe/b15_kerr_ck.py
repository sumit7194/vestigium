"""B15 (prereg): strong Kerr negative control. CHECKPOINTED copy of b15_kerr.py (identical maths; P/Pinv journalled by pcache.py).
 Kerr (89, 80, q = 0), E = 49/50, L_z = 445/2; FROZEN B14 constructor
(hs_construct.py, unedited) plugged in with mn_numerics. Steps 1-2 always; crossings recorded with their angle and
local discretisation floor theta_floor = kappa*(l_u + l_s); red flag = angle > 10 * floor. Steps 3-4 only if step 2
returns an accepted connection (B14: min angle 0.01). Non-rigorous stage; writes horseshoe_results/kerr/b15_*.json."""
import json, time, numpy as np, sympy as sp
from pathlib import Path
import mn_numerics as MNN

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr"; OUT.mkdir(exist_ok=True)
TMAX = 1e6                                   # the homoclinic swings out to r = 46.8 M: returns are long
t0 = time.time()
import os, hashlib, pcache
MAP = os.environ.get("B15_MAP", "mnflow")    # B15b (registered): "rust" = the compiled kerr_rs map; default MNFlow, unchanged
if MAP == "rust":
    # B15b / B15b-1 (registered 2026-10-24): kerr_rs behind MNFlow's interface; gates G0-G5 PASSED before this run
    # (G1/G3/G4 + G4c: 9e6e6f1). delta_floor = max(1e-6, 100 x the largest G4-measured state error) for the plunge
    # certificate. NEW journal/JSON/arcs names: an MNFlow journal is never replayed into a rust run (pcache keys do not
    # name the map). A MapCheckFailed (-1, or an uncertified -2) is raised, never turned into None, and stops the run.
    import kerr_compiled as KC
    kerr = KC.CompiledFlow(KC.RUST)
    _g4 = json.loads((OUT / "b15b_gates" / "G1_G3_G4.json").read_text())["G4"]
    G4_ERR = max(r[n]["maxrel"] for r in _g4 for n in ("rust", "c++") if "maxrel" in r[n])
    kerr.delta_floor = max(1e-6, 100 * G4_ERR)
    LIBSHA = hashlib.sha256(Path(KC.RUST).read_bytes()).hexdigest()
    PLUNGES = OUT / os.environ.get("B15_PLUNGES", "b15_rust_plunges.jsonl")   # every certified plunge (G6 P5), appended as it happens
    _pl0 = kerr._plunge
    def _plunge_logged(kind, w, sign):
        r = _pl0(kind, w, sign); rec = dict(kerr.plunges[-1]); rec.update(kind=kind, w=[float(w[0]), float(w[1])])
        with open(PLUNGES, "a") as fh: fh.write(json.dumps(rec, default=float) + "\n"); fh.flush(); os.fsync(fh.fileno())
        return r
    kerr._plunge = _plunge_logged
    DEF = dict(journal="b15_rust.journal", json="b15_kerr_rust.json", arcs="b15_rust_arcs.npz")
elif MAP == "toy":                           # TEST ONLY (test_b15b_g6_run.py): the toy map of b15b_toyflow.py, never counted
    import b15b_toyflow; kerr = b15b_toyflow.ToyFlow(); log_seed = [0.0, 0.0]
    DEF = dict(journal="b15_wiring_test/toy.journal", json="b15_wiring_test/toy.json", arcs="b15_wiring_test/toy_arcs.npz")
else:
    kerr = MNN.MNFlow(89, 80, 0, sp.Rational(49, 50), sp.Rational(445, 2))
    DEF = dict(journal="b15_kerr.journal", json="b15_kerr_ck.json", arcs="b15_ck_arcs.npz")
H = MNN.plug_into_constructor(kerr)
H.P = lambda w, n=1, jac=False: kerr.P(w, n, jac, tmax=TMAX)
H.Pinv = lambda w: kerr.Pinv(w, tmax=TMAX)
J = pcache.Journal(str(OUT / os.environ.get("B15_JOURNAL", DEF["journal"])))   # crash-safe checkpoint of every finished map call
H = pcache.wrap(H, J)
log = dict(level=dict(M=89, a=80, q=0, E="49/50", L="445/2"), seed=[1.8411884397812655, 0.0], map=MAP)
if MAP == "toy": log["seed"] = [0.0, 0.0]
if MAP == "rust": log.update(lib=str(KC.RUST), lib_sha256=LIBSHA, delta_floor=kerr.delta_floor, g4_state_error=G4_ERR)


def save():
    log["seconds"] = time.time() - t0
    (OUT / os.environ.get("B15_JSON", DEF["json"])).write_text(json.dumps(log, indent=1, default=float))


# step 1: saddle
r = H.find_periodic(np.array(log["seed"]), 1, iters=10, tol=1e-10)   # call-site tol: this system's integration noise is ~1e-12
if r is None:
    log["step1"] = "no convergence"; save(); raise SystemExit("B15 step 1: Newton did not converge")
z, D = r; si = H.saddle_info(D)
log["step1"] = dict(z=z.tolist(), eigvals=[str(e) for e in np.linalg.eigvals(D)], saddle=bool(si),
                    lam_u=(float(si["lam_u"]) if si else None))
print("step 1:", log["step1"], "%.0fs" % (time.time() - t0), "journal hits/misses %d/%d" % (J.hits, J.misses), flush=True); save()
if os.environ.get("B15_STOP_AFTER_STEP1"): raise SystemExit(0)
if not si:
    raise SystemExit("B15 step 1: fixed point is not a saddle")
# step 2: manifolds and crossings, B14 parameters
au = H.manifold_arcs(z, si["e_u"], si["lam_u"], forward=True, K=5, eps=1e-4)
print("W^u arcs: %d pts %.0fs" % (sum(len(a) for _, a in au), time.time() - t0), flush=True)
as_ = H.manifold_arcs(z, si["e_s"], 1 / si["lam_s"], forward=False, K=5, eps=1e-4)
print("W^s arcs: %d pts %.0fs" % (sum(len(a) for _, a in as_), time.time() - t0), flush=True)
np.savez(OUT / os.environ.get("B15_ARCS", DEF["arcs"]), **{f"u_{k}_{i}": a for i, (k, a) in enumerate(au)}, **{f"s_{k}_{i}": a for i, (k, a) in enumerate(as_)})
allc = H.crossings(au, as_, min_angle=0.0, skip_near=[z])          # ALL crossings, for the data record


def floor_at(pt, arcs):
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


rec = []
for pt, ang, ku, ks in allc:
    fu, fs = floor_at(pt, au), floor_at(pt, as_)
    th = (fu[2] + fs[2]) / 2 * (fu[1] + fs[1]) if fu and fs else float("nan")
    rec.append(dict(point=pt.tolist(), angle=float(ang), k_u=int(ku), k_s=int(ks), theta_floor=float(th),
                    red_flag=bool(ang > 10 * th)))
acc = [c for c in rec if c["angle"] >= 0.01]
log["step2"] = dict(n_crossings_all=len(rec), n_at_or_above_0p01=len(acc),
                    min_angle=(min(c["angle"] for c in rec) if rec else None),
                    max_angle=(max(c["angle"] for c in rec) if rec else None),
                    n_red_flags=sum(c["red_flag"] for c in rec), crossings=rec)
print("step 2: %d crossings in all, %d with angle >= 0.01, %d red flags; angles [%s, %s]" % (
    len(rec), len(acc), log["step2"]["n_red_flags"], log["step2"]["min_angle"], log["step2"]["max_angle"]), flush=True)
log["verdict_constructor"] = ("STOPPED at step 2: no transverse connection (B14 threshold 0.01)" if not acc else
                              "step 2 returned candidate connections: steps 3-4 required (prediction: rigorous coverings give no rho > 1)")
if acc: log["scope_note"] = ("B15b-2: registered prediction NOT CONFIRMED because of an implementation scope limit (steps 3-4 not "
                             "implemented); this is not a negative result. Chord crossings are classified by G6 (b15b_g6.py).")
if MAP == "rust": log["plunges_certified"] = len(kerr.plunges)    # in this process (a resumed run: see the plunges file)
save(); print(log["verdict_constructor"])
