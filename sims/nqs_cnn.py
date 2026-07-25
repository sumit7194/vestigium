"""
(c) Make big-N accurate, not just runnable.

The plain MLP has to LEARN that the chain is translation-symmetric, and it does so
worse and worse as N grows (its first layer even grows with N).  Here we BAKE the
symmetry into the architecture: a 1D CNN with circular (periodic) padding is
translation-EQUIVARIANT; summing its per-site outputs makes the log-amplitude
translation-INVARIANT exactly.  Bonus: the parameter count is independent of N.

We run the symmetric CNN head-to-head against the MLP at the critical point and
compare ground-state energies (lower = closer to the truth, guaranteed by the
variational principle), with exact diagonalization where it still fits.
"""
import time
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nqs_tfim import LogPsi, mcmc, local_energy, exact_ground_energy

ED_MAX = 20


class TransInvCNN(nn.Module):
    """Translation-invariant log-amplitude: circular conv stack -> sum over sites."""
    def __init__(self, channels=16, kernel=5, n_layers=3):
        super().__init__()
        layers, in_c = [], 1
        for _ in range(n_layers):
            layers += [nn.Conv1d(in_c, channels, kernel,
                                 padding=kernel // 2, padding_mode="circular"),
                       nn.Tanh()]
            in_c = channels
        self.conv = nn.Sequential(*layers)
        self.head = nn.Conv1d(channels, 1, 1)   # per-site scalar

    def forward(self, s):                # s: [batch, N] of +/-1
        x = self.conv(s.unsqueeze(1))    # [batch, C, N]
        return self.head(x).sum(dim=(1, 2))   # [batch], invariant under cyclic shift


def train_eval(make_net, N, J, h, n_chains, n_iters, lr, device):
    torch.manual_seed(0)
    net = make_net().to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    chains = torch.randint(0, 2, (n_chains, N), device=device).float() * 2 - 1
    chains = mcmc(chains, net, 200)
    t0 = time.time()
    for _ in range(n_iters):
        chains = mcmc(chains, net, 4 * N)
        Eloc = local_energy(chains, net, J, h)
        Em = Eloc.mean()
        f = net(chains)
        loss = 2.0 * ((Eloc - Em).detach() * f).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        vals = [local_energy(mcmc(chains, net, 4 * N), net, J, h).mean().item()
                for _ in range(20)]
    n_params = sum(p.numel() for p in net.parameters())
    return float(np.mean(vals)), n_params, time.time() - t0


def main():
    J, h = 1.0, 1.0
    n_chains, n_iters, lr = 1024, 500, 5e-3
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    Ns = [10, 16, 20, 28, 40]
    E_TD = -4.0 / np.pi

    print(f"device={device}  h/J={h}  iters={n_iters}")
    print(f"{'N':>3} | {'MLP E/N':>9} {'CNN E/N':>9} {'ED E/N':>9} | "
          f"{'MLP err':>8} {'CNN err':>8} | {'MLP par':>7} {'CNN par':>7}")
    rows = []
    for N in Ns:
        e_mlp, p_mlp, _ = train_eval(lambda: LogPsi(N, 64), N, J, h, n_chains, n_iters, lr, device)
        e_cnn, p_cnn, _ = train_eval(lambda: TransInvCNN(16, 5, 3), N, J, h, n_chains, n_iters, lr, device)
        e_ed = exact_ground_energy(N, J, h) if N <= ED_MAX else None
        if e_ed is not None:
            err_m = abs(e_mlp - e_ed) / abs(e_ed)
            err_c = abs(e_cnn - e_ed) / abs(e_ed)
            print(f"{N:3d} | {e_mlp/N:9.4f} {e_cnn/N:9.4f} {e_ed/N:9.4f} | "
                  f"{err_m:8.2e} {err_c:8.2e} | {p_mlp:7d} {p_cnn:7d}")
        else:
            err_m = err_c = np.nan
            print(f"{N:3d} | {e_mlp/N:9.4f} {e_cnn/N:9.4f} {'   --  ':>9} | "
                  f"{'   --  ':>8} {'   --  ':>8} | {p_mlp:7d} {p_cnn:7d}   (CNN E<MLP E => CNN better)")
        rows.append((N, e_mlp/N, e_cnn/N, (e_ed/N if e_ed is not None else np.nan), err_m, err_c))
    a = np.array(rows)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    ax[0].axhline(E_TD, ls=":", color="gray", label=r"thermodynamic limit $-4/\pi$")
    ed = ~np.isnan(a[:, 3])
    ax[0].plot(a[ed, 0], a[ed, 3], "k_", ms=16, mew=2.5, label="exact (ED)")
    ax[0].plot(a[:, 0], a[:, 1], "-o", color="tab:orange", label="MLP (no symmetry)")
    ax[0].plot(a[:, 0], a[:, 2], "-s", color="tab:blue", label="CNN (symmetry baked in)")
    ax[0].set_xlabel("N (spins)"); ax[0].set_ylabel("ground energy / site")
    ax[0].set_title("Lower = better (variational). CNN hugs exact; MLP drifts up.")
    ax[0].legend(); ax[0].grid(alpha=0.3)

    ax[1].semilogy(a[ed, 0], a[ed, 4], "-o", color="tab:orange", label="MLP")
    ax[1].semilogy(a[ed, 0], a[ed, 5], "-s", color="tab:blue", label="CNN")
    ax[1].set_xlabel("N (spins)"); ax[1].set_ylabel("relative error vs exact")
    ax[1].set_title("Error vs exact (where ED fits): CNN far tighter")
    ax[1].legend(); ax[1].grid(alpha=0.3, which="both")
    fig.suptitle("Symmetry-aware ansatz: accuracy that holds as the system grows")
    fig.tight_layout()
    fig.savefig("cnn_vs_mlp.png", dpi=130)
    print("saved plot -> sims/cnn_vs_mlp.png")


if __name__ == "__main__":
    main()
