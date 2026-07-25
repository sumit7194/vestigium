"""
Stage 3, fixed: bake in the Z2 (global spin-flip) symmetry so the network represents
the symmetric 'cat' ground state in the ordered phase -- recovering the correct
entanglement entropy that the plain ansatz lost to spontaneous symmetry breaking.

Fix: f(s) -> logaddexp(f_raw(s), f_raw(-s)), which makes psi(s) = psi(-s) exactly.
Same idea as Stage (c)'s translation symmetry: a physical symmetry, built into the
architecture, makes the hard regime tractable.
"""
import copy
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import torch
import torch.nn as nn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sims"))
from nqs_tfim import mcmc, local_energy            # noqa: E402


class Z2SymCNN(nn.Module):
    """Translation- AND global-spin-flip-symmetric log-amplitude."""
    def __init__(self, channels=16, kernel=5, n_layers=3):
        super().__init__()
        layers, in_c = [], 1
        for _ in range(n_layers):
            layers += [nn.Conv1d(in_c, channels, kernel,
                                 padding=kernel // 2, padding_mode="circular"), nn.Tanh()]
            in_c = channels
        self.conv = nn.Sequential(*layers)
        self.head = nn.Conv1d(channels, 1, 1)

    def _raw(self, s):
        return self.head(self.conv(s.unsqueeze(1))).sum(dim=(1, 2))

    def forward(self, s):
        return torch.logaddexp(self._raw(s), self._raw(-s))   # psi(s) = psi(-s)


def all_configs(N):
    idx = np.arange(1 << N, dtype=np.int64)
    return 1.0 - 2.0 * ((idx[:, None] >> np.arange(N)) & 1).astype(np.float32)


def entropy_bits(psi, N):
    M = psi.reshape(1 << (N // 2), 1 << (N - N // 2))
    lam = np.linalg.svd(M, compute_uv=False) ** 2
    lam = lam[lam > 1e-14]; lam = lam / lam.sum()
    return float(-np.sum(lam * np.log2(lam)))


def exact_psi(N, J, h):
    dim = 1 << N; st = np.arange(dim, dtype=np.int64)
    sps = np.stack([1 - 2 * ((st >> i) & 1) for i in range(N)], axis=1)
    zz = sum(sps[:, i] * sps[:, (i + 1) % N] for i in range(N))
    rows, cols, data = [st], [st], [(-J * zz).astype(float)]
    for i in range(N):
        rows.append(st); cols.append(st ^ (1 << i)); data.append(np.full(dim, -h))
    H = sp.coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(dim, dim)).tocsr()
    _, v = spla.eigsh(H, k=1, which="SA")
    return v[:, 0]


def nn_psi(net, N, device):
    cfg = all_configs(N)
    with torch.no_grad():
        f = net(torch.tensor(cfg, device=device)).cpu().numpy()
    f = f - f.max(); psi = np.exp(f); return psi / np.linalg.norm(psi)


def train(net, chains, N, J, h, iters, lr=5e-3):
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    for _ in range(iters):
        chains = mcmc(chains, net, 4 * N)
        El = local_energy(chains, net, J, h); Em = El.mean()
        f = net(chains); loss = 2.0 * ((El - Em).detach() * f).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return net, chains


def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    J, N, iters = 1.0, 12, 350
    torch.manual_seed(0)
    hs = [1.6, 1.4, 1.2, 1.0, 0.8, 0.6, 0.4]

    print(f"device={device}  N={N}  Z2-symmetric ansatz  (entanglement entropy, bits)")
    print(f"{'h/J':>5} | {'S_NN':>7} {'S_exact':>8}")
    net = Z2SymCNN(16, 5, 3).to(device)
    chains = torch.randint(0, 2, (1024, N), device=device).float() * 2 - 1
    chains = mcmc(chains, net, 200)
    rows = []
    t0 = time.time()
    for h in hs:
        net, chains = train(net, chains, N, J, h, iters)
        s_nn = entropy_bits(nn_psi(net, N, device), N)
        s_ex = entropy_bits(exact_psi(N, J, h), N)
        print(f"{h:5.2f} | {s_nn:7.3f} {s_ex:8.3f}")
        rows.append((h, s_nn, s_ex))
    print(f"(trained in {time.time()-t0:.1f}s)")

    a = np.array(rows)
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.plot(a[:, 0], a[:, 2], "k-", lw=2, label="exact")
    ax.plot(a[:, 0], a[:, 1], "o", color="tab:green", ms=8, label="Z2-symmetric NN")
    ax.axvline(1.0, ls="--", color="gray")
    ax.set_xlabel("field  h / J"); ax.set_ylabel("entanglement entropy (bits)")
    ax.set_title(f"Symmetry baked in: entanglement now correct everywhere (N={N})")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig("stage3_symmetric.png", dpi=130)
    print("saved plot -> qsim/stage3_symmetric.png")


if __name__ == "__main__":
    main()
