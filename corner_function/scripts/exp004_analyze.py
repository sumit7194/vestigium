"""Analyse an EXP-004 result file: compare with published values, extract kappa from the sharp-angle end,
estimate the mass-tail truncation from the node data. Usage: exp004_analyze.py result.json"""
import sys, json, glob, math, numpy as np
res = json.load(open(sys.argv[1])); mode = res["mode"]; deg = np.array(res["deg"]); s = np.array(res["s"]); th = np.radians(deg)
# published references (real scalar / Dirac), see report EXP-001/EXP-004
REF = {
 "renyi2": {"label":"real scalar Renyi-2 [HHCWM16 Tab.1 alpha=2, complex/2; lattice in ()]", 26.565:(0.0881/2,0.087/2), 45:(0.0453/2,0.0450/2), 63.435:(0.0267/2,0.0268/2), 90:(0.0130/2,0.0130/2), 116.565:(0.00572/2,0.00572/2), 135:(0.00273/2,0.00272/2), 153.435:(0.000923/2,0.000923/2),
            "sigma": 1/(48*math.pi**2), "sigmap": (5+math.pi**2)/(960*math.pi**4), "kappa": None},
 "ee":     {"label":"real scalar EE [HHCWM16 Tab.1 alpha=1 ansatz/2 (lattice/2); CHL09 exact at 90,135]", 26.565:(0.156/2,0.154/2), 45:(0.0810/2,0.0809/2), 63.435:(0.0482/2,0.0483/2), 90:(0.02366/2,0.0236/2), 116.565:(0.0105/2,0.0105/2), 135:(0.005040/2,0.00507/2), 153.435:(0.00171/2,0.00170/2),
            "sigma": 1/256, "sigmap": (20+3*math.pi**2)/(18432*math.pi**2), "kappa": 0.0397},
 "dirac":  {"label":"Dirac EE [HHCWM16 Tab.2 alpha=1 ansatz (lattice); CHL09 exact at 90,135]", 26.565:(0.146,0.147), 45:(0.0776,0.0777), 63.435:(0.0468,0.0466), 90:(0.02329,0.02329), 116.565:(0.01043,0.0106), 135:(0.005022,0.0049), 153.435:(0.001703,0.002),
            "sigma": 1/128, "sigmap": (16+3*math.pi**2)/(9216*math.pi**2), "kappa": 0.0722},
}[mode]
print(f"mode={mode}  nodes={res['nodes']} failures={res['failures']}  p_max={res['p_max']} nt={res['nt']} t_max={res['t_max']}")
print(f"sigma  from H1: {res['sigma_from_H1']:.10e}   exact {REF['sigma']:.10e}   ratio {res['sigma_from_H1']/REF['sigma']:.8f}")
print(f"sigma' from H3: {res['sigmap_from_H3']:.10e}   exact {REF['sigmap']:.10e}   ratio {res['sigmap_from_H3']/REF['sigmap']:.8f}")
print(f"\n{'deg':>8} {'s(theta)':>14} {'ref ansatz':>12} {'ratio':>8} {'ref lattice':>12} {'ratio':>8}   a/C_T (C_T real scalar 3/32pi^2, Dirac 3/16pi^2)")
CT = 3/(16*math.pi**2) if mode=="dirac" else 3/(32*math.pi**2)
for d, v in zip(deg, s):
    r = REF.get(float(d)) or REF.get(int(d)) if float(d).is_integer() else REF.get(float(d))
    line = f"{d:8.3f} {v:14.8e}"
    if r: line += f" {r[0]:12.6e} {v/r[0]:8.4f} {r[1]:12.6e} {v/r[1]:8.4f}"
    else: line += " "*44
    line += f"   {v/CT:10.6f}"
    print(line)
# smooth-limit check: s(170), s(160) vs sigma eps^2 + sigma' eps^4 (+ sigma'' eps^6 from Helmes where available)
for d in (170.0, 160.0):
    i = list(deg).index(d); eps = math.pi - th[i]
    print(f"smooth check {d}: s = {s[i]:.8e}  sigma eps^2 + sigma' eps^4 = {REF['sigma']*eps**2 + REF['sigmap']*eps**4:.8e}  ratio {s[i]/(REF['sigma']*eps**2 + REF['sigmap']*eps**4):.6f}")
# kappa from the sharp end: fit s(theta) = kappa/theta + c0 + c1 theta + c2 theta^2 on the 4-6 smallest angles
sel = deg <= 30.1
A = np.vstack([1/th[sel], np.ones(sel.sum()), th[sel], th[sel]**2]).T
coef, *_ = np.linalg.lstsq(A, s[sel], rcond=None)
A3 = np.vstack([1/th[sel], np.ones(sel.sum()), th[sel]]).T; coef3, *_ = np.linalg.lstsq(A3, s[sel], rcond=None)
print(f"\nkappa from fit (angles <= 30 deg): 4-param {coef[0]:.6f}, 3-param {coef3[0]:.6f}" + (f"   published {REF['kappa']}" if REF['kappa'] else "") + f"   -> kappa/C_T = {coef[0]/CT:.4f}")
# node-level tail diagnostics
nodes = [json.load(open(f)) for f in glob.glob(sys.argv[1].rsplit('/',1)[0] + f"/exp004_nodes/{mode}_*.json")]
nodes = [n for n in nodes if n.get('ok')]
if nodes:
    ts = sorted(set(round(n['t'],8) for n in nodes))
    print(f"\n{len(nodes)} ok nodes; t values: {len(ts)}; per-node seconds: max {max(n['secs'] for n in nodes):.0f}, total {sum(n['secs'] for n in nodes)/3600:.2f} core-h")
    # mass decay at the largest masses for t = smallest t: ratio F(M_k)/F(M_{k-1}) at 5 and 26.6 deg
    t0 = ts[0]; sub = sorted([n for n in nodes if round(n['t'],8)==t0], key=lambda n: n['M'])
    print("largest-mass nodes (t=%.3f): M, F(5), F(26.6), F(90), branch, flips, secs" % t0)
    for n in sub[-4:]: print(f"   {n['M']:7.3f} {n['F_re'][0]:.3e} {n['F_re'][4]:.3e} {n['F_re'][13]:.3e}  br={n.get('branch')} fl={n.get('flips')} {n['secs']:.0f}s")
    if len(sub) >= 3:
        for i, dname in [(0,'5deg'),(4,'26.6deg')]:
            f1, f2 = sub[-2]['F_re'][i], sub[-1]['F_re'][i]; dM = sub[-1]['M'] - sub[-2]['M']
            lam = -math.log(f2/f1)/dM if f1>0 and f2>0 else float('nan')
            Mmax = sub[-1]['M']; p = math.sqrt(Mmax**2-0.25)
            tail = p*p*f2/lam if lam>0 else float('nan')   # crude: Int_{Mmax}^inf p^2 F ~ p^2 F(Mmax)/lam
            print(f"   tail estimate at {dname}: decay rate {lam:.2f}/unit M, tail beyond M_max ~ {tail:.2e} (x prefactor), i.e. ~{(2 if mode=='renyi2' else 1)*tail/ s[i]:.1e} of s")
