"""DIAGNOSTIC ONLY: which CSE subexpressions of the generated MN field carry the interval over-widening.
Evaluates every CSE temp of mn_codegen.build()['field'] on a box of half-width h (mpmath interval arithmetic, in the
same CSE order the C++ uses) and compares its width with the linear true range sum_j |d temp/d z_j| 2h (mpmath, point
derivative by forward-mode on the same DAG). Reports temps whose ratio jumps relative to their inputs."""
import sys, mpmath as mp, sympy as sp
sys.path.insert(0, "/Users/sumit/Github/quantum/qsim/capd/horseshoe")
import mn_codegen as CG
mp.mp.dps = 40; mp.iv.dps = 40
X = CG.build(); field = X["field"]
reps, red = sp.cse(field, symbols=sp.numbered_symbols("t"), optimizations="basic")
z = [CG.x, CG.y, CG.PX, CG.PY]
pars = {CG.k: 39, CG.al: sp.Rational(-5, 8), CG.beta: sp.Rational(13394411, 1186380), CG.E: sp.Rational(19, 20), CG.L: 267}
pt = [float(a) for a in sys.argv[1:5]]; h = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-6
ivenv = {CG.k: mp.iv.mpf(39), CG.al: mp.iv.mpf(-5) / 8, CG.beta: mp.iv.mpf(13394411) / 1186380, CG.E: mp.iv.mpf(19) / 20, CG.L: mp.iv.mpf(267)}
for s, v in zip(z, pt): ivenv[s] = mp.iv.mpf([v - h, v + h])
penv = {s: mp.mpf(v) for s, v in zip(z, pt)}; penv.update({k_: mp.mpf(sp.Rational(v).p) / sp.Rational(v).q for k_, v in pars.items()})
dpenv = {s: [mp.mpf(1) if i == j else mp.mpf(0) for j in range(4)] for i, s in enumerate(z)}
for k_ in pars: dpenv[k_] = [mp.mpf(0)] * 4
def ev_iv(e, env):
    if e.is_Symbol: return env[e]
    if e.is_Integer: return mp.iv.mpf(int(e))
    if e.is_Rational: return mp.iv.mpf(e.p) / e.q
    a = [ev_iv(q, env) for q in e.args]
    if e.is_Add: r = a[0]; [r := r + q for q in a[1:]]; return r
    if e.is_Mul: r = a[0]; [r := r * q for q in a[1:]]; return r
    if e.is_Pow:
        b, n = a[0], e.args[1]
        if n.is_Integer: return b ** int(n) if int(n) >= 0 else 1 / b ** (-int(n))
        if n == sp.Rational(1, 2): return mp.iv.sqrt(b)
        if n.is_Rational and n.q == 2: return mp.iv.sqrt(b) ** n.p if n.p > 0 else 1 / mp.iv.sqrt(b) ** (-n.p)
    if isinstance(e, sp.exp): return mp.iv.exp(a[0])
    raise ValueError(e)
def ev_pt(e, env, denv):            # value and gradient (forward mode)
    if e.is_Symbol: return env[e], denv[e]
    if e.is_Number: return mp.mpf(e.p) / e.q if e.is_Rational else mp.mpf(e), [mp.mpf(0)] * 4
    a = [ev_pt(q, env, denv) for q in e.args]
    if e.is_Add: return sum(v for v, _ in a), [sum(g[i] for _, g in a) for i in range(4)]
    if e.is_Mul:
        v, g = a[0]
        for v2, g2 in a[1:]: g = [g[i] * v2 + v * g2[i] for i in range(4)]; v = v * v2
        return v, g
    if e.is_Pow:
        (b, gb), n = a[0], e.args[1]; nn = mp.mpf(n.p) / n.q
        return b ** nn, [nn * b ** (nn - 1) * gi for gi in gb]
    if isinstance(e, sp.exp): v, g = a[0]; ev_ = mp.exp(v); return ev_, [ev_ * gi for gi in g]
    raise ValueError(e)
rows = []
for s_, e in reps:
    iv_ = ev_iv(e, ivenv); ivenv[s_] = iv_
    v, g = ev_pt(e, penv, dpenv); penv[s_] = v; dpenv[s_] = g
    lin = float(sum(abs(gi) for gi in g) * 2 * h); wid = float(iv_.b) - float(iv_.a)
    rows.append((str(s_), float(wid), float(lin), float(wid / lin) if lin > 0 else float("nan"), e, float(v)))
for i, e in enumerate(red):
    iv_ = ev_iv(e, ivenv); v, g = ev_pt(e, penv, dpenv); lin = sum(abs(gi) for gi in g) * 2 * h
    print("out[%d] value %.4e width %.3e lin %.3e ratio %.2e" % (i, float(v), float(iv_.b) - float(iv_.a), float(lin), (float(iv_.b) - float(iv_.a)) / float(lin)))
# ratio jumps: a temp whose ratio exceeds 3x the max ratio of the temps it uses
idx = {r[0]: r for r in rows}
print("--- temps whose over-widening ratio jumps >= 3x over their inputs (top 25 by jump)")
jumps = []
for name, wid, lin, rat, e, v in rows:
    ins = [idx[str(q)][3] for q in e.free_symbols if str(q) in idx]
    base = max([r for r in ins if r == r] + [1.0])
    if rat == rat and rat / base >= 3: jumps.append((rat / base, name, rat, v, e))
for j, name, rat, v, e in sorted(jumps, key=lambda q: -q[0])[:25]:
    print("%-6s jump %.1e ratio %.1e value %.3e  :: %s" % (name, j, rat, v, str(e)[:150]))
