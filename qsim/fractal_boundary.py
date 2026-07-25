"""
Plan B — does the detector boundary's structure reshape where detections land?

2D Schrodinger (Visscher leapfrog, hbar=m=1). A wavepacket passes a double slit;
the interference pattern then hits a DETECTOR WALL whose absorbing surface has
one of three structures along y:

  uniform  : every cell absorbs
  periodic : evenly spaced absorbing segments (control for "structured but regular")
  cantor   : Cantor-set fractal segments (level 3)

periodic and cantor have the SAME total absorbing fraction (8 segments, 8/27 of the
height) so any difference is geometry, not coverage.  Clicks = probability actually
removed by each wall row, accumulated over the whole run.  Non-absorbing gaps are
dead zones: the wave passes and is eaten silently by the border sponge (not counted).

Honest questions scored at the end:
  1) GATING: do the three walls yield different click distributions?  (expected: yes)
  2) FRINGE INTEGRITY: within the cells that DO absorb, do click peaks sit at the
     same y as the incident interference pattern (no fringe shift)?  We compare the
     detected pattern to incident(y) x mask(y).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- grid & scheme ----------------
Nx, Ny = 480, 324
dx, dt = 1.0, 0.2
steps = 9000
k0 = 1.0                      # packet momentum -> lambda = 2*pi
x = np.arange(Nx)[:, None]
y = np.arange(Ny)[None, :]

# geometry
slit_x = 150                  # barrier column
det_x = 430                   # detector wall column (strip det_x..det_x+3)
sep, sw = 40, 10              # slit separation (center-to-center), slit width
cy = Ny // 2

# border sponge (kills anything reaching edges; not counted as detection)
border = 18
bd = np.minimum(np.minimum(x, Nx - 1 - x), np.minimum(y, Ny - 1 - y))
sponge = np.where(bd >= border, 1.0, 1.0 - 0.35 * ((border - bd) / border) ** 2)

# slit barrier: absorbing wall with two openings (graded, low reflection)
slit_damp = np.ones((Nx, Ny))
wall_cols = slice(slit_x, slit_x + 8)
open1 = np.abs(y - (cy - sep // 2)) <= sw // 2
open2 = np.abs(y - (cy + sep // 2)) <= sw // 2
blocked = ~(open1 | open2)
for i, col in enumerate(range(slit_x, slit_x + 8)):
    a = 0.55 * np.sin(np.pi * (i + 0.5) / 8)
    slit_damp[col, :] = np.where(blocked[0], 1.0 - a, 1.0)

def masks():
    """absorbing masks along y for the detector wall (True = absorbing cell)"""
    m_uni = np.ones(Ny, bool)
    # cantor level 3 on the full height: keep 8 segments of length Ny/27
    seg = [(0.0, 1.0)]
    for _ in range(3):
        seg = [s for a, b in seg for s in ((a, a + (b - a) / 3), (b - (b - a) / 3, b))]
    m_can = np.zeros(Ny, bool)
    for a, b in seg:
        m_can[int(a * Ny):max(int(a * Ny) + 1, int(b * Ny))] = True
    frac = m_can.mean()                       # ~8/27
    # periodic: 8 evenly spaced segments, same total coverage
    m_per = np.zeros(Ny, bool)
    nseg, w = 8, max(1, int(round(frac * Ny / 8)))
    for i in range(nseg):
        c = int((i + 0.5) * Ny / nseg)
        m_per[c - w // 2:c - w // 2 + w] = True
    return {"uniform": m_uni, "periodic": m_per, "cantor": m_can}

def run(mask):
    """evolve; return clicks(y) at the detector and incident pattern just before it"""
    rng_norm = None
    sx, sy = 28.0, 70.0
    env = np.exp(-((x - 70) ** 2) / (2 * sx ** 2) - ((y - cy) ** 2) / (2 * sy ** 2))
    R = env * np.cos(k0 * (x - 70.0)); I = env * np.sin(k0 * (x - 70.0))
    nrm = np.sqrt(np.sum(R ** 2 + I ** 2)); R /= nrm; I /= nrm

    det_damp = np.ones((Nx, Ny))
    for i, col in enumerate(range(det_x, det_x + 4)):
        a = 0.5 * np.sin(np.pi * (i + 0.5) / 4)
        det_damp[col, :] = np.where(mask, 1.0 - a, 1.0)
    damp = sponge * slit_damp * det_damp

    clicks = np.zeros(Ny)
    incident = np.zeros(Ny)
    c = dt / (2 * dx * dx)
    for s in range(steps):
        lap = (np.roll(R, 1, 0) + np.roll(R, -1, 0) +
               np.roll(R, 1, 1) + np.roll(R, -1, 1) - 4 * R)
        I += c * lap * 2
        lap = (np.roll(I, 1, 0) + np.roll(I, -1, 0) +
               np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4 * I)
        R -= c * lap * 2
        p_before = R[det_x:det_x + 4, :] ** 2 + I[det_x:det_x + 4, :] ** 2
        R *= damp; I *= damp
        p_after = R[det_x:det_x + 4, :] ** 2 + I[det_x:det_x + 4, :] ** 2
        clicks += (p_before - p_after).sum(axis=0)
        incident += R[det_x - 6, :] ** 2 + I[det_x - 6, :] ** 2
    return clicks, incident

def js_div(p, q):
    p = p / p.sum(); q = q / q.sum(); m = 0.5 * (p + q)
    kl = lambda a, b: np.sum(np.where(a > 0, a * np.log(a / np.maximum(b, 1e-300)), 0))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

M = masks()
res = {}
for name, m in M.items():
    clicks, inc = run(m)
    res[name] = (clicks, inc)
    print(f"{name:>9}: total detected = {clicks.sum():.4f}   "
          f"(absorbing fraction of wall = {m.mean():.3f})")

# --- analysis ---
u_clicks, u_inc = res["uniform"]
print("\nGATING (do the walls yield different click distributions?):")
for name in ("periodic", "cantor"):
    d = js_div(res[name][0] + 1e-15, u_clicks + 1e-15)
    print(f"   JS divergence vs uniform wall: {name:>9} = {d:.4f}")

print("\nFRINGE INTEGRITY (is detected ~ incident x mask, i.e. gated but not shifted?):")
for name, m in M.items():
    clicks, inc = res[name]
    pred = inc * m                      # gating prediction
    keep = m & (inc > 0.01 * inc.max())
    if keep.sum() > 4:
        cc = np.corrcoef(clicks[keep], pred[keep])[0, 1]
        print(f"   {name:>9}: corr(detected, incident x mask) on live cells = {cc:.4f}")

# --- figure ---
fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
yy = np.arange(Ny)
for ax, name, col in zip(axes, ("uniform", "periodic", "cantor"),
                         ("tab:green", "tab:orange", "tab:red")):
    clicks, inc = res[name]
    m = M[name]
    ax.fill_between(yy, 0, (inc / inc.max()), color="gray", alpha=0.25,
                    label="incident interference pattern")
    ax.plot(yy, clicks / clicks.max(), color=col, lw=1.8, label=f"clicks ({name} wall)")
    ax.fill_between(yy, -0.14, -0.03, where=m, color=col, alpha=0.6)
    ax.text(3, -0.125, "absorbing cells", fontsize=8, color="dimgray")
    ax.set_ylim(-0.16, 1.08); ax.legend(loc="upper right", fontsize=9)
    ax.set_ylabel("normalized")
axes[0].set_title("Same wave, same fringes — the wall's structure gates WHERE clicks can happen")
axes[2].set_xlabel("position y along the detector wall")
fig.tight_layout()
fig.savefig("fractal_boundary.png", dpi=125)
print("\nsaved -> qsim/fractal_boundary.png")
