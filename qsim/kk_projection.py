"""
Plan A — the Kaluza-Klein projection demo.

A MASSLESS wave lives on a cylinder: one visible dimension x, one hidden tiny loop y
(circumference L = 2*pi*R).  The full 2D field obeys the plain massless wave equation

    d2 phi/dt2 = c^2 (d2/dx2 + d2/dy2) phi ,   c = 1.

Because y is a loop, the y-dependence is quantized: phi ~ e^{i n y / R}, n = winding.
Plug that in and the visible (x) projection obeys

    d2 phi/dt2 = d2 phi/dx2 - (n/R)^2 phi      <-- the Klein-Gordon equation
                                                    of a particle with MASS m_n = n/R.

So: same 2D massless wave; different winding around the hidden loop; the projection
sees a tower of particles of different masses.  "Mass = motion in the hidden dimension."

We verify numerically, from the simulation alone (no formula injected):
  1) REST BUZZ: an n>=1 packet with zero visible momentum oscillates at frequency m_n.
     Measure the oscillation frequency for n=1,2,3 -> should scale 1:2:3.
  2) SLOWER TRAVEL: give each packet the same visible momentum k; massless n=0 moves
     at c, massive n>=1 move at the Klein-Gordon group velocity v = k/sqrt(k^2+m^2).
  3) Panels of the projection |phi(x)|: n=0 stays sharp and races; n>=1 lags & buzzes.

Leapfrog integration of the 2D wave equation; y handled spectrally (exact, since the
loop dependence stays a single Fourier mode: phi(x,y,t) = f(x,t) e^{i n y/R}, and f
obeys f_tt = f_xx - (n/R)^2 f -- we evolve THAT 1D equation, which IS the projection).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- setup ----------------
c = 1.0
R = 1.0                      # hidden loop radius  -> m_n = n/R = n
Nx, Lx = 4096, 400.0
x = np.linspace(-Lx/2, Lx/2, Nx, endpoint=False)
dx = x[1] - x[0]
dt = 0.4 * dx                # CFL-safe
k_kick = 1.0                 # visible momentum given in the travel test
sigma = 6.0                  # packet width

def evolve(n_wind, k0, T):
    """Evolve f_tt = f_xx - m^2 f (m = n_wind/R) from a Gaussian packet; leapfrog."""
    m = n_wind / R
    f = np.exp(-x**2/(2*sigma**2)) * np.exp(1j*k0*x)
    # exact first-step velocity for a packet built from +omega modes:
    #   f_t = -i*omega(k) f  applied in k-space
    kgrid = 2*np.pi*np.fft.fftfreq(Nx, dx)
    omega = np.sqrt(kgrid**2 + m**2)
    ft = np.fft.ifft(-1j*omega*np.fft.fft(f))
    fprev = f - dt*ft                                   # backward Euler seed
    steps = int(T/dt)
    lap_fac = (dt/dx)**2
    probe = []                                          # field at a probe point
    ip = Nx//2
    for s in range(steps):
        lap = np.roll(f, 1) + np.roll(f, -1) - 2*f
        fnew = 2*f - fprev + lap_fac*lap - (dt*m)**2 * f
        fprev, f = f, fnew
        probe.append(f[ip])
    return f, np.array(probe)

# ---------------- 1) rest buzz: frequency vs winding ----------------
T_buzz = 300.0
freqs = []
for n in (1, 2, 3):
    _, probe = evolve(n, k0=0.0, T=T_buzz)
    sig = (probe - probe.mean()).real * np.hanning(len(probe))
    sp = np.abs(np.fft.rfft(sig))
    fr = np.fft.rfftfreq(len(sig), dt) * 2*np.pi        # angular frequency
    i = np.argmax(sp)
    # parabolic interpolation around the peak for sub-bin frequency accuracy
    if 0 < i < len(sp)-1:
        d = 0.5*(sp[i-1]-sp[i+1])/(sp[i-1]-2*sp[i]+sp[i+1])
        freqs.append(fr[i] + d*(fr[1]-fr[0]))
    else:
        freqs.append(fr[i])
f1, f2, f3 = freqs
print("1) REST BUZZ (packet at rest, hidden winding n):")
print(f"   measured omega  n=1: {f1:.4f}   n=2: {f2:.4f}   n=3: {f3:.4f}")
print(f"   ratios: {f1/f1:.3f} : {f2/f1:.3f} : {f3/f1:.3f}   (exact KK: 1 : 2 : 3)")
print(f"   absolute vs m_n = n/R: errors "
      f"{abs(f1-1):.3%}, {abs(f2-2)/2:.3%}, {abs(f3-3)/3:.3%}")

# ---------------- 2) travel race: group velocity vs winding ----------------
T_race = 120.0
centers, snaps = [], {}
for n in (0, 1, 2):
    f, _ = evolve(n, k0=k_kick, T=T_race)
    P = np.abs(f)**2
    xc = np.sum(x*P)/np.sum(P)
    centers.append(xc)
    snaps[n] = P
v_meas = [xc/T_race for xc in centers]
v_exact = [k_kick/np.sqrt(k_kick**2 + (n/R)**2) for n in (0, 1, 2)]
print("\n2) TRAVEL RACE (same visible kick k=1 for everyone):")
for n, vm, ve in zip((0, 1, 2), v_meas, v_exact):
    print(f"   n={n}:  v_measured = {vm:.4f}   v_KG_exact = {ve:.4f}"
          f"   (err {abs(vm-ve)/ve:.2%})")
print("   n=0 races at c; higher winding = heavier = slower. Same 2D wave each time.")

# ---------------- figure ----------------
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))

# cylinder cartoon
th = np.linspace(0, 2*np.pi, 60)
for xx in np.linspace(0.5, 9.5, 12):
    ax[0].plot(xx + 0.35*np.sin(th), 1.2*np.cos(th)*0.5, color="lightgray", lw=1)
ax[0].annotate("visible dimension x", (5, -1.35), ha="center")
ax[0].annotate("hidden loop y\n(circumference 2πR)", (0.6, 0.95), fontsize=9)
for i, (nn, col) in enumerate(zip((0, 1, 2), ("tab:green", "tab:orange", "tab:red"))):
    yy = 0.42 - 0.42*i
    ax[0].plot(np.linspace(1.5, 8.5, 200),
               yy + 0.12*np.sin(nn*np.linspace(0, 14*np.pi, 200)),
               color=col, lw=1.6)
    ax[0].annotate(f"winding n={nn}", (8.7, yy-0.03), color=col, fontsize=9)
ax[0].set_xlim(0, 10.8); ax[0].set_ylim(-1.6, 1.6); ax[0].axis("off")
ax[0].set_title("One massless wave on a cylinder;\nonly the winding differs")

# rest buzz spectrum ratios
ax[1].bar(["n=1", "n=2", "n=3"], [f1, f2, f3],
          color=["tab:orange", "tab:red", "tab:purple"], width=0.55)
ax[1].plot([-0.4, 2.4], [1, 1], "k:", lw=1); ax[1].plot([-0.4, 2.4], [2, 2], "k:", lw=1)
ax[1].plot([-0.4, 2.4], [3, 3], "k:", lw=1)
ax[1].set_ylabel("rest-buzz frequency  $\\omega$")
ax[1].set_title("Packet at rest 'buzzes' at $m_n = n/R$\n(dotted = exact KK tower)")

# race snapshots
for n, col in zip((0, 1, 2), ("tab:green", "tab:orange", "tab:red")):
    P = snaps[n]/snaps[n].max()
    ax[2].plot(x, P + n*1.1, color=col, lw=1.4,
               label=f"n={n}  (v={v_meas[n]:.2f})")
    ax[2].axvline(v_exact[n]*T_race, color=col, ls=":", lw=1)
ax[2].set_xlim(-30, 130); ax[2].set_yticks([])
ax[2].set_xlabel("visible position x  (after same kick, same time)")
ax[2].set_title("The projection: heavier winding lags\n(dotted = exact massive-particle prediction)")
ax[2].legend(fontsize=9, loc="upper left")

fig.suptitle("Mass from a hidden dimension: winding around the loop → apparent mass in the projection",
             fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("kk_projection.png", dpi=125)
print("\nsaved -> qsim/kk_projection.png")
