"""
Experiment 4 — standard QM vs objective collapse (CSL/QMUPL toy).

Same stochastic equation as weak_measurement.py, ONE change of meaning:
there is NO detector. In collapse models the localization noise is a law of
nature, and its strength for a rigid object scales as N^2 (N nucleons moving
together). Small things stay quantum ~forever; big things localize instantly;
in between sits a testable edge.

    d|psi> = [ -iH dt - k (x-<x>)^2 dt + sqrt(2k) (x-<x>) dW ] |psi>,
    k = kappa0 * N^2         (single-nucleon rate kappa0, mass amplification N^2)

We prepare a cat (two humps, separation d) and read its MOMENTUM-space fringes
(what a matter-wave interferometer effectively measures).  Analytic target for
the quadratic model: coherence(x,x') decays at rate k (x-x')^2, so fringe
visibility V(T) = exp(-k d^2 T).

Deliverables:
  1) MECHANISM (simulated): ensemble momentum fringes for light/medium/heavy
     objects -- full / faded / gone; measured V(N) vs the analytic decay.
  2) NO DETECTOR NEEDED: single trajectories at large N commit to one hump on
     their own (nature rolls the dice; nobody watching).
  3) REAL UNITS (analytic): V = exp(-lambda N^2 T) with T = 10 ms flight,
     lambda_GRW = 1e-16 /s vs lambda_Adler = 1e-8 /s; markers at real
     experiments (C70, Fein 25 kamu, levitated nanoparticle, MAQRO) -- the
     actual exclusion logic: Adler's edge sits at current experiments,
     GRW's edge needs ~1e9 amu.

Honesty notes: quadratic (QMUPL-like) localization = small-separation limit of
CSL; real CSL saturates at Gamma = lambda*N^2 for d >> r_C (used in the real-
units panel).  The strongest current bounds are non-interferometric (X-ray,
LISA Pathfinder) -- this toy shows the interferometric mechanism.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(11)

# ---------- batch SSE evolver (same scheme as weak_measurement.py, Ito-correct) ----
def run_sse(psi0, x, k, T, dt, M):
    N = x.size; dx = x[1] - x[0]
    kgrid = 2*np.pi*np.fft.fftfreq(N, dx)
    kin = np.exp(-0.5j * kgrid**2 * dt)
    psi = np.tile(psi0, (M, 1)).astype(np.complex128)
    steps = int(round(T/dt))
    Pr_t = []
    for s in range(steps):
        P = np.abs(psi)**2 * dx
        P /= P.sum(1, keepdims=True)
        xm = (x[None, :]*P).sum(1, keepdims=True)
        Pr_t.append(P[:, x > 0].sum(1))
        psi = np.fft.ifft(np.fft.fft(psi, axis=1)*kin, axis=1)
        dW = rng.normal(0.0, np.sqrt(dt), (M, 1))
        psi *= np.exp(-2*k*(x[None, :]-xm)**2*dt + np.sqrt(2*k)*(x[None, :]-xm)*dW)
        psi /= np.sqrt((np.abs(psi)**2).sum(1, keepdims=True)*dx)
    return psi, np.array(Pr_t)

def momentum_dist(psi, x):
    dx = x[1] - x[0]; N = x.size
    ft = np.fft.fftshift(np.fft.fft(psi, axis=1), axes=1) * dx
    p = np.fft.fftshift(2*np.pi*np.fft.fftfreq(N, dx))
    P = np.abs(ft)**2
    return p, P.mean(0) / np.trapezoid(P.mean(0), p)     # ensemble average

def visibility(p, P, d):
    """contrast between the central fringe max (p=0) and first min (p=pi/d)."""
    Pmax = np.interp(0.0, p, P)
    Pmin = 0.5*(np.interp(np.pi/d, p, P) + np.interp(-np.pi/d, p, P))
    return (Pmax - Pmin) / (Pmax + Pmin)

# ---------- setup: the cat ----------
Ngrid, L = 1024, 120.0
x = np.linspace(-L/2, L/2, Ngrid, endpoint=False)
sig, d = 2.5, 30.0
g = lambda c: np.exp(-(x-c)**2/(4*sig**2))
cat = g(-d/2) + g(d/2)
cat /= np.sqrt((np.abs(cat)**2).sum()*(x[1]-x[0]))

kappa0, T, dt = 1e-9, 5.0, 0.005          # single-nucleon rate (sim units), flight time
Ns = np.array([50, 100, 200, 400, 700, 1000, 1500, 2500])
M = 200

# ---------- 1) mechanism: V(N) from simulation vs analytic ----------
print("MECHANISM (sim units): V(N) vs analytic exp(-kappa0 N^2 d^2 T)")
Vm, dists, Pr_big = [], {}, None
for Nn in Ns:
    k = kappa0 * Nn**2
    psi, Pr_t = run_sse(cat, x, k, T, dt, M)
    p, P = momentum_dist(psi, x)
    Vm.append(visibility(p, P, d))
    if Nn in (100, 700, 2500):
        dists[Nn] = (p, P)
    if Nn == Ns[-1]:
        Pr_big = Pr_t
Vm = np.array(Vm)
Vrel = Vm / Vm[0]                                     # envelope-calibrated
Vth = np.exp(-kappa0*(Ns.astype(float)**2 - float(Ns[0])**2) * d**2 * T)
for Nn, vm, vt in zip(Ns, Vrel, Vth):
    print(f"   N={Nn:5d}:  V_sim(rel) = {vm:6.3f}   analytic = {vt:6.3f}"
          f"   (kd^2T = {kappa0*Nn**2*d**2*T:8.3f})")
err = np.max(np.abs(Vrel - Vth))
print(f"   max |sim - analytic| = {err:.3f}")

# no detector needed: commitment at the largest N
final = Pr_big[-1]
committed = np.mean((final > 0.9) | (final < 0.1))
frac_r = np.mean(final[(final > 0.9) | (final < 0.1)] > 0.5)
print(f"\nNO DETECTOR: at N={Ns[-1]}, {committed*100:.0f}% of runs localized to one hump "
      f"by T; fraction right = {frac_r:.2f} (symmetric cat -> 0.50)")

# ---------- 3) real units ----------
Treal = 0.01                                   # 10 ms interferometer flight
lam_grw, lam_adler = 1e-16, 1e-8
m = np.logspace(0, 12, 600)                    # mass in amu ~ nucleon count
V_grw = np.exp(-lam_grw * m**2 * Treal)
V_adl = np.exp(-lam_adler * m**2 * Treal)
edge = lambda lam: np.sqrt(1.0/(lam*Treal))
print(f"\nREAL UNITS (T = 10 ms): collapse edge N* = sqrt(1/(lambda T))")
print(f"   GRW   (1e-16/s): N* = {edge(lam_grw):.1e} amu   (needs MAQRO-class)")
print(f"   Adler (1e-8 /s): N* = {edge(lam_adler):.1e} amu   (at current experiments)")

# ---------- figure ----------
fig, ax = plt.subplots(2, 2, figsize=(13, 8.6))

off = 0.0
cols = {100: "tab:green", 700: "tab:orange", 2500: "tab:red"}
for Nn in (100, 700, 2500):
    p, P = dists[Nn]
    sel = np.abs(p) < 0.55
    ax[0, 0].plot(p[sel], P[sel]/P[sel].max() + off, color=cols[Nn], lw=1.8,
                  label=f"N = {Nn}")
    off += 1.15
ax[0, 0].set_title("Interference read-out vs object size\n(ensemble momentum fringes; NOBODY is measuring)")
ax[0, 0].set_xlabel("momentum p"); ax[0, 0].set_yticks([])
ax[0, 0].legend(fontsize=9)

ax[0, 1].semilogx(Ns, Vrel, "o", ms=8, color="tab:blue", label="simulation")
NN = np.logspace(np.log10(Ns[0]), np.log10(Ns[-1]), 200)
ax[0, 1].semilogx(NN, np.exp(-kappa0*(NN**2 - float(Ns[0])**2)*d**2*T), "k--",
                  lw=1.4, label=r"analytic  $e^{-\kappa_0 N^2 d^2 T}$")
ax[0, 1].set_title("Fringe visibility vs size: the collapse edge\n(mass amplification $k=\\kappa_0 N^2$)")
ax[0, 1].set_xlabel("N (constituents)"); ax[0, 1].set_ylabel("visibility")
ax[0, 1].legend(fontsize=9)

for j in range(40):
    c = "tab:red" if Pr_big[-1, j] > 0.5 else "tab:blue"
    ax[1, 0].plot(np.arange(Pr_big.shape[0])*dt, Pr_big[:, j], color=c, alpha=0.35, lw=0.9)
ax[1, 0].set_title(f"Heavy object (N={Ns[-1]}): each run localizes SPONTANEOUSLY\n(no detector anywhere -- the model's noise does it)")
ax[1, 0].set_xlabel("time"); ax[1, 0].set_ylabel(r"$P_{right}(t)$")

ax[1, 1].semilogx(m, V_grw, color="tab:green", lw=2, label=r"GRW  $\lambda=10^{-16}$/s (alive)")
ax[1, 1].semilogx(m, V_adl, color="tab:red", lw=2, label=r"Adler  $\lambda=10^{-8}$/s (being excluded)")
marks = [(840, "C70\n(1999)"), (2.5e4, "Fein 2019\n25 kamu"), (1e8, "levitated\nnano (goal)"), (1e10, "MAQRO\n(proposed)")]
for mm, lab in marks:
    ax[1, 1].axvline(mm, color="gray", ls=":", lw=1)
    ax[1, 1].text(mm*1.15, 0.55, lab, fontsize=7.5, color="dimgray")
ax[1, 1].set_title("Real units: the same edge, calibrated (flight T = 10 ms)\nfringes seen at a mass => that collapse rate is excluded")
ax[1, 1].set_xlabel("object mass (amu ~ nucleon count)"); ax[1, 1].set_ylabel("predicted visibility")
ax[1, 1].set_ylim(-0.05, 1.1); ax[1, 1].legend(fontsize=9, loc="center left")

fig.suptitle("Objective collapse (CSL-type) toy: superpositions die with SIZE, no observer required",
             fontsize=13.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("csl_toy.png", dpi=125)
print("\nsaved -> qsim/csl_toy.png")
