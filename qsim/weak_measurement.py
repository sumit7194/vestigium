"""
Experiment 1 — watch collapse happen gradually (continuous weak measurement).

We simulate the standard quantum-trajectory / stochastic Schrodinger equation (SSE)
for continuous position monitoring with strength k  (hbar = m = 1):

    d|psi> = [ -iH dt  -  k (x - <x>)^2 dt  +  sqrt(2k) (x - <x>) dW ] |psi>

H = p^2/2 (free particle).  dW = Gaussian noise, one draw per trajectory per step.
This is textbook physics (Jacobs & Steck 2006); each trajectory = one experimental
run with its own measurement record.

Three verifications, computed from the simulation alone:
  A) BORN RULE EMERGES: a two-hump cat  sqrt(0.7)|left> + sqrt(0.3)|right>
     commits gradually & randomly to one hump; the fraction of trajectories per
     hump must approach 70/30 -- not postulated, produced by the dynamics.
  B) CONDITIONAL STEADY STATE: for a monitored Gaussian the conditional variance
     must relax onto the deterministic Riccati solution and saturate at
     V_ss = 1/sqrt(8k).
  C) COLLAPSE vs DECOHERENCE: each single trajectory localizes (V saturates),
     while the ENSEMBLE ignoring the records spreads as the Lindblad prediction
     V_ens(t) = V0 + Vp0 t^2 + (2/3) k t^3.  Same physics, two viewpoints.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)

def run_sse(psi0, x, k, T, dt, M, snap_times=()):
    """Batch-evolve M trajectories from psi0 under free H + position monitoring."""
    N = x.size; dx = x[1] - x[0]
    kgrid = 2*np.pi*np.fft.fftfreq(N, dx)
    kin = np.exp(-0.5j * kgrid**2 * dt)
    psi = np.tile(psi0, (M, 1)).astype(np.complex128)
    steps = int(round(T/dt))
    snap_steps = {int(round(t/dt)): t for t in snap_times}
    ts, xm_t, V_t, Pr_t, snaps = [], [], [], [], {}
    for s in range(steps + 1):
        P = np.abs(psi)**2 * dx
        Ptot = P.sum(1, keepdims=True)
        P /= Ptot
        xm = (x[None, :]*P).sum(1, keepdims=True)
        V = ((x[None, :]-xm)**2 * P).sum(1)
        if s in snap_steps:
            snaps[snap_steps[s]] = (np.abs(psi)**2 / Ptot).copy()
        ts.append(s*dt); xm_t.append(xm[:, 0].copy()); V_t.append(V.copy())
        Pr_t.append(P[:, x > 0].sum(1))
        if s == steps:
            break
        psi = np.fft.ifft(np.fft.fft(psi, axis=1)*kin, axis=1)          # kinetic
        dW = rng.normal(0.0, np.sqrt(dt), (M, 1))
        # exponential (Kraus-like) update with the Ito correction included:
        # exp[-2k(x-xm)^2 dt + sqrt(2k)(x-xm) dW] expands (dW^2=dt) to the target
        # SSE increment  -k(x-xm)^2 dt + sqrt(2k)(x-xm) dW .
        psi *= np.exp(-2*k*(x[None, :]-xm)**2*dt + np.sqrt(2*k)*(x[None, :]-xm)*dW)
        psi /= np.sqrt((np.abs(psi)**2).sum(1, keepdims=True)*dx)       # renorm
    return (np.array(ts), np.array(xm_t), np.array(V_t), np.array(Pr_t), snaps)

def riccati(V0, C0, Vp0, k, T, dt=1e-3):
    """Deterministic conditional-covariance evolution (Gaussian/Kalman)."""
    V, C, Vp = V0, C0, Vp0
    ts, Vs = [0.0], [V0]
    n = int(T/dt)
    for i in range(n):
        dV = 2*C - 8*k*V*V
        dC = Vp - 8*k*V*C
        dVp = 2*k - 8*k*C*C
        V += dV*dt; C += dC*dt; Vp += dVp*dt
        if (i+1) % 50 == 0:
            ts.append((i+1)*dt); Vs.append(V)
    return np.array(ts), np.array(Vs)

# ================= A) cat commitment + Born rule =================
N, L = 1024, 80.0
x = np.linspace(-L/2, L/2, N, endpoint=False)
sig, d = 2.0, 8.0
gL = np.exp(-(x+d)**2/(4*sig**2)); gR = np.exp(-(x-d)**2/(4*sig**2))
gL /= np.sqrt((gL**2).sum()*(x[1]-x[0])); gR /= np.sqrt((gR**2).sum()*(x[1]-x[0]))
cat = np.sqrt(0.7)*gL + np.sqrt(0.3)*gR
cat /= np.sqrt((np.abs(cat)**2).sum()*(x[1]-x[0]))

kA, TA, dtA, MA = 0.003, 12.0, 0.005, 400
snapT = (0.0, 1.0, 2.5, 5.0, 12.0)
tsA, xmA, VA, PrA, snapsA = run_sse(cat, x, kA, TA, dtA, MA, snap_times=snapT)

final = PrA[-1]
right = np.sum(final > 0.9); left = np.sum(final < 0.1)
undec = MA - right - left
frac_r = right / max(1, right + left)
se = np.sqrt(0.3*0.7/max(1, right+left))
print(f"A) BORN RULE FROM DYNAMICS (cat = 70/30 left/right, k={kA}):")
print(f"   decided: {right+left}/{MA} (undecided {undec})")
print(f"   fraction committed RIGHT = {frac_r:.3f}   (Born prediction 0.300, "
      f"stat. err ~{se:.3f})")

# ================= B) conditional variance vs Riccati =================
N2, L2 = 2048, 160.0
x2 = np.linspace(-L2/2, L2/2, N2, endpoint=False)
V0 = 16.0
g0 = np.exp(-x2**2/(4*V0)); g0 /= np.sqrt((g0**2).sum()*(x2[1]-x2[0]))
ks = (0.0125, 0.05, 0.2)
TB, dtB, MB = 20.0, 0.005, 100
resB = {}
print("\nB) CONDITIONAL VARIANCE -> analytic steady state V_ss = 1/sqrt(8k):")
for kk in ks:
    tsB, xmB, VB, _, _ = run_sse(g0, x2, kk, TB, dtB, MB)
    late = VB[int(0.7*len(tsB)):].mean()
    print(f"   k={kk:<7}: late-time V = {late:7.3f}   exact 1/sqrt(8k) = "
          f"{1/np.sqrt(8*kk):7.3f}   (err {abs(late-1/np.sqrt(8*kk))/(1/np.sqrt(8*kk)):.1%})")
    resB[kk] = (tsB, xmB, VB)

# ================= C) collapse (conditional) vs decoherence (ensemble) ==========
kk = 0.05
tsB, xmB, VB = resB[kk]
V_cond = VB.mean(1)                                  # per-trajectory (conditional)
V_ens = VB.mean(1) + xmB.var(1)                      # pooled ensemble variance
Vp0 = 1/(4*V0)
V_lind = V0 + Vp0*tsB**2 + (2/3)*kk*tsB**3           # Lindblad (no-record) prediction
errC = abs(V_ens[-1]-V_lind[-1])/V_lind[-1]
print(f"\nC) COLLAPSE vs DECOHERENCE (k={kk}):")
print(f"   conditional V at T: {V_cond[-1]:.2f} (saturated near {1/np.sqrt(8*kk):.2f})")
print(f"   ensemble    V at T: {V_ens[-1]:.1f} vs Lindblad prediction {V_lind[-1]:.1f} "
      f"(err {errC:.1%})")

# ================= figure =================
fig, ax = plt.subplots(2, 2, figsize=(13, 8.6))

# (1) one trajectory committing (pick one that ends RIGHT, the 30% hump)
i_r = int(np.argmax(final > 0.9))
off = 0.0
for t in snapT:
    p = snapsA[t][i_r]
    ax[0, 0].fill_between(x, off, off + p/p.max()*0.9, alpha=0.75,
                          color=plt.cm.viridis(t/TA))
    ax[0, 0].text(-38, off+0.28, f"t={t:g}", fontsize=9)
    off += 1.0
ax[0, 0].set_title("One monitored run: the cat commits GRADUALLY\n(this one happened to pick the 30% hump)")
ax[0, 0].set_xlabel("x"); ax[0, 0].set_yticks([]); ax[0, 0].set_xlim(-40, 40)

# (2) P_right(t) spaghetti
for j in range(60):
    c = "tab:red" if final[j] > 0.5 else "tab:blue"
    ax[0, 1].plot(tsA, PrA[:, j], color=c, alpha=0.35, lw=0.9)
ax[0, 1].axhline(0.3, ls=":", color="k", lw=1)
ax[0, 1].text(6.6, 0.315, "initial weight 0.30", fontsize=8)
ax[0, 1].set_title(f"60 runs: weight on the right hump vs time\ncommitted right: {frac_r:.1%}  (Born: 30%)")
ax[0, 1].set_xlabel("time"); ax[0, 1].set_ylabel(r"$P_{right}(t)$")

# (3) conditional variance vs Riccati for three k
cols = {0.0125: "tab:green", 0.05: "tab:orange", 0.2: "tab:red"}
for kk2 in ks:
    tsb, _, Vb = resB[kk2]
    ax[1, 0].plot(tsb, Vb.mean(1), color=cols[kk2], lw=2, label=f"sim  k={kk2}")
    tr, Vr = riccati(V0, 0.0, 1/(4*V0), kk2, TB)
    ax[1, 0].plot(tr, Vr, "k--", lw=1)
    ax[1, 0].axhline(1/np.sqrt(8*kk2), color=cols[kk2], ls=":", lw=1)
ax[1, 0].set_yscale("log")
ax[1, 0].set_title("Conditional width collapses onto the exact (Riccati) curve\ndotted: steady state $1/\\sqrt{8k}$   dashed: theory")
ax[1, 0].set_xlabel("time"); ax[1, 0].set_ylabel("position variance V(t)")
ax[1, 0].legend(fontsize=9)

# (4) collapse vs decoherence
ax[1, 1].plot(tsB, V_cond, color="tab:orange", lw=2, label="conditional (one observer, k=0.05)")
ax[1, 1].plot(tsB, V_ens, color="tab:purple", lw=2, label="ensemble (records ignored)")
ax[1, 1].plot(tsB, V_lind, "k--", lw=1.2, label="Lindblad prediction (decoherence)")
ax[1, 1].set_title("Same runs, two viewpoints:\neach run COLLAPSES -- the average DECOHERES & spreads")
ax[1, 1].set_xlabel("time"); ax[1, 1].set_ylabel("position variance")
ax[1, 1].legend(fontsize=9)

fig.suptitle("Collapse as a gradual process: continuous weak measurement (stochastic Schrodinger equation)",
             fontsize=13.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("weak_measurement.png", dpi=125)
print("\nsaved -> qsim/weak_measurement.png")
