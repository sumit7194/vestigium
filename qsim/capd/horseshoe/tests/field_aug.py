"""DIAGNOSTIC ONLY: interval over-widening of the FIELD components (xdot, ydot, pxdot, pydot) in two forms, at one
point on a box of half-width h in all four coordinates (x, y, p_x, p_y):
  4-D : the generated form (mn_codegen.build()['field'], CSE as in the C++)
  8-D : the augmented form, with a, b, E2 = e^{2 psi}, eG = e^{G} as state variables. The field components are then
        the chain rule  -dH/dx = -(H_x + H_a a_x + H_b b_x + H_E2 E2_x + H_eG eG_x), with a_x = -2 beta a ea_x,
        b_x = 2 beta b eb_x, E2_x = 2 E2 psi_x, eG_x = eG G_x; the augmented states enter as TIGHT enclosures (their
        true range over the box), which is optimistic (flaw 1 in the 2026-10-21 note to the Bridge).
ratio = interval width / true linear range (sum_j |d f_i / d z_j| 2h, from the exact 4-D field).
Usage: field_aug.py x y px py [h] [8|9]   (9: Q also a state)"""
import sys, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe/tests")
import mn_codegen as CG
import mn_field_gate as Qg
mp.mp.dps = 40; mp.iv.dps = 40
x, y, PX, PY = CG.x, CG.y, CG.PX, CG.PY
vals = {CG.k: sp.Integer(39), CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: sp.Integer(267)}
z0 = [mp.mpf(v) for v in sys.argv[1:5]]; h = mp.mpf(sys.argv[5]) if len(sys.argv) > 5 else mp.mpf("1e-6")
Z = [x, y, PX, PY]

def ev_iv(e, env):
    if e.is_Symbol: return env[e]
    if e.is_Integer: return mp.iv.mpf(int(e))
    if e.is_Rational: return mp.iv.mpf(e.p) / e.q
    a = [ev_iv(q, env) for q in e.args]
    if e.is_Add:
        r = a[0]
        for q in a[1:]: r = r + q
        return r
    if e.is_Mul:
        r = a[0]
        for q in a[1:]: r = r * q
        return r
    if e.is_Pow:
        b_, n = a[0], e.args[1]
        if n.is_Integer: return b_ ** int(n) if int(n) >= 0 else 1 / b_ ** (-int(n))
        if n.is_Rational and n.q == 2: return mp.iv.sqrt(b_) ** n.p if n.p > 0 else 1 / mp.iv.sqrt(b_) ** (-n.p)
    if isinstance(e, sp.exp): return mp.iv.exp(a[0])
    raise ValueError(e)

def ev_cse(exprs, env):
    reps, red = sp.cse(exprs, symbols=sp.numbered_symbols("t"), optimizations="basic")
    env = dict(env)
    for s_, e in reps: env[s_] = ev_iv(e, env)
    return [ev_iv(e, env) for e in red]

# exact 4-D field (with parameters substituted) for values and true ranges
F4 = [sp.sympify(f).subs(vals) for f in CG.build()["field"]]
J = [[sp.lambdify(Z, sp.diff(f, v), "mpmath")(*z0) for v in Z] for f in F4]
lin = [sum(abs(J[i][j]) for j in range(4)) * 2 * h for i in range(4)]
box = {v: mp.iv.mpf([c - h, c + h]) for v, c in zip(Z, z0)}
w4 = ev_cse(F4, box)

# 8-D augmented form
a, b, E2, eG = sp.symbols("a b E2 eG")
k, al, beta, E, L = (vals[s] for s in (CG.k, CG.al, CG.beta, CG.E, CG.L))
R = sp.sqrt(x**2 + y**2 - 1); u = x*y/R; P = [sp.legendre(l, u) for l in range(4)]
ea = -1 + sum((x - y)*P[l]/R**(l + 1) for l in range(3))
eb = 1 + sum((-1)**(3 - l)*(x + y)*P[l]/R**(l + 1) for l in range(3))
psi = beta*P[2]/R**3
G = 3*beta**2*(P[3]**2 - P[2]**2)/R**6 + 2*beta*sum(((x - y) + (-1)**l*(x + y))*P[l]/R**(l + 1) - 2 for l in range(3)) + 8*beta
Qp, r = sp.div(sp.Poly(sp.expand((Qg.x**2 - 1)*(1 - Qg.y**2)*Qg.B**2 - 4*Qg.C**2), Qg.x, Qg.y, Qg.a, Qg.b),
               sp.Poly(Qg.A, Qg.x, Qg.y, Qg.a, Qg.b))
sub = {Qg.x: x, Qg.y: y, Qg.a: a, Qg.b: b}
A_, B_, C_, Q_ = Qg.A.subs(sub), Qg.B.subs(sub), Qg.C.subs(sub), Qp.as_expr().subs(sub)
w0 = 4*k*al/(1 - al**2); Lp = L + w0*E; rho2 = k**2*(x**2 - 1)*(1 - y**2)
QS = sp.Symbol("Qs"); NINE = len(sys.argv) > 6 and sys.argv[6] == "9"
Qfull = Q_
if NINE: Q_ = QS                                   # 9-D: Q itself is a state; its total x/y derivative is chained
V = (E2*A_*Lp**2 - 4*k*C_*E*Lp - k**2*E**2*Q_/E2)/(2*rho2*B_)
gxx = E2*(x**2 - 1)*(1 - al**2)**2/(k**2*B_*eG); gyy = E2*(1 - y**2)*(1 - al**2)**2/(k**2*B_*eG)
H = (gxx*PX**2 + gyy*PY**2)/2 + V
dz = {}
for v in (x, y):
    dz[v] = sp.diff(H, v) + sp.diff(H, a)*(-2*beta*a*sp.diff(ea, v)) + sp.diff(H, b)*(2*beta*b*sp.diff(eb, v)) \
            + sp.diff(H, E2)*(2*E2*sp.diff(psi, v)) + sp.diff(H, eG)*(eG*sp.diff(G, v))
    if NINE:
        dQ = sp.diff(Qfull, v) + sp.diff(Qfull, a)*(-2*beta*a*sp.diff(ea, v)) + sp.diff(Qfull, b)*(2*beta*b*sp.diff(eb, v))
        dz[v] = dz[v] + sp.diff(H, QS)*dQ
F8 = [sp.diff(H, PX), sp.diff(H, PY), -dz[x], -dz[y]]
pt = dict(zip(Z, z0))
def tight(e):
    v = sp.lambdify(Z, e, "mpmath")(*z0); g = [sp.lambdify(Z, sp.diff(e, q), "mpmath")(*z0) for q in Z]
    rr = sum(abs(gi) for gi in g) * h
    return mp.iv.mpf([v - rr, v + rr])
env8 = dict(box)
env8[a] = tight(-al*sp.exp(-2*beta*ea)); env8[b] = tight(al*sp.exp(2*beta*eb))
env8[E2] = tight(sp.exp(2*psi)); env8[eG] = tight(sp.exp(G))
if NINE: env8[QS] = tight(Qfull.subs({a: -al*sp.exp(-2*beta*ea), b: al*sp.exp(2*beta*eb)}))
w8 = ev_cse(F8, env8)
print("point", [mp.nstr(c, 10) for c in z0], " h", mp.nstr(h, 3))
for i, nm in enumerate(("xdot", "ydot", "pxdot", "pydot")):
    W4 = float(w4[i].b) - float(w4[i].a); W8 = float(w8[i].b) - float(w8[i].a)
    print("%-6s true range %.2e   4-D ratio %.2e   8-D ratio %.2e" % (nm, float(lin[i]), W4 / float(lin[i]), W8 / float(lin[i])))
