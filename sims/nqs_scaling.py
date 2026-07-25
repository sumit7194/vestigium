"""
Scale the TFIM up at the critical point (h/J = 1, the hardest case) and pit the
Neural Quantum State against exact diagonalization.

The point: the Hilbert space is 2^N.  Exact diagonalization must build a 2^N x 2^N
matrix -> it hits a memory/time wall around N ~ 20-22.  The NQS cost grows only
~linearly in N (network input size, sampling), so it keeps running into Hilbert
spaces exact methods cannot touch.  We verify NQS against ED where ED still works,
then leave ED behind.
"""
import time
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nqs_tfim import LogPsi, mcmc, local_energy, exact_ground_energy

ED_MAX = 20  # above this, 2^N diagonalization is skipped (memory/time)


def run_nqs(N, J, h, hidden, n_chains, n_iters, lr, device):
    torch.manual_seed(0)
    net = LogPsi(N, hidden).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    chains = torch.randint(0, 2, (n_chains, N), device=device).float() * 2 - 1
    chains = mcmc(chains, net, 200)
    t0 = time.time()
    for _ in range(n_iters):
        chains = mcmc(chains, net, 4 * N)
        Eloc = local_energy(chains, net, J, h)
        Emean = Eloc.mean()
        f = net(chains)
        loss = 2.0 * ((Eloc - Emean).detach() * f).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        vals = [local_energy(mcmc(chains, net, 4 * N), net, J, h).mean().item()
                for _ in range(20)]
    return float(np.mean(vals)), time.time() - t0


def run_ed(N, J, h):
    if N > ED_MAX:
        return None, None
    t0 = time.time()
    E = exact_ground_energy(N, J, h)
    return E, time.time() - t0


def main():
    J, h = 1.0, 1.0
    hidden, n_chains, n_iters, lr = 64, 1024, 600, 5e-3
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    Ns = [10, 16, 20, 24, 32, 40]
    E_TD = -4.0 / np.pi  # thermodynamic-limit critical energy density

    print(f"device={device}  h/J={h}  hidden={hidden}  chains={n_chains}  iters={n_iters}")
    print(f"{'N':>3} {'dim=2^N':>12} | {'NQS E/N':>9} {'ED E/N':>9} {'rel.err':>8} | "
          f"{'NQS t(s)':>8} {'ED t(s)':>9}")
    rows = []
    for N in Ns:
        e_nqs, t_nqs = run_nqs(N, J, h, hidden, n_chains, n_iters, lr, device)
        e_ed, t_ed = run_ed(N, J, h)
        dim = 1 << N
        if e_ed is not None:
            rel = abs(e_nqs - e_ed) / abs(e_ed)
            print(f"{N:3d} {dim:12d} | {e_nqs/N:9.4f} {e_ed/N:9.4f} {rel:8.2e} | "
                  f"{t_nqs:8.1f} {t_ed:9.1f}")
        else:
            print(f"{N:3d} {dim:12d} | {e_nqs/N:9.4f} {'  --  ':>9} {'  --  ':>8} | "
                  f"{t_nqs:8.1f} {'INFEASIBLE':>9}")
        rows.append((N, e_nqs / N, (e_ed / N if e_ed is not None else np.nan),
                     t_nqs, (t_ed if t_ed is not None else np.nan)))
    a = np.array(rows)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    ax[0].axhline(E_TD, ls=":", color="gray", label=r"thermodynamic limit $-4/\pi$")
    ed_mask = ~np.isnan(a[:, 2])
    ax[0].plot(a[ed_mask, 0], a[ed_mask, 2], "k_", ms=14, mew=2.5, label="exact (ED)")
    ax[0].plot(a[:, 0], a[:, 1], "o", color="tab:blue", ms=7, label="NQS")
    ax[0].set_xlabel("N (spins)"); ax[0].set_ylabel("ground energy / site")
    ax[0].set_title("NQS tracks exact, then continues past the ED wall")
    ax[0].legend(); ax[0].grid(alpha=0.3)

    ax[1].plot(a[ed_mask, 0], a[ed_mask, 4], "k-s", lw=2, label="exact diagonalization")
    ax[1].plot(a[:, 0], a[:, 3], "-o", color="tab:blue", lw=2, label="NQS (this run)")
    ax[1].axvspan(ED_MAX + 0.5, a[:, 0].max() + 1, color="tab:red", alpha=0.08)
    ax[1].text(ED_MAX + 1, ax[1].get_ylim()[1] * 0.5 if ax[1].get_ylim()[1] > 0 else 1,
               "ED infeasible\n(2^N too large)", color="tab:red", fontsize=9, va="center")
    ax[1].set_yscale("log"); ax[1].set_xlabel("N (spins)")
    ax[1].set_ylabel("wall-clock time (s)")
    ax[1].set_title("Cost: ED explodes (2^N), NQS stays ~linear")
    ax[1].legend(); ax[1].grid(alpha=0.3, which="both")
    fig.suptitle("TFIM at criticality: neural network beyond exact diagonalization")
    fig.tight_layout()
    fig.savefig("scaling.png", dpi=130)
    print("saved plot -> sims/scaling.png")
    print(f"largest NQS system: N={Ns[-1]}  ->  Hilbert dimension 2^{Ns[-1]} = {1<<Ns[-1]:,}")


if __name__ == "__main__":
    main()
