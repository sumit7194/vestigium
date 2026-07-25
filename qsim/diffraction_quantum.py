"""
Quantum version of the aperture progression: the screen pattern is built from
discrete single-particle detections.  Each particle lands at one random spot drawn
from the Born-rule probability P = |FT(aperture)|^2 -- the SAME distribution as the
classical intensity.  Fire many, and the dots accumulate into the same fringes.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 1024
yy, xx = np.mgrid[-N//2:N//2, -N//2:N//2].astype(float)
r = np.hypot(xx, yy); th = np.arctan2(yy, xx)
rng = np.random.default_rng(1)

def slits(sep, bow):
    m = np.zeros((N, N)); Hh, w = 360, 3
    for cx in (-sep/2, sep/2):
        c = cx + np.sign(cx)*bow*(1-(yy/Hh)**2)
        m[(np.abs(yy) < Hh) & (np.abs(xx-c) < w)] = 1
    return m
def arcs(R, gap):
    m = (np.abs(r-R) < 2.5).astype(float); m[np.abs(np.abs(th)-np.pi/2) < np.deg2rad(gap)] = 0; return m
def ring(R): return (np.abs(r-R) < 2.5).astype(float)
def disc(rad): return (r < rad).astype(float)

cases = [("two straight slits", slits(80,0)), ("two curved slits", slits(80,45)),
         ("two arcs  ( )", arcs(150,55)), ("arcs nearly closed", arcs(150,12)),
         ("full ring", ring(150)), ("small disc", disc(26))]

def prob(mask):
    P = np.abs(np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(mask))))**2
    return P

def sample(P, M, crop):
    c = N//2; sub = P[c-crop:c+crop, c-crop:c+crop].astype(float)
    sub = sub/sub.sum(); cdf = np.cumsum(sub.ravel())
    idx = np.searchsorted(cdf, rng.random(M)); w = sub.shape[1]
    return (idx % w) + rng.random(M), (idx // w) + rng.random(M)

crop = 150
# ---- figure 1: the 6 shapes as accumulated single-photon detections ----
fig, ax = plt.subplots(2, 6, figsize=(15, 5.4))
for k, (name, mask) in enumerate(cases):
    P = prob(mask)
    ax[0, k].imshow(mask[N//2-200:N//2+200, N//2-200:N//2+200], cmap="gray_r")
    ax[0, k].set_title(name, fontsize=10); ax[0, k].axis("off")
    x, y = sample(P, 28000, crop)
    ax[1, k].scatter(x, y, s=0.4, c="#ffd27a", alpha=0.5, linewidths=0)
    ax[1, k].set_xlim(0, 2*crop); ax[1, k].set_ylim(2*crop, 0)
    ax[1, k].set_facecolor("#07080c"); ax[1, k].set_xticks([]); ax[1, k].set_yticks([])
fig.text(0.012, 0.74, "aperture", rotation=90, va="center", fontsize=11)
fig.text(0.012, 0.27, "single-photon hits", rotation=90, va="center", fontsize=11)
fig.suptitle("Quantum: the same patterns, built one detected photon at a time (28,000 hits each)", fontsize=13)
fig.tight_layout(rect=[0.02, 0, 1, 1]); fig.savefig("diffraction_quantum.png", dpi=120)

# ---- figure 2: buildup of the straight double slit, dot by dot ----
P = prob(slits(80, 0))
counts = [80, 800, 8000, 60000]
fig2, ax2 = plt.subplots(1, 4, figsize=(15, 3.4))
for k, M in enumerate(counts):
    x, y = sample(P, M, crop)
    ax2[k].scatter(x, y, s=0.5, c="#ffd27a", alpha=0.55, linewidths=0)
    ax2[k].set_xlim(0, 2*crop); ax2[k].set_ylim(2*crop, 0)
    ax2[k].set_facecolor("#07080c"); ax2[k].set_xticks([]); ax2[k].set_yticks([])
    ax2[k].set_title(f"{M:,} photons", fontsize=11)
fig2.suptitle("Single photons fired one at a time -> the double-slit fringes emerge from random clicks", fontsize=13)
fig2.tight_layout(); fig2.savefig("buildup.png", dpi=120)
print("saved -> qsim/diffraction_quantum.png and qsim/buildup.png")
