"""Amendment C1-R control-1 verdict (PREREG_cuspis_sub45_check.md 9f142e6 + f8c94b3). Bridge transcription check passed.
Mine: the committed Stage-1 v3 value (chl_controls_run.json, fine resolution, theta = pi/2). Reference: the CONSERVATIVE
real-scalar interval from chl_c1r_reference.json. PASS iff rel <= 2.1e-4 (rel = 0 inside; else distance to nearer end / L)."""
import json, os
from mpmath import mp, mpf
mp.dps = 30
HERE = os.path.dirname(os.path.abspath(__file__))
mine = mpf(json.load(open(os.path.join(HERE, "chl_controls_run.json")))["resolutions"]["fine"]["values"]["1.570796326795"])
ref = json.load(open(os.path.join(HERE, "chl_c1r_reference.json")))["real_scalar"]
L, U = (mpf(v) for v in ref["conservative"])
tL, tU = (mpf(v) for v in ref["tight"])
rel = mpf(0) if L <= mine <= U else min(abs(mine - L), abs(mine - U))/L
TOL = mpf("2.1e-4")
out = dict(mine=mp.nstr(mine, 15), conservative=[mp.nstr(L, 15), mp.nstr(U, 15)], inside_conservative=bool(L <= mine <= U),
           rel=mp.nstr(rel, 6), tol=str(TOL), verdict="PASS" if rel <= TOL else "FAIL",
           tight=[mp.nstr(tL, 15), mp.nstr(tU, 15)], inside_tight=bool(tL <= mine <= tU),
           position_in_conservative=mp.nstr((mine - L)/(U - L), 6),
           label="passed under an amendment adopted after a documented control failure" if rel <= TOL else "failed under amendment C1-R")
json.dump(out, open(os.path.join(HERE, "chl_c1r_verdict.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
