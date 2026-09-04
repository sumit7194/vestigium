"""
EXP-001 measurement core: the holographic (Einstein) corner function, the SSA lower bound,
and the free-field tabulated values, all normalised by C_T, at the angles where published
free-field values exist. Every number's provenance is named in the comments.

Conventions (M2):
  theta      opening angle of the corner, 0 < theta < pi (radians)
  a(theta)   coefficient of -log(H/delta) in S_EE for one corner
  C_T        stress-tensor 2-pt normalisation, Osborn-Petkou convention:
             C_T(real scalar) = 3/(32 pi^2),  C_T(Dirac fermion) = 3/(16 pi^2)
             [BMW PRL 115, 021602 (2015), text before Fig. 2]
  Holography (Einstein, AdS4): Hirata-Takayanagi JHEP 0702:042 eqs (5.1)-(5.5):
       Omega/2 = g0 sqrt(1+g0^2) Int_0^inf dz / ((z^2+g0^2) sqrt((z^2+g0^2+1)(z^2+2g0^2+1)))
       f(Omega) = Int_0^inf dz [1 - sqrt((z^2+g0^2+1)/(z^2+2g0^2+1))]
       a_E(Omega) = (L^2/(2G)) f(Omega)  [from S_A = (L^2/4G)(2H/delta - 2 f log(H/delta))]
       C_T = 3 L^2/(pi^3 G)  [BMW PRL, holographic C_T for Einstein gravity]
       => a_E/C_T = (pi^3/6) f(Omega).
  Bound: a_min(theta) = (pi^2 C_T/3) log[1/sin(theta/2)]  [Bueno & Witczak-Krempa PRB 93, 045131, eq. II.2]
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from math import pi, gamma, log, sin, sqrt

CT_S = 3/(32*pi**2)      # real scalar
CT_F = 3/(16*pi**2)      # Dirac fermion (2-component, 3d)

def omega_of_g0(g0):
    # substitution z = g0*t removes the width-g0 peak at z=0:
    # Omega/2 = sqrt(1+g0^2) Int_0^inf dt / ((t^2+1) sqrt((g0^2(t^2+1)+1)(g0^2(t^2+2)+1)))
    # g0 -> 0 gives Omega -> pi (smooth); g0 -> inf gives Omega ~ 1/g0 -> 0 (sharp)
    g2 = g0*g0
    f = lambda t: 1.0/((t*t+1)*np.sqrt((g2*(t*t+1)+1)*(g2*(t*t+2)+1)))
    val, err = quad(f, 0, np.inf, limit=1000, epsabs=0, epsrel=1e-13)
    return 2*np.sqrt(1+g2)*val

def f_of_g0(g0):
    # integrand is a bump of width max(1, g0) in z; fine for quad
    g2 = g0*g0
    f = lambda z: 1.0-np.sqrt((z*z+g2+1)/(z*z+2*g2+1))
    val, err = quad(f, 0, np.inf, limit=1000, epsabs=0, epsrel=1e-13, points=None)
    return val

def g0_of_omega(om):
    # omega is DEcreasing in g0
    return brentq(lambda g: omega_of_g0(g)-om, 1e-7, 1e5, xtol=1e-15, rtol=1e-14)

def aE_over_CT(theta):
    return (pi**3/6)*f_of_g0(g0_of_omega(theta))

def amin_over_CT(theta):
    return (pi**2/3)*log(1/sin(theta/2))

def aEMI_over_CT(theta):
    # Extensive-mutual-information model closed form, BMW PRL eq.(14); NOT a CFT (Agon-Bueno-Casini 2021)
    return (pi**2/8)*(1+(pi-theta)/np.tan(theta))

if __name__ == "__main__":
    # ---- Tier-1 style controls on my own holographic evaluation ----
    # (i) sigma/C_T -> pi^2/24 as theta->pi ; (ii) kappa/C_T -> pi^2 Gamma(3/4)^4/6 as theta->0
    eps = 1e-3
    sig = aE_over_CT(pi-eps)/eps**2
    print(f"control sigma/C_T from theta=pi-{eps}: {sig:.6f}   exact pi^2/24 = {pi**2/24:.6f}   rel.err {sig/(pi**2/24)-1:.2e}")
    th0 = 1e-3
    kap = aE_over_CT(th0)*th0
    kap_exact = pi**2*gamma(0.75)**4/6
    print(f"control kappa/C_T from theta={th0}: {kap:.6f}   exact pi^2 G(3/4)^4/6 = {kap_exact:.6f}   rel.err {kap/kap_exact-1:.2e}")
    # (iii) published spot values: BWK Table 1: a_E(pi/2)/C_T = 1.222, a_E(3pi/4)/C_T = 0.264
    print(f"control a_E(pi/2)/C_T = {aE_over_CT(pi/2):.4f} (BWK Table 1: 1.222) ; a_E(3pi/4)/C_T = {aE_over_CT(3*pi/4):.4f} (BWK: 0.264)")
    # (iv) CHL Table 1 normalised holographic values: s_H(pi/2)=0.02321, s_H(3pi/4)=0.005019 with sigma_H = 1/128
    CT_H = (1/128)/(pi**2/24)
    print(f"control CHL-normalised s_H(pi/2) = {aE_over_CT(pi/2)*CT_H:.5f} (CHL: 0.02321) ; s_H(3pi/4) = {aE_over_CT(3*pi/4)*CT_H:.6f} (CHL: 0.005019) ; kappa_H = {kap_exact*CT_H:.4f} (CHL: 0.0704)")

    print("\n---- Free-field tabulated values (sources in comments) ----")
    # Casini-Huerta-Leitao NPB 814 (2009) Table 1: COMPLEX scalar s_S(pi/2)=0.02366, s_S(3pi/4)=0.005040, kappa_S=0.0794;
    #                                              Dirac s_D(pi/2)=0.02329, s_D(3pi/4)=0.005022, kappa_D=0.0722
    # Helmes et al PRB 94, 125142 (2016) Table 1 (complex boson, alpha=1: series / ansatz / lattice) and Table 2 (Dirac)
    helmes_angles = {0.5: np.arctan(0.5), 1: pi/4, 2: np.arctan(2.0), 'inf': pi/2, -2: pi-np.arctan(2.0), -1: 3*pi/4, -0.5: pi-np.arctan(0.5)}
    boson_ansatz  = {0.5:0.156, 1:0.0810, 2:0.0482, 'inf':0.0237, -2:0.0105, -1:0.00504, -0.5:0.00171}
    boson_lattice = {0.5:0.154, 1:0.0809, 2:0.0483, 'inf':0.0236, -2:0.0105, -1:0.00507, -0.5:0.00170}
    boson_series  = {0.5:0.1453,1:0.08037,2:0.04816,'inf':0.02367,-2:0.01051,-1:0.005040,-0.5:0.001705}
    fermion_ansatz  = {0.5:0.146, 1:0.0776}   # rest filled after Table 2 is read in full
    fermion_lattice = {0.5:0.147, 1:0.0777}
    fermion_series  = {0.5:0.1334,1:0.07654}
    CT_CS = 2*CT_S  # complex scalar
    print(f"{'tan':>5} {'theta(deg)':>10} {'holo':>8} {'bound':>8} {'EMI':>8} | {'scalar/CT (ans,lat,ser)':>28} | {'fermion/CT (ans,lat,ser)':>28}")
    for k,th in helmes_angles.items():
        h = aE_over_CT(th); b = amin_over_CT(th); e = aEMI_over_CT(th)
        s = [boson_ansatz[k]/CT_CS, boson_lattice[k]/CT_CS, boson_series[k]/CT_CS]
        f = [fermion_ansatz.get(k,np.nan)/CT_F, fermion_lattice.get(k,np.nan)/CT_F, fermion_series.get(k,np.nan)/CT_F]
        print(f"{str(k):>5} {np.degrees(th):10.2f} {h:8.4f} {b:8.4f} {e:8.4f} | {s[0]:8.4f} {s[1]:8.4f} {s[2]:8.4f}  | {f[0]:8.4f} {f[1]:8.4f} {f[2]:8.4f}")

    print("\n---- CHL 2009 exact-method values normalised ----")
    for name, vals, CT in [("real scalar (CHL complex/2)", (0.02366/2, 0.005040/2, 0.0794/2), CT_S), ("Dirac", (0.02329, 0.005022, 0.0722), CT_F)]:
        print(f"{name:28s} a(pi/2)/CT={vals[0]/CT:.4f}  a(3pi/4)/CT={vals[1]/CT:.4f}  kappa/CT={vals[2]/CT:.4f}")
    print(f"{'holographic Einstein':28s} a(pi/2)/CT={aE_over_CT(pi/2):.4f}  a(3pi/4)/CT={aE_over_CT(3*pi/4):.4f}  kappa/CT={kap_exact:.4f}")
    print(f"{'SSA bound':28s} a(pi/2)/CT={amin_over_CT(pi/2):.4f}  a(3pi/4)/CT={amin_over_CT(3*pi/4):.4f}  kappa/CT= (log only)")

    print("\n---- ../quantum (vestigium) lattice real-scalar values vs exact and vs bound ----")
    # ../quantum/qsim/corner_angles.json values: a60=0.024232, a90(square, s=1)=0.011604, a120=0.0038955 ; corner_s6.json: B=-0.04669 -> a90=0.011673
    for deg, val in [(60, 0.024232), (90, 0.011604), (90, 0.046691/4), (120, 0.0038955)]:
        th = np.radians(deg)
        print(f"a({deg}) lattice={val:.6f}  /CT={val/CT_S:.4f}   holo/CT={aE_over_CT(th):.4f}  bound/CT={amin_over_CT(th):.4f}  bound={amin_over_CT(th)*CT_S:.6f}  {'BELOW BOUND' if val<amin_over_CT(th)*CT_S else 'ok'}")
