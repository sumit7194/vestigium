#!/usr/bin/env python3
"""Does the zero mode contaminate the corner spread, and does it refine away?

WHY: k=0 contributes ~20% of B (see corner_coefficient.py). All four regulators
weight it identically -- reg(0,0) = m^2 -- but the NON-COMMON residual is a
fifth of the regulator signal, so the mode is mostly but not cleanly common.
If that residual carried the observed s^-2 falloff, the falloff would be a
finite-volume artifact vanishing rather than a coefficient becoming universal.

CONDITION: l/L is held FIXED at 0.025..0.125, which is the study's own
parameterisation (ls = [l*s for l in range(4,21,2)] with L = 160s). The bridge
measured the same effect at FIXED l instead, got a clean L^-2.3, and retracted
it -- their setup answered a question the study never asks. Their lesson, which
is the better one: a pre-registration that fixes what you will CONCLUDE from
each outcome still lets you measure the wrong QUANTITY.

RESULT, three resolutions:

    s   L    signal      total shift   non-common   nc/signal
    1  160   0.000789    0.009539      0.000171       21.6%
    2  320   0.000115    0.009627      0.000048       41.5%
    3  480   0.000055    0.009602      0.000015       27.5%

1. THE TOTAL SHIFT IS FLAT: L^+0.01 then L^-0.01. Solid across three points and
   physically expected -- the rank-1 eigenvalue is c*l^2, contributing
   log(c*l^2) = log c + 2 log l to S, so all the L-dependence sits in log c,
   which moves the CONSTANT and not the log coefficient. B picks up a fixed
   amount at every resolution.

   So the original hypothesis is DEAD: the zero mode is not a vanishing
   finite-volume artifact that could masquerade as the s^-2 falloff.

2. THE NON-COMMON RESIDUAL IS 22-41% OF THE REGULATOR SIGNAL at all three
   resolutions. That is the open systematic and it is confirmed, not resolved.

3. ITS SCALING IS UNDETERMINED. I reported "the contamination fraction grows"
   from s=1,2 (21.6% -> 41.5%) and sent that to the bridge. The third point
   gives 27.5% and the exponents swap: non-common goes L^-1.84 then L^-2.81
   while the signal goes L^-2.78 then L^-1.80. NON-MONOTONE, and a two-point
   slope again -- the same sparse-agreement error I corrected in the README this
   afternoon and in the cost probe this evening, for the third time today.
"""
def K2(kx,ky): return (2-2*np.cos(kx))+(2-2*np.cos(ky))
def K4(kx,ky):
    f=lambda k:(4/3)*(2-2*np.cos(k))-(1/12)*(2-2*np.cos(2*k)); return f(kx)+f(ky)
def ent(XA,PA):
    ev,U=np.linalg.eigh(XA); Xh=(U*np.sqrt(np.clip(ev,1e-300,None)))@U.T
    C=Xh@PA@Xh; nu=np.sqrt(np.clip(np.linalg.eigvalsh(0.5*(C+C.T)),0.25,None))
    nu=np.maximum(nu,0.5+1e-12); a,b=nu+0.5,nu-0.5
    return float(np.sum(a*np.log(a)-b*np.log(b)))
def run(s):
    L=160*s; m=0.01/s; ls=[l*s for l in range(4,21,2)]   # l/L FIXED = the study's condition
    n=np.arange(L); kx,ky=np.meshgrid(2*np.pi*n/L,2*np.pi*n/L,indexing="ij")
    R={"nn":m*m+K2(kx,ky),"improved":m*m+K4(kx,ky),
       "higher_deriv":m*m+K2(kx,ky)+0.25*K2(kx,ky)**2,
       "smeared":m*m+K2(kx,ky)*np.exp(0.15*K2(kx,ky))}
    B={}; B0={}
    for nm,rk in R.items():
        w=np.sqrt(rk); GP=np.real(np.fft.ifft2(w))/2.0
        for drop in (False,True):
            inv=1.0/w
            if drop: inv=inv.copy(); inv[0,0]=0.0
            GX=np.real(np.fft.ifft2(inv))/2.0
            S=[]
            for l in ls:
                o=(L-l)//2; st=np.array([(o+i,o+j) for i in range(l) for j in range(l)])
                dx=(st[:,0][:,None]-st[:,0][None,:])%L; dy=(st[:,1][:,None]-st[:,1][None,:])%L
                S.append(ent(GX[dx,dy],GP[dx,dy]))
            M=np.vstack([4*np.array(ls,float),np.log(ls),np.ones(len(ls))]).T
            c,*_=np.linalg.lstsq(M,np.array(S),rcond=None)
            (B0 if drop else B)[nm]=abs(c[1])
            del GX
    names=list(R); sh=[B[n_]-B0[n_] for n_ in names]
    return dict(s=s,L=L,l_over_L="0.025..0.125 (fixed)",
                signal=max(B.values())-min(B.values()),
                shift_mean=sum(sh)/len(sh), noncommon=max(sh)-min(sh))
s=int(sys.argv[1]); print(json.dumps(run(s)))
