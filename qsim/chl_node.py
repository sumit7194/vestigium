"""
One quadrature node (t, q) of the CHL corner-function integral, entirely in mpmath.

  start series at x = pi   : block-triangular solve (chl_mp.solve_series_btf)
  smooth-end coefficients  : I(eps) = sum H_n eps^{n+1}/(n+1), even in eps, so
                             c2, c4, c6 integrands are 8 pi a(1-a) H1/2, H3/4, H5/6
  finite angles            : Taylor stepping (chl_taylor) from x = pi - eps0
Precision scales with mass, dps = 30 + 3M: the start series sheds ~2.7M digits
(measured singular spectrum ~ e^{-2 pi M}; 40 digits at M = 6 kept only ~20).
Only series coefficients of order <= N-4 are used: the top orders carry
truncation artifacts (measured: orders N-3, N-2 off by 1e-7 in the double solve).
"""
import time
import mpmath as mpm


def compute_node(t, q, xs, N=26, eps0="0.15", dps=None, taylor_N=30):
    import chl_mp as cm, chl_taylor as ct
    M = mpm.sqrt(mpm.mpf("0.25") + mpm.mpf(q)**2)
    dps = dps or int(30 + 3*float(M))
    mpm.mp.dps = dps
    a = mpm.mpc("0.5", -mpm.mpf(t))
    t0 = time.time()
    F, info = cm.solve_series_btf(a, M, N, dps=dps)
    t_series = time.time() - t0
    mpm.mp.dps = dps
    K = 8*mpm.pi*a*(1 - a)
    smooth = {f"c{2*j+2}": K*F["H"][2*j + 1]/(2*j + 2) for j in range(3)}
    use = N - 4
    e0 = mpm.mpf(eps0)
    Fu = {k: v[:use + 1] for k, v in F.items()}
    st = cm.evaluate_mp(Fu, e0)
    Y0 = {k: st[k] for k in ["H", "X1", "X2", "b", "c", "u"]}
    Y0["I"] = mpm.fsum(Fu["H"][n]*e0**(n + 1)/(n + 1) for n in range(use + 1))
    Zg = {k: st[k] for k in ["beta1", "beta2", "B1", "B2", "B12"]}
    t0 = time.time()
    xs_mp = [mpm.mpf(x) for x in xs]
    out, steps = ct.integrate(Y0, Zg, mpm.pi - e0, xs_mp, a, M, N=taylor_N,
                              B=ct.Backend("mp", dps=dps))
    t_taylor = time.time() - t0
    trG = {float(mpm.re(x)): K*out[x] for x in out}
    return dict(t=float(t), q=float(q), M=float(M), dps=dps,
                trG={x: [float(v.real), float(v.imag)] for x, v in trG.items()},
                smooth={k: [float(v.real), float(v.imag)] for k, v in smooth.items()},
                block_res=float(info["worst_block_residual"]),
                redundant_res=float(info["redundant_residual"]),
                steps=steps, t_series=t_series, t_taylor=t_taylor)
