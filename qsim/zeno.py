"""
Experiment 6 — the quantum Zeno effect: a watched pot never boils.

A qubit Rabi-flips |0> -> |1> under H = (Omega/2) sigma_x.  Left alone for
T = pi/Omega it flips with certainty.  WATCH it, and the flip is suppressed:

(a) PROJECTIVE watching: N equally spaced measurements. P(every look finds |0>)
    = [cos^2(pi/2N)]^N -> 1 as N grows.  This is exactly what Itano, Heinzen,
    Bollinger & Wineland did with trapped Be+ ions (PRA 41, 2295 (1990)) --
    their data followed this cos^2N law.

(b) CONTINUOUS watching: the same SSE as weak_measurement.py, monitoring
    sigma_z with strength k.  Weak k: noisy Rabi cycles survive.  Strong k:
    TELEGRAPH dynamics -- the qubit sits frozen in an eigenstate and makes rare
    incoherent jumps, at a rate suppressed like 1/k (Zeno scaling: watching
    harder makes transitions RARER).  We fit the measured flip rate vs k.

The punchline for the measurement-strength dial built in experiments 1 & 4:
  k -> 0   : unitary quantum motion (Rabi)
  k medium : stochastic collapse dynamics
  k -> inf : motion FROZEN (Zeno) -- observation as a brake.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(21)
Omega = 1.0

# ---------------- (a) projective Zeno ----------------
def projective_survival(N, M=20000):
    """Monte Carlo: M runs, N equally spaced projective looks over T = pi/Omega."""
    tau = np.pi / Omega / N
    c, s = np.cos(Omega*tau/2), np.sin(Omega*tau/2)
    alive = np.ones(M, bool)          # trajectories where every look said |0>
    # after each projection the state is exactly |0> (if alive); before the next
    # look, amplitude to remain is cos(Omega tau/2) -> survive w.p. cos^2
    for _ in range(N):
        alive &= (rng.random(M) < c*c)
    return alive.mean()

Ns = np.array([1, 2, 4, 8, 16, 32, 64])
mc = np.array([projective_survival(n) for n in Ns])
th = np.cos(np.pi/(2*Ns))**(2*Ns)
print("(a) PROJECTIVE ZENO -- survival of |0> over a full would-be flip (T = pi):")
for n, m_, t_ in zip(Ns, mc, th):
    print(f"    N={n:3d} looks:  MC {m_:.4f}   analytic [cos^2(pi/2N)]^N = {t_:.4f}")
print(f"    max |MC - analytic| = {np.max(np.abs(mc-th)):.4f}   (unwatched: survival = 0)")

# ---------------- (b) continuous Zeno ----------------
def sse_qubit(k, T, dt, M, keep_traj=0):
    """Monitor sigma_z with strength k while H drives Rabi flips."""
    ang = Omega*dt/2
    U = np.array([[np.cos(ang), -1j*np.sin(ang)], [-1j*np.sin(ang), np.cos(ang)]])
    psi = np.zeros((M, 2), complex); psi[:, 0] = 1.0
    z = np.array([1.0, -1.0])
    steps = int(round(T/dt))
    trajs = [] if keep_traj else None
    state = np.ones(M)                 # telegraph state via hysteresis
    flips = np.zeros(M)
    for i in range(steps):
        psi = psi @ U.T
        m = (np.abs(psi)**2 @ z)
        dW = rng.normal(0, np.sqrt(dt), (M, 1))
        psi *= np.exp(-2*k*(z[None, :]-m[:, None])**2*dt
                      + np.sqrt(2*k)*(z[None, :]-m[:, None])*dW)
        psi /= np.linalg.norm(psi, axis=1, keepdims=True)
        m = (np.abs(psi)**2 @ z)
        flipped = (state > 0) & (m < -0.8) | (state < 0) & (m > 0.8)
        flips += flipped
        state = np.where(flipped, -state, state)
        if keep_traj and i % 20 == 0:
            trajs.append(m[:keep_traj].copy())
    rate = flips.mean() / T
    return rate, (np.array(trajs) if keep_traj else None)

print("\n(b) CONTINUOUS ZENO -- flip rate vs watching strength k:")
ks = np.array([2.0, 5.0, 10.0, 20.0])
rates = []
for k in ks:
    dt = min(2e-3, 0.05/(8*k))
    r, _ = sse_qubit(k, T=400.0, dt=dt, M=100)
    rates.append(r)
    print(f"    k={k:5.1f}:  measured flip rate = {r:.5f}   (Omega^2/8k = {Omega**2/(8*k):.5f})")
rates = np.array(rates)
slope = np.polyfit(np.log(ks), np.log(rates), 1)[0]
print(f"    fitted scaling: rate ~ k^({slope:.2f})   (Zeno prediction: k^-1)")
print(f"    prefactor ratio measured/(Omega^2/8k): "
      f"{np.mean(rates/(Omega**2/(8*ks))):.2f}")

# sample trajectories for the picture
_, tr_weak = sse_qubit(0.05, T=60.0, dt=2e-3, M=3, keep_traj=3)
_, tr_strong = sse_qubit(10.0, T=60.0, dt=6.25e-4, M=3, keep_traj=3)

# ---------------- figure ----------------
fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))

NN = np.linspace(1, 70, 300)
ax[0].plot(NN, np.cos(np.pi/(2*NN))**(2*NN), "k--", lw=1.2,
           label=r"analytic $[\cos^2(\pi/2N)]^N$")
ax[0].plot(Ns, mc, "o", ms=8, color="tab:orange", label="Monte Carlo (20k runs)")
ax[0].axhline(0, color="gray", lw=0.6)
ax[0].set_xscale("log", base=2)
ax[0].set_xlabel("number of looks N during the flip")
ax[0].set_ylabel("P(still found in |0⟩ every time)")
ax[0].set_title("Projective Zeno: more looks → frozen\n(Itano et al. 1990, trapped ions)")
ax[0].legend(fontsize=9)

t_w = np.arange(tr_weak.shape[0])*20*2e-3
t_s = np.arange(tr_strong.shape[0])*20*6.25e-4
ax[1].plot(t_w, tr_weak[:, 0], color="tab:blue", lw=1.0,
           label="barely watched (k=0.05): Rabi cycles")
ax[1].plot(t_s, tr_strong[:, 0] + 2.4, color="tab:red", lw=1.0,
           label="watched hard (k=10): telegraph")
ax[1].set_yticks([]); ax[1].set_xlabel("time")
ax[1].set_title("Same qubit, two watching strengths\n(top: frozen + rare jumps; bottom: free oscillation)")
ax[1].legend(fontsize=8.5, loc="center right")

ax[2].loglog(ks, rates, "o", ms=9, color="tab:purple", label="measured flip rate")
ax[2].loglog(ks, Omega**2/(8*ks), "k--", lw=1.2, label=r"$\Omega^2/8k$ (Zeno scaling)")
ax[2].set_xlabel("watching strength k")
ax[2].set_ylabel("flips per unit time")
ax[2].set_title(f"Watching harder → flipping slower\n(fitted power: $k^{{{slope:.2f}}}$, prediction $k^{{-1}}$)")
ax[2].legend(fontsize=9)

fig.suptitle("Quantum Zeno: observation as a brake — the endpoint of the measurement-strength dial",
             fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("zeno.png", dpi=125)
print("\nsaved -> qsim/zeno.png")
