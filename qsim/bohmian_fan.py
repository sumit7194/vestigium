"""
Experiment 3 — the pilot-wave (Bohmian) trajectories of our double slit.

The guiding wave: two freely spreading Gaussian slit-packets (exact analytic
solution of the Schrodinger equation, hbar = m = 1):

    psi(y,t) = G(y - d/2, t) + G(y + d/2, t),
    G(u,t)   = s_t^{-1/2} exp(-u^2 / (4 sigma0 s_t)),   s_t = sigma0 (1 + i t / (2 sigma0^2))

Each particle has a definite position at all times and simply rides the wave:

    dy/dt = v(y,t) = Im( d_y psi / psi )        (the guidance equation)

This is the calculation of Philippidis, Dewdney & Hiley (1979); the same velocity
field is what Kocsis et al. (Science 2011) reconstructed from weak measurements.

Verifications:
  1) EQUIVARIANCE: start 20,000 particles Born-distributed (|psi|^2 at t=0),
     integrate the guidance equation only -- their histogram at the screen must
     reproduce |psi(y,T)|^2 including all fringes.  (This is WHY pilot wave is
     empirically identical to standard QM.)
  2) NO CROSSING: trajectories never cross the symmetry axis (count = 0), the
     famous Bohmian signature -- a particle landing in the upper half CAME from
     the upper slit, definite path and all.

Honesty notes: an interpretation, not new predictions; for photons the analog
is energy-flow lines (Kocsis), massive-particle version shown here.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sigma0, d, T, dt = 1.0, 10.0, 30.0, 0.01
rng = np.random.default_rng(3)

def s_t(t):
    return sigma0 * (1 + 1j * t / (2 * sigma0**2))

def psi_and_dpsi(y, t):
    st = s_t(t)
    out_p, out_d = 0.0, 0.0
    for c in (+d/2, -d/2):
        u = y - c
        g = np.exp(-u**2 / (4 * sigma0 * st)) / np.sqrt(st)
        out_p = out_p + g
        out_d = out_d + g * (-u / (2 * sigma0 * st))
    return out_p, out_d

def vfield(y, t):
    p, dp = psi_and_dpsi(y, t)
    return np.imag(dp / p)

def rk4(y, t, dt):
    k1 = vfield(y, t)
    k2 = vfield(y + 0.5*dt*k1, t + 0.5*dt)
    k3 = vfield(y + 0.5*dt*k2, t + 0.5*dt)
    k4 = vfield(y + dt*k3, t + dt)
    return y + dt*(k1 + 2*k2 + 2*k3 + k4)/6

# ---------- Born-distributed initial ensemble ----------
ygrid = np.linspace(-12, 12, 4001)
p0, _ = psi_and_dpsi(ygrid, 0.0)
w = np.abs(p0)**2; w /= w.sum()
cdf = np.cumsum(w)
Nens = 20000
y_ens = np.interp(rng.random(Nens), cdf, ygrid)
sign0 = np.sign(y_ens)

# fan subset: quantile-spaced for even visual coverage
qs = np.interp(np.linspace(0.004, 0.996, 140), cdf, ygrid)

steps = int(T/dt)
t_axis = np.linspace(0, T, steps+1)
fan = np.zeros((steps+1, qs.size)); fan[0] = qs
ens = y_ens.copy()
for i in range(steps):
    t = i*dt
    fan[i+1] = rk4(fan[i], t, dt)
    ens = rk4(ens, t, dt)

# ---------- verifications ----------
crossings = int(np.sum(np.sign(ens) != sign0))
print(f"NO-CROSSING CHECK: {crossings} of {Nens} trajectories crossed the axis (expected 0)")

yg2 = np.linspace(-45, 45, 121)
hist, edges = np.histogram(ens, bins=yg2, density=True)
centers = 0.5*(edges[1:] + edges[:-1])
pT, _ = psi_and_dpsi(centers, T)
born = np.abs(pT)**2
born /= np.trapezoid(born, centers)
mask = born > 0.003
dev = np.max(np.abs(hist[mask] - born[mask])) / born.max()
print(f"EQUIVARIANCE: max |trajectory histogram - |psi|^2| = {dev:.1%} of peak "
      f"(20k particles, guidance equation only)")

# ---------- background heatmap ----------
yh = np.linspace(-40, 40, 500)
H = np.zeros((yh.size, t_axis[::10].size))
for j, t in enumerate(t_axis[::10]):
    p, _ = psi_and_dpsi(yh, max(t, 1e-9))
    col = np.abs(p)**2
    H[:, j] = col / col.max()

# ---------- figure ----------
fig = plt.figure(figsize=(13, 6.4))
gs = fig.add_gridspec(2, 3, width_ratios=[2.2, 1, 0.02])
axF = fig.add_subplot(gs[:, 0])
axH = fig.add_subplot(gs[0, 1])
axZ = fig.add_subplot(gs[1, 1])

axF.imshow(H, extent=[0, T, yh[0], yh[-1]], origin="lower", aspect="auto",
           cmap="Greys", alpha=0.75)
up = fan[0] > 0
axF.plot(t_axis, fan[:, up], color="tab:orange", lw=0.7, alpha=0.85)
axF.plot(t_axis, fan[:, ~up], color="tab:blue", lw=0.7, alpha=0.85)
axF.set_xlabel("time  (= distance to screen)")
axF.set_ylabel("transverse position y")
axF.set_title("The pilot-wave fan: definite paths, one slit each, bunching into the fringes\n"
              "(orange = upper slit, blue = lower slit -- and they never cross the axis)")
axF.set_ylim(-40, 40)

axH.plot(born[mask]/born.max(), centers[mask], "k-", lw=1.6, label=r"$|\psi|^2$ at screen")
axH.barh(centers, hist/born.max(), height=(centers[1]-centers[0])*0.95,
         color="tab:green", alpha=0.55, label="20k Bohmian endpoints")
axH.set_ylim(-40, 40); axH.set_xlabel("probability (norm.)")
axH.set_title("Equivariance: trajectories\nrebuild the Born fringes", fontsize=10)
axH.legend(fontsize=7.5, loc="lower right")

sel = np.abs(fan[0]) < 6.5
axZ.plot(t_axis[:800], fan[:800, sel], color="tab:purple", lw=0.8)
axZ.set_xlabel("time (early)"); axZ.set_ylabel("y")
axZ.set_title("Early times: paths repelled from\nthe forming dark fringes", fontsize=10)

fig.suptitle("Pilot-wave view of the double slit -- computed from the guidance equation "
             "(Philippidis 1979 / Kocsis 2011)", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("bohmian_fan.png", dpi=125)
print("saved -> qsim/bohmian_fan.png")
