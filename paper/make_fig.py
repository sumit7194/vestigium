"""Figure 1 of paper/mn_chaos.tex (ILLUSTRATIVE, floating point; not part of any proof).
The splitting function Delta K_r(psi_0) / beta = [K_r(W^u) - K_r(W^s)] / beta at the outer turning point, from the S1
float runs (qsim/mn_homoclinic_spike/s1_beta_*.json, committed), against the first-order Melnikov prediction
4 Upsilon_theta |L_2| sin(2 psi_0), with L_2 the interval-certified coefficient (qsim/mn_melnikov/RESULT.md)."""
import os, sys, json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); SP = os.path.join(HERE, "..", "qsim", "mn_homoclinic_spike"); sys.path.insert(0, SP)
import s1
UPS, L2 = 15.0122754941206972, -4.77482114974644e-5
g = np.linspace(0, 2 * np.pi, 721)
fig, ax = plt.subplots(figsize=(6.2, 3.4))
for b, st in (("0.0001", "-"), ("0.01", "--"), ("0.03", ":")):
    r = json.load(open(os.path.join(SP, "s1_beta_%s.json" % b)))
    dK = s1.spline(r["U"])(g) - s1.spline(r["S"])(g)
    ax.plot(g, dK / float(b) * 1e3, st, lw=1.4, label=r"$\beta=%s$ (float)" % {"0.0001": "10^{-4}", "0.01": "10^{-2}", "0.03": "3\\times10^{-2}"}[b])
ax.plot(g, 4 * UPS * abs(L2) * np.sin(2 * g) * 1e3, "k-", lw=0.6, alpha=0.6, label=r"Melnikov: $4\Upsilon_\theta|L_2|\sin 2\psi_0$")
ax.axvline(1.5 * np.pi, color="0.5", lw=0.7); ax.text(1.5 * np.pi + 0.07, 0.25, r"$\psi_*=3\pi/2$", fontsize=8, color="0.3")
ax.axhline(0, color="0.8", lw=0.5)
ax.set_xlim(0, 2 * np.pi); ax.set_xticks([0, np.pi / 2, np.pi, 1.5 * np.pi, 2 * np.pi]); ax.set_xticklabels(["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"])
ax.set_xlabel(r"$\psi_0$ ($\theta$-phase at the outer turning point)"); ax.set_ylabel(r"$\Delta K_r(\psi_0)/\beta\ \ [\times 10^{-3}]$")
ax.legend(fontsize=7.5, loc="upper right", frameon=False); fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig_splitting.pdf")); fig.savefig(os.path.join(HERE, "fig_splitting.png"), dpi=130); print("ok")
