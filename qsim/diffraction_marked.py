"""
Same aperture progression, now WITH which-path markers (orthogonal polarizers, H|V)
on the two halves of each aperture.

Marking removes the interference between the two marked regions:
  unmarked:  P = |FT(left) + FT(right)|^2      (coherent -> fringes)
  marked:    P = |FT(left)|^2 + |FT(right)|^2   (incoherent -> fringes gone)
Whatever structure came from left<->right coherence disappears; each region's own
diffraction envelope survives.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 1024
yy, xx = np.mgrid[-N//2:N//2, -N//2:N//2].astype(float)
r = np.hypot(xx, yy); th = np.arctan2(yy, xx)

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

def ft(m): return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(m)))
def show(P): return np.log1p(P/P.max()*600)

crop = 150
fig, ax = plt.subplots(3, 6, figsize=(15, 7.6))
for k, (name, m) in enumerate(cases):
    L = m*(xx < 0); R = m*(xx >= 0)
    P_un = np.abs(ft(m))**2
    P_mk = np.abs(ft(L))**2 + np.abs(ft(R))**2          # markers: drop the cross term
    # colored aperture: left half = H (red), right half = V (blue)
    rgb = np.ones((400, 400, 3))
    a = m[N//2-200:N//2+200, N//2-200:N//2+200]
    lx = xx[N//2-200:N//2+200, N//2-200:N//2+200] < 0
    rgb[(a>0)&lx] = [0.85, 0.2, 0.2]; rgb[(a>0)&~lx] = [0.2, 0.4, 0.9]
    ax[0, k].imshow(rgb); ax[0, k].set_title(name, fontsize=10); ax[0, k].axis("off")
    c = N//2
    ax[1, k].imshow(show(P_un)[c-crop:c+crop, c-crop:c+crop], cmap="inferno"); ax[1, k].axis("off")
    ax[2, k].imshow(show(P_mk)[c-crop:c+crop, c-crop:c+crop], cmap="inferno"); ax[2, k].axis("off")
for row, lab in [(0, "aperture  (H | V)"), (1, "NO markers"), (2, "WITH markers")]:
    fig.text(0.012, 0.84-row*0.31, lab, rotation=90, va="center", fontsize=11)
fig.suptitle("Which-path markers erase the interference between the two halves — the fringes/rings wash out", fontsize=13)
fig.tight_layout(rect=[0.02, 0, 1, 1]); fig.savefig("diffraction_marked.png", dpi=120)
print("saved -> qsim/diffraction_marked.png")
