"""
Electron vs positron, as waves:
 1) free wavepacket |psi|^2  -> identical shapes (same mass -> same spreading)
 2) the internal phase 'corkscrew' -> opposite handedness (the real difference)
 3) in a magnetic field -> opposite curving (how the handedness becomes visible)
 4) annihilation -> overlapping opposite waves dump all energy into the EM field
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(13, 9))

# --- 1) identical packets ---
ax1 = fig.add_subplot(2, 2, 1)
x = np.linspace(-6, 6, 500)
p = np.exp(-x**2/2)
ax1.plot(x, p**2, color="tab:blue", lw=2.5, label="electron  $|\\psi|^2$")
ax1.plot(x, p**2, color="tab:red", lw=2.5, ls=(0, (4, 4)), label="positron  $|\\psi|^2$")
ax1.set_title("1) Free wavepackets: literally identical\n(same mass -> same wavelength, same spreading)")
ax1.set_xlabel("position"); ax1.set_yticks([]); ax1.legend()

# --- 2) opposite phase corkscrews ---
ax2 = fig.add_subplot(2, 2, 2, projection="3d")
t = np.linspace(0, 4*np.pi, 300)
ax2.plot(t, np.cos(t),  np.sin(t), color="tab:blue", lw=2, label="electron phase")
ax2.plot(t, np.cos(t), -np.sin(t), color="tab:red", lw=2, label="positron phase")
ax2.set_title("2) The internal clock winds opposite ways\n(left- vs right-handed corkscrew)")
ax2.set_xlabel("time ->"); ax2.set_ylabel("Re"); ax2.set_zlabel("Im")
ax2.set_yticks([]); ax2.set_zticks([]); ax2.legend(loc="upper left", fontsize=9)

# --- 3) opposite bend in a magnetic field ---
ax3 = fig.add_subplot(2, 2, 3)
th = np.linspace(0, 0.75*np.pi, 100)
R = 1.0
ax3.plot(R*np.sin(th),  R-R*np.cos(th),  color="tab:blue", lw=2.5)
ax3.plot(R*np.sin(th), -R+R*np.cos(th),  color="tab:red", lw=2.5)
ax3.annotate("electron", (1.05, 0.9), color="tab:blue")
ax3.annotate("positron", (1.05, -1.0), color="tab:red")
ax3.annotate("", xy=(0.45, 0.11), xytext=(0.15, 0.01),
             arrowprops=dict(arrowstyle="->", color="tab:blue"))
ax3.annotate("", xy=(0.45, -0.11), xytext=(0.15, -0.01),
             arrowprops=dict(arrowstyle="->", color="tab:red"))
for xx in np.linspace(0.1, 1.6, 4):
    for yy in np.linspace(-1.3, 1.3, 4):
        ax3.plot(xx, yy, "x", color="gray", ms=6, alpha=0.5)
ax3.text(1.45, 1.25, "B field (into page)", color="gray", fontsize=9)
ax3.set_title("3) Same push, opposite bend\n(the handedness made visible by a field)")
ax3.set_xlim(-0.1, 1.9); ax3.set_ylim(-1.5, 1.5)
ax3.set_xticks([]); ax3.set_yticks([]); ax3.set_aspect("equal")

# --- 4) annihilation ---
ax4 = fig.add_subplot(2, 2, 4)
xx = np.linspace(-6, 6, 500)
ax4.plot(xx, np.exp(-(xx+3.2)**2/1.2)*np.cos(6*xx)*0.5+1.2, color="tab:blue", lw=1.8)
ax4.plot(xx, np.exp(-(xx-3.2)**2/1.2)*np.cos(6*xx)*0.5+1.2, color="tab:red", lw=1.8)
ax4.annotate("", xy=(-1.6, 1.2), xytext=(-3.0, 1.2), arrowprops=dict(arrowstyle="->", color="tab:blue"))
ax4.annotate("", xy=(1.6, 1.2), xytext=(3.0, 1.2), arrowprops=dict(arrowstyle="->", color="tab:red"))
ax4.plot(0, 0, "*", color="#efaf3a", ms=20)
gx = np.linspace(0.4, 5.6, 300)
ax4.plot(gx, 0.25*np.sin(9*gx)*np.exp(-0*gx), color="#b8860b", lw=1.6)
ax4.plot(-gx, 0.25*np.sin(9*gx), color="#b8860b", lw=1.6)
ax4.annotate("photon  511 keV", (2.4, -0.62), color="#b8860b")
ax4.annotate("photon  511 keV", (-5.6, -0.62), color="#b8860b")
ax4.set_title("4) Overlap -> annihilation:\nboth excitations unwind, all energy -> EM field")
ax4.set_xlim(-6, 6); ax4.set_ylim(-1.1, 2.1); ax4.set_xticks([]); ax4.set_yticks([])

fig.suptitle("Electron vs positron: same wave, opposite internal winding", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("matter_antimatter.png", dpi=120)
print("saved -> qsim/matter_antimatter.png")
