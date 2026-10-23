"""B17 checkpoint data for one W0 (PREREG B17), from the centre orbit and point sampling only (no sets):
for every TIME checkpoint t_c:
  u1, u2 (left singular vectors of Phi(t_c, 0) D_in), n_H (unit grad H), as 8-vectors (aux entries 0: 4-D projection);
  true widths along u1, u2: hull of the images of n_b boundary points of the W0 box (DOP853 1e-13), projected;
  gains to the next checkpoint: 4-D variational for u1, u2, n_H; 8-D augmented variational (mn_codegen8 field, on the
  manifold) for the off-manifold directions e_q - grad q(x, y)  (q = a, b, E2, eG).
For the SECTION checkpoints (first y = 0 crossing with ydot < 0; the return to y = 0 with ydot > 0) the same quantities
are written at the centre's crossing time; the set side measures the section enclosure (diagnostic code).
Interpretation logged here (not a change to B17): at the final Sigma return there is no further propagation within the
return, so the fake-direction rule there uses g = 1.
Usage: b17_checkpoints.py W0 out.json [n_boundary_per_edge]"""
import sys, json, numpy as np, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_numerics as MNN
import mn_codegen as CG
import mn_codegen8 as C8
from scipy.integrate import solve_ivp

W0 = float(sys.argv[1]); OUT = sys.argv[2]; NB = int(sys.argv[3]) if len(sys.argv) > 3 else 4
T = json.load(open("/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/mn_smoke/b17_times.json"))
tp1, tp2 = T["t_periapsis"]; ts1, ts2 = (s["t_star"] for s in T["swings"])
cps = [("t", tp1 - 7), ("t", ts1), ("t", tp1 + 1), ("t", tp1 + 5), ("sec_down", T["t_y0_down"]),
       ("t", tp2 - 7), ("t", ts2), ("t", tp2 + 1), ("t", tp2 + 5), ("sec_return", T["t_return"])]
times = [c[1] for c in cps]

f = MNN.MNFlow(89, 80, sp.Rational(13394411, 1186380), sp.Rational(19, 20), sp.Integer(267))
x0, px0 = 3.6419361737, 6.0360992808; py0 = f.py_of(x0, px0)
f0 = np.array(f._f(x0, 0.0, px0, py0), float); Hx, Hpx, Hpy = -f0[2], f0[0], f0[1]
D_in = np.array([[1, 0], [0, 0], [0, 1], [-Hx / Hpy, -Hpx / Hpy]])
sv = solve_ivp(f.rhs, (0, times[-1]), np.concatenate([[x0, 0, px0, py0], np.eye(4).ravel()]), method="DOP853",
               rtol=1e-13, atol=1e-13, dense_output=True)

# boundary-point images (true hull)
pts = []
for i in range(NB):
    s_ = -1 + 2 * i / NB
    pts += [(-1, s_), (s_, 1), (1, -s_), (-s_, -1)]
traj = []
for u, s in pts:
    x, px = x0 + u * W0, px0 + s * W0; py = f.py_of(x, px)
    traj.append(solve_ivp(f.rhs, (0, times[-1]), [x, 0, px, py], method="DOP853", rtol=1e-13, atol=1e-13, t_eval=times).y)
traj = np.array(traj)                                     # (npts, 4, ncp)

# 8-D augmented field and Jacobian (parameters substituted), for off-manifold gains
F8, p8 = C8.build8()
vals = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
F8v = [e.subs(vals) for e in F8]
J8 = sp.lambdify(C8.STATE, sp.Matrix(F8v).jacobian(C8.STATE), "numpy", cse=True)
f8 = sp.lambdify(C8.STATE, F8v, "numpy", cse=True)
aux = sp.lambdify([CG.x, CG.y], [e.subs(vals) for e in p8["aux"]], "numpy")
gaux = sp.lambdify([CG.x, CG.y], [[sp.diff(e.subs(vals), v) for v in (CG.x, CG.y)] for e in p8["aux"]], "numpy")
def rhs8(t, s):
    z = s[:8]; Phi = s[8:].reshape(8, 8)
    return np.concatenate([np.array(f8(*z), float), (np.array(J8(*z), float) @ Phi).ravel()])

# section crossings of the boundary points (for the SECTION checkpoints): first crossing in the stated direction
def crossing(z0, direction, t_after, t_near):
    ev = lambda t, s: s[1]; ev.direction = direction
    so = solve_ivp(f.rhs, (0, t_near + 50), z0, method="DOP853", rtol=1e-13, atol=1e-13, events=ev)
    ok = [k for k, t in enumerate(so.t_events[0]) if t > t_after]
    k = min(ok, key=lambda k: abs(so.t_events[0][k] - t_near)); return so.y_events[0][k]
rec = []
for j, (kind, tc) in enumerate(cps):
    P = sv.sol(tc)[4:].reshape(4, 4); zc = sv.sol(tc)[:4]
    fc = np.array(f._f(*zc), float); nH = np.array([-fc[2], -fc[3], fc[0], fc[1]]); nH /= np.linalg.norm(nH)
    if kind == "t":
        U, S, Vt = np.linalg.svd(P @ D_in, full_matrices=False)
        dirs4 = {"u1": U[:, 0], "u2": U[:, 1], "nH": nH}
        true = {k: float(np.ptp(traj[:, :, j] @ dirs4[k])) for k in ("u1", "u2")}
    else:                                                    # section: derivative of the crossing state, flow-corrected
        dirn = -1.0 if kind == "sec_down" else 1.0
        V = P @ D_in; V = V - np.outer(fc, V[1] / fc[1])     # slide along the flow back to y = 0
        U, S, Vt = np.linalg.svd(V, full_matrices=False)
        dirs4 = {"u1": U[:, 0], "u2": U[:, 1], "nH": nH}
        cz = np.array([crossing([x0 + u * W0, 0, px0 + s * W0, f.py_of(x0 + u * W0, px0 + s * W0)], dirn, 1.0, tc) for u, s in pts])
        true = {k: float(np.ptp(cz @ dirs4[k])) for k in ("u1", "u2")}
    if j + 1 < len(cps):
        tn = cps[j + 1][1]; Pn = sv.sol(tn)[4:].reshape(4, 4); Pjn = Pn @ np.linalg.inv(P)
        g4 = {k: float(np.linalg.norm(Pjn @ v)) for k, v in dirs4.items()}
        a0 = np.array(aux(zc[0], zc[1]), float)
        s8 = solve_ivp(rhs8, (tc, tn), np.concatenate([zc, a0, np.eye(8).ravel()]), method="DOP853", rtol=1e-11, atol=1e-13)
        Phi8 = s8.y[8:, -1].reshape(8, 8)
        ga = np.array(gaux(zc[0], zc[1]), float)
        goff = {}
        for q, nm in enumerate(("a", "b", "E2", "eG")):
            d = np.zeros(8); d[4 + q] = 1                        # an off-manifold displacement at fixed (x, y, p)
            goff[nm] = float(np.linalg.norm(Phi8 @ d))
    else:
        g4 = {k: 1.0 for k in dirs4}; goff = {nm: 1.0 for nm in ("a", "b", "E2", "eG")}
    rec.append(dict(kind=kind, t=float(tc), dirs={k: list(map(float, list(v) + [0, 0, 0, 0])) for k, v in dirs4.items()},
                    true=true, gain=dict(g4, **goff), centre=list(map(float, zc))))
    print("%-10s t=%9.4f  true u1 %.3e u2 %.3e | gains u1 %.2e u2 %.2e nH %.2e a %.2e b %.2e E2 %.2e eG %.2e" % (
        kind, tc, true["u1"], true["u2"], g4["u1"], g4["u2"], g4["nH"], goff["a"], goff["b"], goff["E2"], goff["eG"]), flush=True)
json.dump(dict(W0=W0, n_boundary=len(pts), checkpoints=rec), open(OUT, "w"), indent=1)
with open(OUT.replace(".json", ".txt"), "w") as fh:                # plain text for the C++ checker
    for r in rec:
        fh.write("%s %.17e\n" % (r["kind"], r["t"]))
        for k in ("u1", "u2", "nH"): fh.write(" ".join("%.17e" % v for v in r["dirs"][k]) + "\n")
        fh.write("%.17e %.17e\n" % (r["true"]["u1"], r["true"]["u2"]))
        fh.write(" ".join("%.17e" % r["gain"][k] for k in ("u1", "u2", "nH", "a", "b", "E2", "eG")) + "\n")
        fh.write(" ".join("%.17e" % v for v in r["centre"]) + "\n")
