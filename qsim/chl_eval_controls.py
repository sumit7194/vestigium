"""
Judge the stage-1 run against the known answers -- POISON FIRST, tolerances fixed
here BEFORE the run's numbers are read (written while the run was in progress).

Tolerances come from the SOURCE's printed precision, never from the run:
  c2 = 1/256 exact            -> limited by our own quadrature: 1e-7
  c4 = (20+3pi^2)/(18432pi^2) -> exact; 1e-6
  c6 = 5.34656e-5/2           -> 6 printed figures: half-ulp 1e-6 relative -> 2e-6
  s(pi/2)  = 0.02366/2        -> 4 figures: 2.1e-4 (the pre-registered control 1)
  s(3pi/4) = 0.005040/2       -> 4 figures: 1e-4 relative half-ulp -> 2e-4
  BWK16 bound at both angles  -> must hold, no tolerance
and the two quadrature resolutions must agree to 1e-7, or no value is reported.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chl_controls as C

PI = math.pi
run = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "chl_controls_run.json")))
res = run["resolutions"]
lo, hi = res["12x16"], res["16x24"]
for r in (lo, hi):
    if r["missing"]:
        raise SystemExit(f"INCOMPLETE: {len(r['missing'])} nodes missing or failed -- no control is judged")

def val(r, name):
    if name in ("c2", "c4", "c6"):
        return r["values"][name]
    x = {"s90": PI/2, "s135": 3*PI/4}[name]
    return r["values"][f"{x:.12f}"]

print("CONVERGENCE (two resolutions must agree before anything is judged):")
conv_ok = True
for n in ["c2", "c4", "c6", "s90", "s135"]:
    a, b = val(lo, n), val(hi, n)
    d = abs(a - b)/abs(b)
    ok = d < 1e-7
    conv_ok &= ok
    print(f"   {n:>5}: 12x16 {a:.12e}   16x24 {b:.12e}   rel diff {d:.1e}  {'ok' if ok else 'NOT CONVERGED'}")
print("t-tail bounds (beyond t = 3):", {k: f"{v:.1e}" for k, v in hi["t_tail_bound"].items()})
if not conv_ok:
    raise SystemExit("quadrature not converged -- controls not judged")

print("\nCONTROLS (each rejects its own poison before its verdict counts):")
checks = [
    C.make_known_value_control(PI/2, 0.02366/2, 2.1e-4, "CHL09 Table 1 / 2"),
    C.make_known_value_control(3*PI/4, 0.005040/2, 2e-4, "CHL09 Table 1 / 2"),
    C.make_bound_control(PI/2),
    C.make_bound_control(3*PI/4),
]
values = [val(hi, "s90"), val(hi, "s135"), val(hi, "s90"), val(hi, "s135")]
smooth = [("c2 = sigma", 1/256, 1e-7, "exact; Elvang-Hadjiantonis 2015"),
          ("c4", (20 + 3*PI**2)/(18432*PI**2), 1e-6, "exact; Helmes et al. 2016 Table 3 / 2"),
          ("c6", 5.34656e-5/2, 2e-6, "CHL09 Table 1 / 2")]
for nm, ref, tol, src in smooth:
    def chk(v, ref=ref, tol=tol, src=src, nm=nm):
        rel = abs(v - ref)/abs(ref)
        if rel > tol:
            raise C.ControlFailed(f"{nm} = {v:.10e} vs {ref:.10e} [{src}]: rel {rel:.2e} > {tol:.0e}")
        return f"{nm} = {v:.12e} vs {ref:.12e} [{src}], rel {rel:.2e} <= {tol:.0e}"
    checks.append(C.Control(nm, "smooth end", chk, lambda v, ref=ref, tol=tol: ref*(1 + 1.1*tol)))
    values.append(val(hi, nm.split()[0]))

allpass = True
for ctrl, v in zip(checks, values):
    try:
        detail, poison = ctrl.validate(v)
        print(f"  PASS  {ctrl.name}\n        {detail}\n        (first {poison})")
    except C.ControlFailed as e:
        allpass = False
        print(f"  FAIL  {ctrl.name}\n        {e}")
print("\nSTAGE 1:", "ALL CONTROLS PASS -- stage 2 (small-angle controls) may proceed" if allpass
      else "A CONTROL FAILED -- the instrument is not validated; nothing below 45 deg is reportable")
