"""
Far-field (Fraunhofer) diffraction patterns for a progression of apertures:
two straight slits -> curved slits -> arcs -> a ring -> a disc.

The screen pattern is |FourierTransform(aperture)|^2.  We just build each aperture
as a binary mask and FFT it.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 1024
yy, xx = np.mgrid[-N//2:N//2, -N//2:N//2].astype(float)
r = np.hypot(xx, yy)
th = np.arctan2(yy, xx)

def slits(sep, bow):
    m = np.zeros((N, N))
    Hh, w = 360, 3
    for cx in (-sep/2, sep/2):
        c = cx + np.sign(cx) * bow * (1 - (yy/Hh)**2)
        m[(np.abs(yy) < Hh) & (np.abs(xx - c) < w)] = 1
    return m

def arcs(R, gap_deg):                       # ring of radius R with gaps at top & bottom
    g = np.deg2rad(gap_deg)
    m = (np.abs(r - R) < 2.5).astype(float)
    m[np.abs(np.abs(th) - np.pi/2) < g] = 0   # cut top & bottom -> left & right arcs
    return m

def ring(R):  return (np.abs(r - R) < 2.5).astype(float)
def disc(rad): return (r < rad).astype(float)

cases = [
    ("two straight slits",      slits(80, 0)),
    ("two curved slits",        slits(80, 45)),
    ("two arcs  ( )",           arcs(150, 55)),
    ("arcs nearly closed",      arcs(150, 12)),
    ("full ring",               ring(150)),
    ("small disc",              disc(26)),
]

def farfield(mask):
    F = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(mask)))
    I = np.abs(F)**2
    return I / I.max()

fig, axes = plt.subplots(2, 6, figsize=(15, 5.4))
crop = 150  # central region of the screen to show
for k, (name, mask) in enumerate(cases):
    I = farfield(mask)
    c = N//2
    sub = I[c-crop:c+crop, c-crop:c+crop]
    axes[0, k].imshow(mask[c-200:c+200, c-200:c+200], cmap="gray_r")
    axes[0, k].set_title(name, fontsize=10); axes[0, k].axis("off")
    axes[1, k].imshow(np.log1p(sub*600), cmap="inferno")
    axes[1, k].axis("off")
axes[0, 0].set_ylabel("aperture")
fig.text(0.012, 0.74, "aperture", rotation=90, va="center", fontsize=11)
fig.text(0.012, 0.27, "screen pattern", rotation=90, va="center", fontsize=11)
fig.suptitle("Diffraction: as two slits curve into a ring, straight fringes bend into concentric rings", fontsize=13)
fig.tight_layout(rect=[0.02, 0, 1, 1])
fig.savefig("diffraction_shapes.png", dpi=120)
print("saved -> qsim/diffraction_shapes.png")
