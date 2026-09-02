#!/usr/bin/env python3
"""Gate for the LRL secular-average instrument. Every assertion numeric, with
the known-fail controls marked. Run: python3 qsim/lrl_gate.py"""
import importlib.util, sys
import numpy as np
spec = importlib.util.spec_from_file_location("m", "qsim/lrl_secular.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

C = []
def check(name, v, op, b, kind="POS", note=""):
    C.append((name, float(v), op, float(b), kind, note))

# --- calibration: the instrument reproduces identities it was not fitted to
assert m.calibrate.__doc__
rng = np.random.default_rng(11)
w_h0 = w_so4 = 0.0
for _ in range(60):
    a, e, th = rng.uniform(0.7, 2.2), rng.uniform(0.1, 0.8), rng.uniform(0, 2*np.pi)
    rv, pv = m.kepler_state(a, e, th)
    s = np.linalg.norm(m.lrl(rv, pv))
    for i in range(3):
        w_h0 = max(w_h0, abs(m.pb_numeric(m.H0, lambda r, p, i=i: m.lrl(r, p)[i], rv, pv))/s)
    bAA = m.pb_numeric(lambda r, p: m.lrl(r, p)[0], lambda r, p: m.lrl(r, p)[1], rv, pv)
    pred = -2.0*m.H0(rv, pv)*np.cross(rv, pv)[2]
    w_so4 = max(w_so4, abs(bAA - pred)/abs(pred))
check("CALIB {H0,A}=0 pointwise", w_h0, "<", 1e-6, note="A conserved by unperturbed flow")
check("CALIB so(4) {A_x,A_y}=-2H0 L_z", w_so4, "<", 1e-6, note="non-degenerate algebra check")

perts = m.make_perts()
triv, pos = perts[0], perts[1]

# --- TRIVIAL control: the one people skip
w_tr, w_pt = 0.0, np.inf
for a in (0.8, 1.3, 2.0):
    for e in (0.1, 0.4, 0.7):
        w_tr = max(w_tr, np.linalg.norm(m.A_avg_theta(triv, a, e)))
        w_pt = min(w_pt, m.pointwise_nonzero(triv, a, e))
check("TRIVIAL dk/r: average vanishes on the grid", w_tr, "<", 1e-12,
      note="change of Kepler constant maps Kepler->Kepler")
check("TRIVIAL dk/r: bracket NONZERO pointwise [NEG]", w_pt, ">", 0.1, kind="NEG",
      note="if this were zero the control would test nothing")

# --- POSITIVE control against the analytic precession rate
w_an, w_rt = 0.0, 0.0
for a in (0.8, 1.3, 2.0):
    for e in (0.1, 0.4, 0.7):
        At = m.A_avg_theta(pos, a, e); Ao = m.A_avg_time(pos, a, e)
        An = m.A_analytic("r2", a, e)
        w_an = max(w_an, abs(At[1] - An[1])/abs(An[1]))
        w_rt = max(w_rt, abs(At[1] - Ao[1])/abs(At[1]))
check("POSITIVE beta/r^2 vs analytic precession", w_an, "<", 1e-6,
      note="2 pi beta e/(T a (1-e^2)), independently derivable from perihelion advance")
check("POSITIVE: theta-quadrature vs ODE time-average", w_rt, "<", 1e-6,
      note="two routes sharing no code path")
check("POSITIVE: nonzero on an OPEN SET, not a point [NEG]",
      min(abs(m.A_avg_theta(pos, a, e)[1]) for a in (0.8, 1.3, 2.0) for e in (0.1, 0.4, 0.7)),
      ">", 1e-3, kind="NEG", note="smallest value on the grid still far from zero")

# --- structural facts that were measured, not assumed
check("central perturbations: A_x = 0 by parity", 
      max(abs(m.A_avg_theta(p, 1.3, e)[0]) for p in (triv, pos) for e in (0.2, 0.6)),
      "<", 1e-12, note="test is blind to |A| drift for ANY central perturbation")
check("quadrature converges at e=0.99 [NEG-partner]",
      abs(m.A_avg_theta(pos, 1.3, 0.99, n=32001)[1]
          - m.A_avg_theta(pos, 1.3, 0.99, n=2001)[1])
      / abs(m.A_avg_theta(pos, 1.3, 0.99, n=32001)[1]),
      "<", 1e-10, note="no conditional convergence: the r^2 dtheta measure tames 1/r^n")

# --- the hidden hypothesis: the F1 bound is NOT uniform over the open set
f1 = {e: m.F1_amplitude(pos, 1.3, e) for e in (0.90, 0.95, 0.99)}
check("F1 bound NOT uniform in e [NEG]", f1[0.99]/f1[0.90], ">", 8.0, kind="NEG",
      note="lemma is applied on an open set; boundedness is per-orbit only")
c = [f1[e]*(1-e) for e in (0.90, 0.95, 0.99)]
check("F1 ~ C/(1-e), C constant", (max(c)-min(c))/np.mean(c), "<", 0.02,
      note="fixes the window at eps ~ (k/C) e (1-e)")

# --- dynamical: A is MINUS the secular rate, verified on the full system
rate, _, _ = m.measured_drift(pos, 1.3, 0.4, 0.0025, n_orb=480)
check("dynamical ratio vs -eps*A_avg at eps=2.5e-3",
      abs(rate/(-0.0025*m.A_avg_theta(pos, 1.3, 0.4)[1]) - 1.0), "<", 0.005,
      note="sign: dA/dt = -eps{H1,A}; O(eps) residual, halves as eps halves")

print("="*74)
print(f"LRL secular gate — {len(C)} assertions, {sum(1 for c in C if c[4]=='NEG')} negative")
print("="*74)
bad = 0
for n, v, op, b, kind, note in C:
    ok = v < b if op == "<" else v > b
    bad += not ok
    print(f"{'ok' if ok else '!!':3s}{n:<48}{v:11.3e}{op:>3}{b:9.3g}")
print("-"*74)
print("GREEN" if not bad else f"RED — {bad} failed")
sys.exit(1 if bad else 0)
