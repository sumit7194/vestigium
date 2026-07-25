"""
Configuration space made drawable: put each particle on its own position axis
(1-D per particle, so the picture stays low-dimensional).

  1 particle  -> 1 axis  (this IS ordinary space)
  2 particles -> 2 axes  (a plane)   <- drawable
  3 particles -> 3 axes  (a cube)    <- barely drawable
  N particles -> N axes  (real 3-D particles: 3N axes)

A single POINT in this space = one whole arrangement ("A here AND B there").
Unentangled state -> the blob factors (axis-aligned) = same as two separate
1-D waves.  Entangled -> the blob lies on a diagonal = a correlation that can't
be split into separate waves.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 400)
g = lambda c, s=0.55: np.exp(-(x-c)**2/(2*s**2))
N = 300
ax = np.linspace(-3, 3, N)
XA, XB = np.meshgrid(ax, ax)
def blob2(ca, cb, s=0.42): return np.exp(-((XA-ca)**2+(XB-cb)**2)/(2*s**2))

fig = plt.figure(figsize=(15, 4.3))

# 1 particle -> a wave over one axis (real space)
a1 = fig.add_subplot(1, 4, 1)
a1.fill_between(x, g(0)**2, color="#efaf3a", alpha=0.85)
a1.set_title("1 particle\n(1 axis = ordinary space)", fontsize=11)
a1.set_xlabel("position of A"); a1.set_yticks([])

# 2 particles, UNentangled -> product, axis-aligned blob
a2 = fig.add_subplot(1, 4, 2)
P = (g_outer := np.outer(np.exp(-(ax**2)/(2*0.55**2)), np.exp(-(ax**2)/(2*0.55**2))))
a2.imshow(P, extent=[-3,3,-3,3], origin="lower", cmap="inferno")
a2.set_title("2 particles, UNentangled\nblob factors = 2 separate waves", fontsize=11)
a2.set_xlabel("position of A"); a2.set_ylabel("position of B")

# 2 particles, ENTANGLED -> correlated, lies on the diagonal
a3 = fig.add_subplot(1, 4, 3)
P2 = (blob2(-1.3, -1.3) + blob2(1.3, 1.3))**2
a3.imshow(P2, extent=[-3,3,-3,3], origin="lower", cmap="inferno")
a3.plot([-3,3], [-3,3], "w--", lw=0.7, alpha=0.5)
a3.set_title("2 particles, ENTANGLED\nbright only where A,B match", fontsize=11)
a3.set_xlabel("position of A"); a3.set_ylabel("position of B")

# 3 particles, ENTANGLED -> a cube, two lumps on the body diagonal (GHZ-like)
a4 = fig.add_subplot(1, 4, 4, projection="3d")
rng = np.random.default_rng(0)
pts = np.vstack([rng.normal([-1.3,-1.3,-1.3], 0.4, (1500,3)),
                 rng.normal([ 1.3, 1.3, 1.3], 0.4, (1500,3))])
a4.scatter(pts[:,0], pts[:,1], pts[:,2], s=2, c="#ffd27a", alpha=0.35, linewidths=0)
a4.set_title("3 particles, ENTANGLED\n(a cube; 4+ -> can't draw)", fontsize=11)
a4.set_xlabel("A"); a4.set_ylabel("B"); a4.set_zlabel("C")
a4.set_xlim(-3,3); a4.set_ylim(-3,3); a4.set_zlim(-3,3)

fig.suptitle("The quantum wave for N particles lives over N position-axes (configuration space), not in one shared 3-D space", fontsize=12)
fig.tight_layout(rect=[0,0,1,0.95])
fig.savefig("config_space.png", dpi=120)
print("saved -> qsim/config_space.png")
