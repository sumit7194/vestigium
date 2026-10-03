"""Development self-test of the native core on equations with EXACTLY known monodromy (non-reduced, p != 0).
Becomes part of the registered V-G0 rung. Expected values are computed in Arb from closed forms."""
import cmath, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
import ia_native as IN, ia_hub as IA
from flint import acb, arb, ctx
ctx.prec = 192
z = sp.Symbol("z")
R = sp.Rational
a_, b_, c_ = R(1, 5), R(1, 7), R(1, 3)

def e2pi(q):   # exact exp(2 pi i q) as an Arb ball
    return (acb(0, 1)*2*arb.pi()*arb(int(q.p))/int(q.q)).exp()

def hyp_entries(b, p_expr, q_expr):
    """M = [[0,1],[-q,-p]] with p, q given as SymPy rational expressions in z."""
    pn, pd = sp.fraction(sp.together(-p_expr))
    qn, qd = sp.fraction(sp.together(-q_expr))
    zero, one = b.const(0), b.const(1)
    return [[(zero, one), (one, one)], [(b.expr(qn, z), b.expr(qd, z)), (b.expr(pn, z), b.expr(pd, z))]]

results = {}
# (a) Gauss hypergeometric, non-reduced: z(1-z)y'' + [c-(a+b+1)z]y' - ab y = 0
p = (c_ - (a_ + b_ + 1)*z)/(z*(1 - z))
q = -a_*b_/(z*(1 - z))
b = IN.SLPBuilder()
ent = hyp_entries(b, p, q)
loops = [("around0", IA.loop_points(0.5 + 0.5j, 0, 0.25)), ("around1", IA.loop_points(0.5 + 0.5j, 1, 0.25))]
job = IN.write_job(b, ent, loops, obst=[0, 1], threads=2)
res = IN.run_job(job)
exp_tr = {"around0": 1 + e2pi(1 - c_), "around1": 1 + e2pi(c_ - a_ - b_)}
exp_det = {"around0": e2pi(1 - c_), "around1": e2pi(c_ - a_ - b_)}
for nm in ("around0", "around1"):
    M = res[nm]["M"]
    t, d = IN.tr(M), IN.det(M)
    ok = t.contains(exp_tr[nm]) and d.contains(exp_det[nm])
    results[f"(a) hypergeometric {nm}"] = dict(status=res[nm]["status"], steps=res[nm]["steps"], trace=str(t),
                                               expected=str(exp_tr[nm]), det=str(d), contains=bool(ok),
                                               digits=IA.radius_digits(t))
# (b) exp pullback w = exp(2/x^3) of the same equation (coefficients in Q(x, E), essential point x = 0):
#     y'' + P y' + Q y = 0,  P = w'' / ... : P = -(w''/w') + w' p(w),  Q = w'^2 q(w)
x = z
w = sp.exp(2/x**3)
wp = sp.diff(w, x)
lp = sp.simplify(sp.diff(wp, x)/wp)                    # rational: -4/x - 6/x^4
P = -lp + wp*p.subs(z, w)
Q = wp**2*q.subs(z, w)
b2 = IN.SLPBuilder()
ent2 = hyp_entries(b2, P, Q)
x1 = complex(sp.N((-sp.I/sp.pi)**R(1, 3), 30))
job2 = IN.write_job(b2, ent2, [("aroundE1", IA.loop_points(x1 + 0.01, x1, 0.01, ngon=32))], bad=[0], obst=[x1],
                    hmax=0.004, threads=1)
res2 = IN.run_job(job2)
M = res2["aroundE1"]["M"]
t = IN.tr(M)
results["(b) exp pullback around E=1 root"] = dict(status=res2["aroundE1"]["status"], steps=res2["aroundE1"]["steps"],
                                                  trace=str(t), expected=str(exp_tr["around1"]),
                                                  contains=bool(t.contains(exp_tr["around1"])),
                                                  digits=IA.radius_digits(t))
for k, v in results.items():
    print(k, v, flush=True)
print("SELFTEST_PASS", all(v["contains"] and v["digits"] >= 10 for v in results.values()))
