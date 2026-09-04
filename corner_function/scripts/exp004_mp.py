"""
EXP-004 (mp): arbitrary-precision version of the Casini-Huerta-Leitao corner-function solver.
Same equations as exp004_ch_solver.py (CHL09 App. B eqs 72-89). Needed because the physical
solution near x=pi is ~e^{-2 pi M} times the O(1) variables and then grows like e^{2M(pi-x)}, so
double precision cannot represent it for M >~ 4, while sharp angles need M up to ~15.
Precision: dps = 25 + 3 M digits keeps the round-off seed e^{2 pi M} 10^{-dps} below 1e-16.
Series start: Gauss-Newton in mp on the parity-reduced coefficient system (H,u,beta odd in
delta=pi-x; X,b,c,B even), warm-started from the double-precision solution.
ODE: Gragg-Bulirsch-Stoer (modified midpoint + polynomial extrapolation), adaptive macro-step.
"""
import sys, math, numpy as np
import mpmath as mp
from mpmath import mpf, mpc
sys.path.insert(0, __file__.rsplit('/',1)[0])
import exp004_ch_solver as cs

def set_prec(M): mp.mp.dps = int(25 + 3*abs(M))

def bc_values_mp(M, a):
    M = mpf(M); a = mpc(a) if isinstance(a, complex) else mpf(a)
    mu = mp.sqrt(4*M*M - 1)
    def Xpi(a):
        Impsi = (mp.digamma(mpf(1)/2 + a + 1j*mu/2) - mp.digamma(mpf(1)/2 + a - 1j*mu/2))/(2j)
        absG2 = mp.gamma(mpf(1)/2 - a + 1j*mu/2)*mp.gamma(mpf(1)/2 - a - 1j*mu/2)
        num = mp.gamma(-a)*(mp.cosh(mp.pi*mu/2)*Impsi - (mp.pi/2)*mp.sinh(mp.pi*mu/2))
        den = mpf(2)**(2*a)*mu*(mp.cos(2*a*mp.pi) + mp.cosh(mp.pi*mu))*mp.gamma(1+a)*absG2
        return num/den
    def bpi(a):
        absG2 = mp.gamma(mpf(1)/2 + a + 1j*mu/2)*mp.gamma(mpf(1)/2 + a - 1j*mu/2)
        return mpf(2)**(1-2*a)*a*(1-a)*absG2/(M*mp.gamma(1+a)**2)
    return Xpi(a), Xpi(1-a), bpi(a), bpi(1-a)

# ---- mp truncated series (lists of mpc, length K) ----
def smul(p, q, K):
    r = [mpc(0)]*K
    for i, pi_ in enumerate(p):
        if pi_ == 0: continue
        for j in range(K - i):
            r[i+j] += pi_*q[j]
    return r
def sadd(p, q): return [x+y for x,y in zip(p,q)]
def ssub(p, q): return [x-y for x,y in zip(p,q)]
def sscale(p, s): return [x*s for x in p]
def sDx(p, K): return [-(k+1)*p[k+1] for k in range(K-1)] + [mpc(0)]     # d/dx = -d/ddelta
def trig_mp(K):
    f = [mp.factorial(i) for i in range(K)]
    sin_d = [mpc(0) if i%2==0 else mpc((-1)**((i-1)//2))/f[i] for i in range(K)]
    cos_d = [mpc((-1)**(i//2))/f[i] if i%2==0 else mpc(0) for i in range(K)]
    sin_h = [mpc(0) if i%2==0 else mpc((-1)**((i-1)//2))/(f[i]*mpf(2)**i) for i in range(K)]
    cos_h = [mpc((-1)**(i//2))/(f[i]*mpf(2)**i) if i%2==0 else mpc(0) for i in range(K)]
    cos_2d= [mpc((-1)**(i//2))*mpf(2)**i/f[i] if i%2==0 else mpc(0) for i in range(K)]
    return sin_d, cos_d, sin_h, cos_h, cos_2d

def series_start_mp(M, a, N, guess_double, iters=4, verbose=False, branch=-1):
    """Refine the double-precision series coefficients in mp. guess_double: tuple of S objects from cs.series_start."""
    K = N+1
    Ma = mpf(M); aa = mpc(a) if isinstance(a, complex) else mpf(a)
    X10, X20, b0, c0 = bc_values_mp(M, a)
    sin_d, cos_d, sin_h, cos_h, cos_2d = trig_mp(K)
    one_m_cos = ssub([mpc(1)]+[mpc(0)]*(K-1), cos_d); sin_h2 = smul(sin_h, sin_h, K)
    pref = 1/(8*mp.pi*aa*(1-aa))
    # parity-reduced unknown layout: H odd (k=1,3,..), X1,X2 even (k=2,4,..), b,c even, u odd, be1,be2 odd, B1,B2 even (k=0,2,..), B12 odd
    odd = [k for k in range(1,K) if k%2==1]; even_pos = [k for k in range(2,K) if k%2==0]; even0 = [k for k in range(0,K-2) if k%2==0]   # top-order B's are undetermined by the truncated system: drop them
    layout = [('H',odd),('X1',even_pos),('X2',even_pos),('b',even_pos),('c',even_pos),('u',odd),('be1',odd),('be2',odd),('B1',even0),('B2',even0),('B12',odd)]   # B12 is ODD in delta (checked numerically on the double solution)
    lead = {'H':mpc(0),'X1':X10,'X2':X20,'b':b0,'c':c0,'u':mpc(0),'be1':mpc(0),'be2':mpc(0),'B1':None,'B2':None,'B12':None}
    nun = sum(len(ks) for _,ks in layout)
    def unpack(v):
        d = {}; i = 0
        for name, ks in layout:
            s = [mpc(0)]*K
            if lead[name] is not None: s[0] = lead[name]
            for k in ks: s[k] = v[i]; i += 1
            d[name] = s
        return d
    def resid(v):
        d = unpack(v); H,X1,X2,b,c,u,be1,be2,B1,B2,B12 = (d[n] for n,_ in layout)
        m = lambda p,q: smul(p,q,K)
        E73 = sadd(sDx(H,K), sscale(sadd(sadd(m(b,B2), m(c,B1)), sscale(m(u,B12),2)), Ma/2))
        E74 = sadd(sDx(X1,K), sscale(sadd(m(b,B12), m(u,B1)), Ma))
        E75 = sadd(sDx(X2,K), sscale(sadd(m(c,B12), m(u,B2)), Ma))
        E76 = sadd(sadd(m(sin_d, sDx(c,K)), sscale(m(m(be2,u),cos_h), 2*Ma)), sscale(m(c,one_m_cos), 1-aa))
        E77 = sadd(sadd(m(sin_d, sDx(b,K)), sscale(m(m(be1,u),cos_h), 2*Ma)), sscale(m(b,one_m_cos), aa))
        E78 = ssub(sadd(m(sin_h, sDx(u,K)), sscale(sadd(m(b,be2), m(c,be1)), Ma/2)), sscale(m(u,cos_h), mpf(1)/2))
        bX = sadd(m(be1,X2), m(be2,X1))
        E79 = ssub(sadd(ssub(sscale(sin_h,pref), m(cos_h,H)), sscale(bX, Ma)), sscale(m(m(sin_h,u),B12), 2*Ma))
        E80 = ssub(sadd(sadd(sscale(m(cos_h,sin_h),pref), m(sin_h2,H)), sscale(m(cos_h,bX), Ma)), sscale(m(m(cos_h,sin_h), sadd(m(b,B2),m(c,B1))), Ma))
        E81 = sadd(sadd(sscale(m(m(cos_h,sin_h), ssub(m(c,X1),m(b,X2))), -Ma), sscale(m(cos_h, ssub(m(be2,B1),m(be1,B2))), Ma)), sscale(m(sin_h2,B12), 1-2*aa))
        t1 = [mpc(-4*aa*(aa-1))]+[mpc(0)]*(K-1)
        t2 = sscale(sadd(sadd([mpc(4)]+[mpc(0)]*(K-1), sscale(m(be1,be2),-8)), sadd(m(b,c), sscale(m(u,u),3))), -Ma*Ma)
        t3 = sscale(m(cos_d, sadd([mpc(aa*(aa-1))]+[mpc(0)]*(K-1), sscale(sadd(m(u,u),[mpc(1)]+[mpc(0)]*(K-1)), Ma*Ma))), 4)
        t4 = sscale(m(cos_2d, ssub(m(b,c), m(u,u))), Ma*Ma)
        E82 = sadd(sadd(t1,t2), sadd(t3,t4))
        E83 = sadd(sscale(m(u,sin_h2), 2*aa-1), sscale(m(cos_h, ssub(m(be1,c), m(b,be2))), Ma))
        r = E73[:N]+E74[:N]+E75[:N]+E76+E77+E78+E79+E80+E81+E82+E83
        return r
    if guess_double is None:
        # hand-derived leading order, evaluated in mp (exact cancellations that are catastrophic in double):
        # beta1^1 beta2^1 = P, beta1^1 c0 = b0 beta2^1, u^1 = M c0 beta1^1, H^1 = pref/2 + M(beta1^1 X2^0 + beta2^1 X1^0),
        # b0 B2^0 + c0 B1^0 = 2 H^1/M,  beta2^1 B1^0 - beta1^1 B2^0 = (c0 X1^0 - b0 X2^0)/2
        P = (aa*(aa-1) + Ma*Ma*(1 + b0*c0))/(4*Ma*Ma)
        be1_1 = branch*mp.sqrt(P*b0/c0); be2_1 = P/be1_1; u1 = Ma*c0*be1_1
        H1 = pref/2 + Ma*(be1_1*X20 + be2_1*X10)
        det = -c0*be1_1 - b0*be2_1; r80 = 2*H1/Ma; r81 = (c0*X10 - b0*X20)/2
        B10 = (-be1_1*r80 - b0*r81)/det; B20 = (c0*r81 - be2_1*r80)/det
        lead_coef = {'H':{1:H1}, 'u':{1:u1}, 'be1':{1:be1_1}, 'be2':{1:be2_1}, 'B1':{0:B10}, 'B2':{0:B20}}
        v = []
        for name, ks in layout:
            for k in ks: v.append(lead_coef.get(name, {}).get(k, mpc(0)))
        v = np.array(v, dtype=object)
    else:
        dd = dict(zip([n for n,_ in layout], guess_double))
        v = []
        for name, ks in layout:
            cc = dd[name] if isinstance(dd[name], (list, tuple)) else dd[name].c
            for k in ks: v.append(mpc(complex(cc[k])) if k < len(cc) else mpc(0))
        v = np.array(v, dtype=object)
    r0 = resid(v); nr = float(mp.sqrt(sum(abs(x)**2 for x in r0)))
    if verbose:
        names = ['E73','E74','E75','E76','E77','E78','E79','E80','E81','E82','E83']; lens = [N,N,N,K,K,K,K,K,K,K,K]; i0 = 0
        for nm, L in zip(names, lens):
            blk = r0[i0:i0+L]; i0 += L
            print(f"     warm-start block {nm}: max|r| = {float(max(abs(x) for x in blk)):.2e}", file=sys.stderr)
    for it in range(iters):
        r0 = resid(v); r0v = np.array(r0, dtype=object)
        nr = float(mp.sqrt(sum(abs(x)**2 for x in r0)))
        if verbose: print(f"     GN iter {it}: |r| = {nr:.2e}", file=sys.stderr)
        if nr < mpf(10)**(-mp.mp.dps+6): break
        # finite-difference Jacobian (complex step in each unknown; residual is holomorphic in the unknowns)
        h = mpf(10)**(-(mp.mp.dps//2))
        J = np.empty((len(r0), len(v)), dtype=object)
        for j in range(len(v)):
            vv = v.copy(); vv[j] = vv[j] + h
            rj = resid(vv)
            for i in range(len(r0)): J[i,j] = (rj[i]-r0[i])/h
        # least squares via normal equations in mp
        Jm = mp.matrix(J.tolist()); rm = mp.matrix([[x] for x in r0])
        JH = Jm.H; A = JH*Jm
        lam = mpf(10)**(-mp.mp.dps+8)*max(abs(A[i,i]) for i in range(A.rows))
        for i in range(A.rows): A[i,i] += lam
        dv = mp.lu_solve(A, JH*rm)
        lam_ls = mpf(1)
        for _ls in range(8):
            vt = np.array([v[j] - lam_ls*dv[j] for j in range(len(v))], dtype=object)
            rt = resid(vt); nrt = float(mp.sqrt(sum(abs(x)**2 for x in rt)))
            if nrt < nr: break
            lam_ls = lam_ls/2
        v = vt; nr = nrt
    d = unpack(v)
    return d, nr

DIAG_MP = {'ambiguous':0, 'far_jump':0}
def algebraic_mp(x, M, a, H, X1, X2, b, c, u, be1_prev):
    sh, ch, th = mp.sin(x/2), mp.cos(x/2), mp.tan(x/2)
    D = -(2*a-1)*u*ch/(M*th)
    cx, c2x = mp.cos(x), mp.cos(2*x)
    P = (4*a*(a-1) + M*M*(4 + b*c + 3*u*u) + 4*cx*(a*(a-1) + M*M*(u*u+1)) - M*M*c2x*(b*c - u*u))/(8*M*M)
    disc = mp.sqrt(D*D + 4*c*P*b)
    r1, r2 = (D + disc)/(2*c), (D - disc)/(2*c)
    be1 = r1 if abs(r1 - be1_prev) < abs(r2 - be1_prev) else r2
    if abs(r1 - r2) < mpf('1e-3')*(abs(r1)+abs(r2)): DIAG_MP['ambiguous'] += 1
    if min(abs(r1-be1_prev), abs(r2-be1_prev)) > mpf('0.3')*abs(r1-r2): DIAG_MP['far_jump'] += 1
    be2 = (be1*c - D)/b
    B12 = (ch/(8*mp.pi*a*(1-a)) - sh*H + M*(be1*X2 + be2*X1))/(2*M*ch*u)
    R80 = 1/(8*mp.pi*a*(1-a)*M) + ch*H/(M*sh) + (be1*X2 + be2*X1)/ch
    R81 = ch*(c*X1 - b*X2) - (1-2*a)*ch*ch*B12/(M*sh)
    det = -c*be1 - b*be2
    B1 = (-be1*R80 - b*R81)/det; B2 = (c*R81 - be2*R80)/det
    return B1, B2, B12, be1, be2

def rhs_mp(x, y, M, a, state):
    H,X1,X2,b,c,u,F = y
    B1,B2,B12,be1,be2 = algebraic_mp(x, M, a, H, X1, X2, b, c, u, state['be1']); state['be1'] = be1
    sx, sh, ch, th, cx = mp.sin(x), mp.sin(x/2), mp.cos(x/2), mp.tan(x/2), mp.cos(x)
    return [-(M/2)*(b*B2 + c*B1 + 2*u*B12), -M*(b*B12 + u*B1), -M*(c*B12 + u*B2),
            -2*M*be1*u*sh/sx - b*a*(1+cx)/sx, -2*M*be2*u*sh/sx - c*(1-a)*(1+cx)/sx,
            -(M/2)*(b*be2 + c*be1)/ch + u*th/2, -H]

def bs_step(f, x, y, Hs, args, state, tol, seq=(2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32)):
    # tol: list of per-component tolerances (relative-to-(|y|+1) for the O(1) variables, relative for H and F)
    """One Gragg-Bulirsch-Stoer macro step of size Hs (negative: integrating towards smaller x). Returns (y_new, err_est, ok)."""
    T = []
    for n in seq:
        h = Hs/n
        st = dict(state)
        z0 = list(y); z1 = [z0[i] + h*fi for i, fi in enumerate(f(x, z0, *args, st))]
        for m in range(1, n):
            fz = f(x + m*h, z1, *args, st)
            z2 = [z0[i] + 2*h*fz[i] for i in range(len(y))]
            z0, z1 = z1, z2
        fz = f(x + Hs, z1, *args, st)
        yn = [(z0[i] + z1[i] + h*fz[i])/2 for i in range(len(y))]
        T.append(yn)
        # polynomial (Neville) extrapolation in h^2 -> 0 across the sequence so far
        k = len(T)-1
        row = [yn]
        for j in range(1, k+1):
            fac = (mpf(seq[k])/mpf(seq[k-j]))**2 - 1
            prev = row[-1]
            row.append([prev[i] + (prev[i] - Ttab[k-1][j-1][i])/fac for i in range(len(y))])
        if k == 0: Ttab = [row]
        else: Ttab.append(row)
        if k >= 1:
            best, prevbest = Ttab[k][k], Ttab[k][k-1]
            err = max(abs(best[i]-prevbest[i])/((abs(best[i])+abs(y[i])+mpf(10)**-300)*tol[i]) for i in range(len(y)))
            if err < 1: return best, err, True, st
    return Ttab[-1][-1], err, False, st

def integrate_mp(M, a, x_min, x_grid, N=None, delta0=None, tol=None, verbose=False, branch=-1, guess=None):
    set_prec(M)
    # absolute start accuracy must be ~ e^{-2 pi M} 1e-10 in ALL variables (any O(1) error seeds the physical growing mode):
    # truncation ~ (2 M delta0)^(N+1) with delta0 = 0.01/M  =>  N ~ 1.6 M + 8
    if N is None: N = int(2*round((1.6*abs(M) + 8)/2))
    if delta0 is None: delta0 = min(0.05, 0.01/max(abs(M), 0.2))
    if tol is None:
        tolA = mpf(10)**(-(12 + 2.8*abs(M)))          # O(1) variables: any error seeds the growing mode ~ e^{2 pi M}
        tol = [mpf('1e-14'), tolA, tolA, tolA, tolA, tolA, mpf('1e-14')]   # [H, X1, X2, b, c, u, F]
    # double-precision warm start only at a small order (the coefficients span ~(2M)^N, beyond double range for large M),
    # then continuation in N inside mp: each stage warm-starts from the previous stage's coefficients (higher orders = 0)
    g = None; Ncur = 4
    while True:
        d, nr = series_start_mp(M, a, Ncur, g, iters=8, verbose=False, branch=branch)
        if verbose: print(f"     N-continuation stage N={Ncur}: |r|={float(nr):.1e}", file=sys.stderr)
        if Ncur >= N: break
        Ncur = min(N, Ncur + 4)
        g = tuple(d[k] for k in ['H','X1','X2','b','c','u','be1','be2','B1','B2','B12'])
    Ma = mpf(M); aa = mpc(a) if isinstance(a, complex) else mpf(a)
    d0 = mpf(delta0)
    ev = lambda s: sum(s[k]*d0**k for k in range(len(s)))
    y = [ev(d['H']), ev(d['X1']), ev(d['X2']), ev(d['b']), ev(d['c']), ev(d['u']), sum(d['H'][k]*d0**(k+1)/(k+1) for k in range(1, N+1))]
    state = {'be1': ev(d['be1'])}
    x = mp.pi - d0; Hs = -mpf(delta0)
    targets = sorted([mpf(t) for t in x_grid], reverse=True); out = {}; outq = {}
    nsteps = 0
    while x > x_min + mpf(10)**-20 and targets:
        # do not step past the next target
        Hs_eff = Hs
        if x + Hs_eff < targets[0]: Hs_eff = targets[0] - x
        ynew, err, ok, st = bs_step(rhs_mp, x, y, Hs_eff, (Ma, aa), state, tol)
        if not ok:
            Hs = Hs/2; continue
        x = x + Hs_eff; y = ynew; state = st; nsteps += 1
        if err < mpf('0.01'): Hs = Hs*mpf('1.5')
        if abs(Hs) > mpf('0.15'): Hs = -mpf('0.15')
        while targets and x <= targets[0] + mpf(10)**-25:
            out[float(targets[0])] = y[6]
            B1_,B2_,B12_,be1_,be2_ = algebraic_mp(x, Ma, aa, y[0], y[1], y[2], y[3], y[4], y[5], state['be1'])
            outq[float(targets[0])] = (y[3], y[1], be1_, B1_)      # (b, X1, beta1, B1) at this angle, for CHL09 eq (59)
            targets.pop(0)
    if verbose: print(f"   M={M} a={a}: dps={mp.mp.dps} N={N} delta0={delta0:.4f} series |r|={float(nr):.1e} steps={nsteps} diag={dict(DIAG_MP)}", file=sys.stderr)
    integrate_mp.last_outq = outq
    return out, d

if __name__ == "__main__":
    import time
    degs = [5,15,26.565,45,90,135]; xg = [math.radians(v) for v in degs]
    Ms = [float(v) for v in sys.argv[1:]] or [1.0, 3.0]
    for M in Ms:
        t0 = time.time(); out, d = integrate_mp(M, 0.5, math.radians(4), xg, verbose=True)
        print(f"M={M}: " + " ".join(f"F({dg})={mp.nstr(out[x].real, 10)}" for dg,x in zip(degs,xg)) + f"  H1={mp.nstr(d['H'][1],8)}  [{time.time()-t0:.0f}s]", flush=True)
