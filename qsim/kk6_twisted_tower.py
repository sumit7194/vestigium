"""
BRIDGE ASK 1 (round 6, 2026-07-10) — the 6D twisted tower, direct numerics.

Two hidden loops (y1, y2), R = 1, with twisted internal metric
    M = [[1, chi], [chi, 1]],   inverse g = M^-1 = [[1, -chi], [-chi, 1]]/(1-chi^2).
A massless wave's rest-buzz is governed by the hidden Laplacian
    L = g11 d2/dy1^2 + 2 g12 d/dy1 d/dy2 + g22 d2/dy2^2 .

BLIND PROTOCOL: the evolution below uses ONLY the metric coefficients and
finite-difference stencils; the measurement pipeline extracts the oscillation
frequency from the dynamics (mode-projected signal -> Hann window -> FFT ->
parabolic peak interpolation). The target formula is evaluated in a separate
scoring block AFTER all measurements are recorded. Discretization systematics:
centered 2nd-order stencils on a 64x64 torus -> expected O((n*dy)^2/12) ~ 0.3%
at the highest winding.

Sectors: (1,0), (0,1), (1,1), (1,-1), (2,1) at chi = 0 and chi = 0.3.
Deliverable: console table + kk6_twisted_tower.json for the bridge's ledger.
"""
import json
import numpy as np

# ---------------- lattice + integrator (geometry only — no formula) ----------
Ny = 64
dy = 2*np.pi/Ny
y = np.arange(Ny)*dy
Y1, Y2 = np.meshgrid(y, y, indexing="ij")

def evolve_rest_buzz(n1, n2, chi, T=140.0):
    det = 1.0 - chi*chi
    g11 = 1.0/det; g22 = 1.0/det; g12 = -chi/det
    dt = 0.12*dy
    steps = int(T/dt)
    mode = np.cos(n1*Y1 + n2*Y2)
    phi = mode.copy()
    phi_prev = phi.copy()                       # zero initial velocity
    inv_dy2 = 1.0/(dy*dy)
    sig = np.empty(steps)
    norm = np.sum(mode*mode)
    for s in range(steps):
        d11 = (np.roll(phi, 1, 0) + np.roll(phi, -1, 0) - 2*phi)*inv_dy2
        d22 = (np.roll(phi, 1, 1) + np.roll(phi, -1, 1) - 2*phi)*inv_dy2
        d12 = (np.roll(np.roll(phi, 1, 0), 1, 1) + np.roll(np.roll(phi, -1, 0), -1, 1)
               - np.roll(np.roll(phi, 1, 0), -1, 1) - np.roll(np.roll(phi, -1, 0), 1, 1)) \
              * (0.25*inv_dy2)
        lap = g11*d11 + 2*g12*d12 + g22*d22
        phi_new = 2*phi - phi_prev + dt*dt*lap
        phi_prev, phi = phi, phi_new
        sig[s] = np.sum(phi*mode)/norm          # mode-projected signal ~ cos(w t)
    return sig, dt

def measure_freq(sig, dt):
    s = (sig - sig.mean())*np.hanning(sig.size)
    sp = np.abs(np.fft.rfft(s))
    fr = np.fft.rfftfreq(sig.size, dt)*2*np.pi
    i = int(np.argmax(sp))
    if 0 < i < sp.size - 1:
        d = 0.5*(sp[i-1] - sp[i+1])/(sp[i-1] - 2*sp[i] + sp[i+1])
        return float(fr[i] + d*(fr[1] - fr[0]))
    return float(fr[i])

# ---------------- measurements (recorded before any scoring) -----------------
sectors = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1)]
chis = [0.0, 0.3]
measured = {}
for chi in chis:
    for (n1, n2) in sectors:
        sig, dt = evolve_rest_buzz(n1, n2, chi)
        measured[(chi, n1, n2)] = measure_freq(sig, dt)

# ---------------- scoring block (formula evaluated only now) -----------------
def target_m(n1, n2, chi):
    return np.sqrt((n1*n1 - 2*chi*n1*n2 + n2*n2)/(1 - chi*chi))

rows = []
print(f"{'chi':>5} {'(n1,n2)':>9} {'m_measured':>11} {'m_target':>10} {'err %':>7}")
for chi in chis:
    for (n1, n2) in sectors:
        m_meas = measured[(chi, n1, n2)]
        m_tgt = target_m(n1, n2, chi)
        err = (m_meas - m_tgt)/m_tgt*100
        rows.append({"chi": chi, "n1": n1, "n2": n2,
                     "m_measured": round(m_meas, 6),
                     "m_target": round(float(m_tgt), 6),
                     "err_percent": round(float(err), 4)})
        print(f"{chi:5.2f} {str((n1,n2)):>9} {m_meas:11.5f} {m_tgt:10.5f} {err:7.3f}")

# degeneracy / splitting summary
def get(chi, n1, n2): return measured[(chi, n1, n2)]
split0 = abs(get(0.0, 1, 1) - get(0.0, 1, -1))
split3 = abs(get(0.3, 1, 1) - get(0.3, 1, -1))
deg3 = abs(get(0.3, 1, 0) - get(0.3, 0, 1))
print(f"\n(1,1)/(1,-1) splitting:  chi=0: {split0:.5f}   chi=0.3: {split3:.5f}"
      f"   (target {target_m(1,-1,0.3)-target_m(1,1,0.3):.5f})")
print(f"(1,0)/(0,1)  splitting at chi=0.3: {deg3:.2e}   (target 0: stays degenerate)")

summary = {
    "ask": "bridge round-6 ask-1: 6D twisted tower rest-buzz",
    "protocol": "blind (integrator = geometry+stencils only; formula scored after measurement)",
    "lattice": {"Ny": Ny, "stencil": "2nd-order centered incl. mixed d12", "T": 140.0},
    "rows": rows,
    "splittings": {
        "pair_11_1m1_chi0": round(split0, 6),
        "pair_11_1m1_chi03_measured": round(split3, 6),
        "pair_11_1m1_chi03_target": round(float(target_m(1, -1, 0.3) - target_m(1, 1, 0.3)), 6),
        "pair_10_01_chi03_measured": round(deg3, 8),
        "pair_10_01_chi03_target": 0.0,
    },
    "reading": "splitting keyed by n1*n2 = the section-113 axion, made measurable",
}
with open("kk6_twisted_tower.json", "w") as fh:
    json.dump(summary, fh, indent=1)
print("\nsaved -> qsim/kk6_twisted_tower.json")
