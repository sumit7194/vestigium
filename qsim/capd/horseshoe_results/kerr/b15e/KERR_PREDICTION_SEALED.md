# SEALED blind prediction of the Kerr negative control (B15e)

- **[model: Fable 5.2]. UNVERIFIED.** Written 2026-11-26 for `BRIEF_FABLE_KERR_PREDICT.md` (commit 74b5f2e).
- **Blindness.** I read only the brief's allowed inputs, by exact path: PREREG lines 1 to 1973 (by `head`/`sed` ranges), `b15c/ARM.json`, `b15d/kerr/build.json`, `kerr_e/N1N2.spec`, `kerr_e/N0N0.out`, `kerr_e/N0N1.out`, the COVER lines of `twin_e/` and `recipe/`, and `hs_cover.cpp`. I did not open, list or stat any other `kerr_e/` or `kerr_a/` output, the void directories, `run.log`, guard outputs, `ckpt/kerr/`, the a4 logs, or PREREG from line 1974; no `ps`; no git log past 74b5f2e.
- **Disclosure (things I knew before the brief, from this session's memory index and the commit subjects in its header).**
  - The kerr_e chunks N1N2 and N2N3 hit the 48 h watchdog and were to be rerun with a longer one.
  - A KERR-EARLY step was passed in the queue; I do not know what it said.
  - I know no COVER line, no FAILPIECE line and no class of any covering except the two the brief gives.
- **Compute.** About 20 s of float Python: a model of the Kerr section map on the registered sets (appendix). It reads `build.json` only. Nothing launched. Main not edited.

## 1. Per-covering prediction

| Covering | (i) Edge chunk | (ii) Final class: P(CERTIFIED) / P(CERTIFIED-FAIL) / P(UNDECIDED) | (iii) Where the failure appears, and why |
|---|---|---|---|
| N0N0 (required) | known: b = 1, no certified failure | **CERTIFIED** 0.87 / 0.00 / 0.13 | No failure. N0 uses the saddle's own eigen-frame; the image is a strip 1/62.6 thin along W^u. An UNDECIDED could only come from interior pieces at the depth cap. |
| N0N1 (required) | known: b = 1, no certified failure | **CERTIFIED** 0.85 / 0.00 / 0.15 | No failure, same reason. The strip crosses N1 at \|s\| below 0.01. |
| N1N2 (required) | **edge-fixed CERTIFIED-FAIL** | 0.005 / **0.94** / 0.055 | Edge. Each u-edge image sweeps N2 from u = +450 to u = -740: leaves of one edge land on both sides, and a leaf near s = -0.06 (L), +0.06 (R) lies inside \|u\| < 1. |
| N2N3 (required) | **edge-fixed CERTIFIED-FAIL** | 0.005 / **0.88** / 0.115 | Edge. Sweep from u = +19 to -23; crossings at s = -0.10 (L) and +0.10 (R); several top-level leaves lie inside \|u\| < 1. |
| N3N4 (required) | **edge-fixed CERTIFIED-FAIL** | 0.005 / **0.88** / 0.115 | Edge. Sweep from u = +20 to -22; crossings at s = -0.055 (L) and -0.01 (R). |
| N4N5 (required) | **edge-fixed CERTIFIED-FAIL** | 0.005 / **0.93** / 0.065 | Edge. Sweep from u = +509 to -644, and the tangent itself contracts 25 times: the leaf at s = 0 of both edges lands at \|u\| < 0.05. |
| N5N0 (required) | **edge-fixed CERTIFIED-FAIL** | 0.003 / **0.94** / 0.057 | Edge. Sweep from u = -309 to +374 through the saddle; the tangent contracts about 1000 times, so both edges land at u = 0.001 for s = 0. |
| N5N1 (optional) | **edge-fixed CERTIFIED-FAIL** | 0.003 / **0.93** / 0.067 | Edge. Sweep from u = +807 to -1280; crossing near s = -0.03 on both edges. |

- **Edge column call, all six: edge-fixed CERTIFIED-FAIL**, with `orient_certified_fail=1` and `certified_fail_b` > 0. I do not call "not finishing" for any; N2N3 and N3N4 (the swing to r = 46.8M) are the slow ones.
- **Ungraded extras.** leaves_b between 170 and 320 per covering (128 top leaves plus the bisection at the two crossings of u = -1 and u = +1 on each edge); certified_fail_b between 15 and 90; fail_b a few more than that (the depth-12 leaves that straddle u = +-1 stay uncertified). Interior chunks of the six: a = 1 is true in the model, but the class is already fixed.
- **No interior failure anywhere in the model.** On a 41 x 41 grid per covering, no image point lies in F = {\|u\| <= 1, \|s\| >= 1}, and no orbit leaves the domain x >= 1.05 within one return.

## 2. Chain class

| Chain class | Probability |
|---|---|
| **CERTIFIED-FAIL** (modal call) | 0.955 |
| UNDECIDED | 0.020 |
| HARNESS-ERROR or reading withheld | 0.023 |
| RHO>1 | 0.002 |

**P(no horseshoe certified) = 1 - P(RHO>1) = 0.998.**

## 3. Reasoning

**The map.** Kerr separates, so on the section the return map is exactly P = (radial flow in Mino time) run for the polar Mino period of that orbit's Q:
- Q(x, p_x) follows from R(r) = (p_x Delta / k)^2, r = kx + M;
- each Q-level curve is invariant, and P moves a point along its own curve by Lambda_theta(Q).

**Checks of the model against what is known.**
- Q_s = 0.7407624527609606 M^2 (registered 0.740762452760964).
- lam_u = exp(kappa Lambda_theta) = 62.620268582 (ARM.json: 62.620268580).
- P maps each registered centre onto the next to 9 digits, N0 through N5.
- It reproduces the two known edge results: N0N0 edges at u = -61.6 and +63.7 (orient LR), N0N1 edges at u = +156 and -220 (orient RL), no failure.

**How integrability shows up.**
- W^u = W^s. The chain's U_j is the tangent of the separatrix. In the frame (tangent T, normal N), DP = [[sigma, c], [0, 1/sigma]]: sigma is the stretch of the tangent, c the shear from the twist (neighbouring Q-curves advance by different amounts).
- No transverse stable direction exists. The prereg records it (B15d section 2): sin of the angle between U_j and S_j is 1.9e-3 down to 6e-11. So the registered frame took S = U rotated by 90 degrees.
- At the saddle the two eigen-directions are 0.031 rad apart, both along p_x with slopes +-65. A step of 0.005 in x (the half-width along S) therefore carries 0.32 of unstable coordinate, while the half-length 0.01 along U carries only 0.02. The image of a u-edge is stretched 16 times more than the image of the set's own length.
- Result: the image of N1 is a strip along W^u about 1500 target-units long, and BOTH u-edges run its whole length. Condition (b) needs the two edges on opposite sides; here each edge alone lands on both sides. hs_cover certifies that twice: `orient_certified_fail=1` (one edge's leaves in both sides), and a leaf with u certainly inside (-1, 1).
- Second half of the loop (N4N5, N5N0): the tangent is now the contracting direction (sigma = 0.04 and 0.001). Even without the shear the u-edges land inside the target. This is the HH swap twin's mechanism: there all 6 coverings were edge-fixed with certified_fail_b from 123 to 309.
- N0N0 and N0N1 pass because N0 alone has a real hyperbolic frame (the saddle's e_u, e_s). A saddle's self-covering is allowed on an integrable system (PREREG 6.3): it gives a periodic point, not entropy. The chain cannot close because every later set lacks a contracting direction transverse to U.

**Use of the controls.**
- Recipe (HH, same recipe): all 6 required coverings CERTIFIED, with b = 1 at 128 leaves and leaves_a from 261 to 2870. On HH the stable direction makes an O(1) angle with U, so U rotated by 90 degrees stretches less than U. That is the difference to Kerr, and it is why a Kerr failure is informative.
- Twin swap: shows the code reaches the certified edge failure and the orientation contradiction in practice.
- B15c arm: the arm found the chain only as an unfrozen diagnostic, on the separatrix to 2.8e-10 in Q. The sets are slivers across a single invariant curve.

**Why not higher than 0.94 per covering.** The model is float and exact in structure; the open part is the rigorous enclosure. Leaves far from the crossing sit hundreds of units outside (N1N2, N4N5, N5N0, N5N1), so even poor enclosures certify their side. N2N3 and N3N4 have only +-20 units of room and the longest integration.

## 4. Falsifiers

**Refute the reasoning:**
1. Any of the six edge chunks completes with b = 1.
2. A completed edge chunk among the six in which the certified landings of each edge are all on one side (no orientation contradiction) while leaves do land.
3. The sweep runs the other way or elsewhere: for N1N2 the L edge must land right for s < -0.06 and left for s > -0.06 (R edge: right for s < +0.06). A crossing more than 0.05 in s away from the values in the table refutes the float map.
4. Any S4 or S9 throw on a piece of these sets (the model has every orbit inside the domain for one return).
5. N0N0 or N0N1 reading CERTIFIED-FAIL, or any HARNESS-ERROR caused by a merged class that disagrees with the edge-fixed class.
6. RHO>1.

**Only miss a probability:** a covering left UNDECIDED because every leaf near the crossing stays uncertified and the far leaves fail to land (enclosure limit); N0N0 or N0N1 UNDECIDED from depth-cap interior leaves; a chunk that never completes.

## 5. Literature (all from memory, not checked at source)
- Arioli and Zgliczynski 2001, covering relations (the code's "AZ 2001 Def. 2"); Zgliczynski and Gidea, J. Differential Equations 202 (2004).
- Carter 1968, the fourth constant Q; Mino 2003, Mino time; Schmidt 2002 and Fujita and Hikida 2009, Mino-time frequencies.
- Levin and Perez-Giz 2009, homoclinic orbits of Kerr (cited in the prereg).

No statement above rests on a specific section or equation of these.

## Appendix: the float model (not committed elsewhere; run with sims/.venv python, about 20 s)

```python
# Float model of the Kerr section map (separable: P = radial Mino flow for the polar Mino period of that Q).
# Model only; no rigorous output is read. [model: Fable 5.2]
import json, math, numpy as np
from fractions import Fraction as F
from scipy.integrate import solve_ivp, quad
M,a,k,E,L=89.0,80.0,39.0,0.98,222.5
Dl=lambda r: r*r-2*M*r+a*a
def Qof(x,p):
    r=k*x+M; D=Dl(r); return ((E*(r*r+a*a)-a*L)**2-(p*D/k)**2)/D - r*r-(L-a*E)**2
def R(r,Q): return (E*(r*r+a*a)-a*L)**2-Dl(r)*(r*r+(L-a*E)**2+Q)
def dR(r,Q): return 4*E*r*(E*(r*r+a*a)-a*L)-(2*r-2*M)*(r*r+(L-a*E)**2+Q)-Dl(r)*2*r
def Lam(Q):
    A=a*a*(1-E*E); B=Q+A+L*L; disc=math.sqrt(B*B-4*A*Q); zm=(B-disc)/(2*A); zp=(B+disc)/(2*A)
    return 4*quad(lambda f: 1/math.sqrt(A*(zp-zm*math.sin(f)**2)),0,math.pi/2,epsabs=1e-14,epsrel=1e-13)[0]
def P(x,p):
    Q=Qof(x,p); r=k*x+M; v=Dl(r)*p/k; T=Lam(Q)
    ev=lambda t,y: y[0]-(M+0.05*k); ev.terminal=True
    s=solve_ivp(lambda t,y:[y[1],0.5*dR(y[0],Q)],[0,T],[r,v],method="DOP853",rtol=1e-12,atol=1e-9,events=ev)
    if s.status==1: return None
    r2,v2=s.y[0,-1],s.y[1,-1]; return ((r2-M)/k, k*v2/Dl(r2))
B=json.load(open("/Users/sumit/Github/quantum/qsim/capd/horseshoe_results/kerr/b15d/kerr/build.json"))
S={n:[[float(F(c)) for c in v] for v in B["sets"][n]] for n in B["sets"]}
def pt(n,u,s): c,U,V=S[n]; return (c[0]+u*U[0]+s*V[0], c[1]+u*U[1]+s*V[1])
def chart(n,w): c,U,V=S[n]; return np.linalg.solve(np.array([[U[0],V[0]],[U[1],V[1]]]),np.array([w[0]-c[0],w[1]-c[1]]))
if __name__=="__main__":
    zs=(1.8411884397812655,0.0); Qs=Qof(*zs); rs=k*zs[0]+M
    print("Q_s/M^2",Qs/M**2,"(prereg 0.740762452760964)  Lam_theta",Lam(Qs))
    d2=(dR(rs+1e-3,Qs)-dR(rs-1e-3,Qs))/2e-3; print("lam_u model",math.exp(math.sqrt(d2/2)*Lam(Qs)),"(ARM 62.6203)")
    for n in S: c=S[n][0]; print(n,"centre",c,"Q/Qs-1 %.2e"%(Qof(*c)/Qs-1),"-> P(centre)",P(*c))
    for a_,b_ in [("N0","N0"),("N0","N1"),("N1","N2"),("N2","N3"),("N3","N4"),("N4","N5"),("N5","N0"),("N5","N1")]:
        out=[]
        for side in (-1,1):
            us=[]; nret=0; ss=np.linspace(-1,1,129)
            for s in ss:
                w=P(*pt(a_,side,s))
                if w is None: us.append((s,None,None)); continue
                nret+=1; u,sj=chart(b_,w); us.append((s,u,sj))
            ok=[t for t in us if t[1] is not None]
            uu=np.array([t[1] for t in ok]); sj=np.array([t[2] for t in ok])
            ins=[t for t in ok if abs(t[1])<1]
            out.append(f"   edge {'L' if side<0 else 'R'}: returns {nret}/129, u_j range [{uu.min():.3g}, {uu.max():.3g}], left {int((uu<-1).sum())} right {int((uu>1).sum())} inside {len(ins)}"+(f" (s in [{min(t[0] for t in ins):.3f},{max(t[0] for t in ins):.3f}], s_j there [{min(t[2] for t in ins):.3g},{max(t[2] for t in ins):.3g}])" if ins else "")+f"; u_j at s=-1,0,1: {us[0][1]}, {us[64][1]}, {us[128][1]}")
        # interior (a): sample grid
        bad=0; nor=0; tot=0
        for u in np.linspace(-1,1,41):
            for s in np.linspace(-1,1,41):
                tot+=1; w=P(*pt(a_,u,s))
                if w is None: nor+=1; continue
                uj,sj=chart(b_,w)
                if abs(uj)<=1 and abs(sj)>=1: bad+=1
        print(f"{a_}=>{b_}: interior grid {tot}: no-return/out-of-domain {nor}, points truly in F (|u|<=1,|s|>=1) {bad}"); print("\n".join(out))
```
