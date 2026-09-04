"""
EXP-001, part 3: Einsteinian-cubic-gravity corner function at all angles (the only holographic
family known to change the SHAPE of a(theta)/C_T), and the sensitivity of a(theta)/C_T to the
sharp-limit coefficient kappa via the sigma-kappa trial function.

Sources:
  a_E(h0), theta(h0):  Bueno-Camps-Vilar Lopez JHEP04(2021)145 eqs (276),(277)  [h0 = 1/g0 of Hirata-Takayanagi]
  a_ECG(h0):           same paper eq (293); C_T^ECG = (1-3 mu) C_T^E (eq. 2174 in ar5iv text / their sec. 5)
  allowed mu:          -0.00322 <= mu <= 0.00312  <->  -4 <= t4 <= +4  (BCV 2021 after eq. 297)
  trial function:      BMW JHEP09(2015)091 as restated in BCV eq (261) / Helmes et al eq (21):
     a~(theta) = 2pi(kappa-3pi sigma)/(pi^2-6) (theta-pi)^2/(theta(2pi-theta)) - 3(2kappa-pi^3 sigma)/(pi(pi^2-6)) [1+(pi-theta)cot theta]
Controls (must pass before any number is quoted): sigma_ECG/sigma_E=(1-3mu), kappa_ECG/kappa_E=(1-123mu/20) [BCV eqs 295,297].
"""
import sys, numpy as np
from math import pi, gamma, sin, log
from scipy.integrate import quad
sys.path.insert(0, __file__.rsplit('/',1)[0])
from exp001_measure import aE_over_CT, g0_of_omega, amin_over_CT

def I_ecg(h0):
    h2=h0*h0
    f=lambda y: 3*(1+h2)*(15+8*h2*h2*(1+y*y)**2+h2*(23+16*y*y))/(4*(1+h2*(1+y*y))**3.5*np.sqrt(2+h2*(1+y*y)))
    v,e=quad(f,0,np.inf,limit=1000,epsabs=0,epsrel=1e-12)
    return v

def aECG_over_CT(theta, mu):
    h0 = 1.0/g0_of_omega(theta)
    aE = aE_over_CT(theta)                      # = (pi^3/6) f
    corr = (pi**3/6)*I_ecg(h0)                  # (mu L^2/2G) I  normalised by C_T^E = 3L^2/(pi^3 G)
    return ((1+3*mu)*aE - mu*corr)/(1-3*mu)

def trial_over_CT(theta, kappa_over_CT, sigma_over_CT=pi**2/24):
    k, s = kappa_over_CT, sigma_over_CT
    return 2*pi*(k-3*pi*s)/(pi**2-6)*(theta-pi)**2/(theta*(2*pi-theta)) - 3*(2*k-pi**3*s)/(pi*(pi**2-6))*(1+(pi-theta)/np.tan(theta))

if __name__=="__main__":
    kapE = pi**2*gamma(0.75)**4/6
    # ---- controls ----
    for mu in (0.00312, -0.00322):
        eps=1e-3; s_ratio = aECG_over_CT(pi-eps,mu)*(1-3*mu)/aE_over_CT(pi-eps)   # sigma_ECG/sigma_E (un-normalise C_T)
        th=1e-3;  k_ratio = aECG_over_CT(th,mu)*(1-3*mu)/aE_over_CT(th)
        print(f"control mu={mu:+.5f}: sigma_ECG/sigma_E={s_ratio:.6f} (exact {1-3*mu:.6f}) ; kappa_ECG/kappa_E={k_ratio:.6f} (exact {1-123*mu/20:.6f})")
    print()
    angles=[(26.57,np.arctan(0.5)),(45,pi/4),(60,pi/3),(63.43,np.arctan(2.0)),(90,pi/2),(116.57,pi-np.arctan(2.0)),(120,2*pi/3),(135,3*pi/4),(153.43,pi-np.arctan(0.5))]
    print(f"{'deg':>7} {'Einstein':>9} {'ECG t4=+4':>10} {'dev%':>6} {'ECG t4=-4':>10} {'dev%':>6} | {'trial(kE)':>9} {'res%':>6} {'trial(k_s)':>10} {'trial(k_f)':>10} | d(a/CT)/d(k/CT)")
    for deg,th in angles:
        e=aE_over_CT(th); p=aECG_over_CT(th,0.00312); m=aECG_over_CT(th,-0.00322)
        tE=trial_over_CT(th,kapE); tS=trial_over_CT(th,0.0794/(3/(16*pi**2))); tF=trial_over_CT(th,0.0722/(3/(16*pi**2)))
        sens=(trial_over_CT(th,kapE+0.01)-trial_over_CT(th,kapE-0.01))/0.02
        print(f"{deg:7.2f} {e:9.4f} {p:10.4f} {(p/e-1)*100:+6.2f} {m:10.4f} {(m/e-1)*100:+6.2f} | {tE:9.4f} {(tE/e-1)*100:+6.2f} {tS:10.4f} {tF:10.4f} | {sens:.4f}")
    print("\nTrial function vs exact free fields (CHL Table 1 / Helmes ansatz):")
    CTc=3/(16*pi**2)
    for name,k,ex in [("complex scalar",0.0794/CTc,{pi/2:0.02366/CTc,3*pi/4:0.005040/CTc,pi/4:0.0810/CTc}),("Dirac",0.0722/CTc,{pi/2:0.02329/CTc,3*pi/4:0.005022/CTc,pi/4:0.0776/CTc})]:
        for th,v in ex.items():
            print(f"  {name:15s} theta={np.degrees(th):6.1f}: trial {trial_over_CT(th,k):.4f}  exact {v:.4f}  ({(trial_over_CT(th,k)/v-1)*100:+.2f}%)")
    print("\nWhat a theta=pi/2 measurement with +-0.1 on a/C_T says about kappa/C_T (trial-function slope):")
    s90=(trial_over_CT(pi/2,kapE+0.01)-trial_over_CT(pi/2,kapE-0.01))/0.02
    print(f"  slope at pi/2 = {s90:.4f}  ->  delta(kappa/C_T) = 0.1/{s90:.4f} = +-{0.1/s90:.2f}   (band of all known theories: {kapE*(1-123*0.00312/20)/(1-3*0.00312):.3f} .. {0.0794/CTc:.3f}, width {0.0794/CTc-kapE*(1-123*0.00312/20)/(1-3*0.00312):.3f})")
