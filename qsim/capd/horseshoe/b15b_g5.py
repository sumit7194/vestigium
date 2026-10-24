"""B15b gate G5 (registered): end-to-end step 1 with kerr_rs through the frozen constructor.
The same call as b15_kerr_ck.py: plug_into_constructor(CompiledFlow(kerr_rs)), P with tmax 1e6, then
find_periodic(seed, 1, iters=10, tol=1e-10) and saddle_info. Criterion: z within 1e-9 of the recorded Python step 1
z = (1.8411884397812655, 0.0), and lam_u within 1e-8 relative of 62.62026858030255 (b15_kerr.json). A validation,
since the Python step 1 is known. Writes horseshoe_results/kerr/b15b_gates/G5.json; exit 0 iff PASS."""
import json, sys, numpy as np
from pathlib import Path
import kerr_compiled as K, mn_numerics as MNN

OUT = Path(__file__).resolve().parent.parent / "horseshoe_results" / "kerr" / "b15b_gates"
PY = json.loads((OUT.parent / "b15_kerr.json").read_text())["step1"]
TMAX = 1e6
f = K.CompiledFlow(K.RUST)
H = MNN.plug_into_constructor(f)
H.P = lambda w, n=1, jac=False: f.P(w, n, jac, tmax=TMAX)
H.Pinv = lambda w: f.Pinv(w, tmax=TMAX)
r = H.find_periodic(np.array([1.8411884397812655, 0.0]), 1, iters=10, tol=1e-10)
if r is None:
    res = dict(verdict="FAIL", reason="Newton did not converge")
else:
    z, D = r; si = H.saddle_info(D)
    dz = float(np.linalg.norm(np.asarray(z) - np.asarray(PY["z"]))); dl = abs(si["lam_u"] - PY["lam_u"]) / PY["lam_u"] if si else None
    ok = bool(si) and dz <= 1e-9 and dl <= 1e-8
    res = dict(z=list(map(float, z)), lam_u=float(si["lam_u"]) if si else None, eigvals=[str(e) for e in np.linalg.eigvals(D)],
               dz=dz, dlam_rel=dl, python_step1=PY, verdict="PASS" if ok else "FAIL")
(OUT / "G5.json").write_text(json.dumps(res, indent=1, default=float))
print("G5", res.get("verdict"), "dz %.3e dlam_rel %.3e" % (res.get("dz", float("nan")), res.get("dlam_rel") or float("nan")), "lam_u", res.get("lam_u"))
sys.exit(0 if res["verdict"] == "PASS" else 1)
