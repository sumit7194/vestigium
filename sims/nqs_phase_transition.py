"""
Sweep the transverse field h across the TFIM quantum phase transition and measure
two observables directly from the trained Neural Quantum State, overlaid on exact
diagonalization:

  <sigma^x>   transverse magnetization   (0  -> 1   as field wins)   [off-diagonal]
  <M_z^2>     order parameter, M_z=(1/N)sum s_i  (1 -> ~0 ordered->disordered) [diagonal]

The critical point sits at h/J = 1.  We warm-start each field from the previous one
(adiabatic continuation), so a few hundred VMC steps per h suffice.
"""
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nqs_tfim import LogPsi, mcmc, local_energy


def exact_observables(N, J, h):
    dim = 1 << N
    states = np.arange(dim, dtype=np.int64)
    spins = np.stack([1 - 2 * ((states >> i) & 1) for i in range(N)], axis=1).astype(np.float64)
    zz = sum(spins[:, i] * spins[:, (i + 1) % N] for i in range(N))
    rows = [states]; cols = [states]; data = [(-J * zz)]
    for i in range(N):
        rows.append(states); cols.append(states ^ (1 << i)); data.append(np.full(dim, -h))
    H = sp.coo_matrix((np.concatenate(data),
                       (np.concatenate(rows), np.concatenate(cols))),
                      shape=(dim, dim)).tocsr()
    e, v = spla.eigsh(H, k=1, which="SA")
    psi = v[:, 0]
    sx = sum(float(np.dot(psi, psi[states ^ (1 << i)])) for i in range(N)) / N
    Mz = spins.mean(axis=1)
    mz2 = float(np.dot(psi**2, Mz**2))
    return float(e[0]), sx, mz2


@torch.no_grad()
def nqs_observables(chains, net, steps, J, h, N, reps=25):
    sx, mz2, en = [], [], []
    for _ in range(reps):
        chains = mcmc(chains, net, steps)
        f0 = net(chains)
        s = 0.0
        for i in range(N):
            flip = chains.clone(); flip[:, i] = -flip[:, i]
            s = s + torch.exp(net(flip) - f0).mean()
        sx.append((s / N).item())
        mz2.append((chains.mean(dim=1) ** 2).mean().item())
        en.append(local_energy(chains, net, J, h).mean().item())
    return chains, np.mean(en), np.mean(sx), np.mean(mz2)


def train_at(net, chains, J, h, N, steps, lr, n_iters):
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    for _ in range(n_iters):
        chains = mcmc(chains, net, steps)
        Eloc = local_energy(chains, net, J, h)
        Emean = Eloc.mean()
        f = net(chains)
        loss = 2.0 * ((Eloc - Emean).detach() * f).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return net, chains


def main():
    N, J, hidden = 10, 1.0, 48
    n_chains, steps, lr, n_iters = 2048, 4 * 10, 5e-3, 400
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    torch.manual_seed(0)
    # sweep high field -> low field: easy (paramagnetic) first, warm-start into the
    # hard ordered phase so the network never has to find the cat state cold.
    hs = [2.0, 1.8, 1.6, 1.4, 1.2, 1.1, 1.0, 0.9, 0.8, 0.6, 0.4, 0.2]

    net = LogPsi(N, hidden).to(device)
    chains = torch.randint(0, 2, (n_chains, N), device=device).float() * 2 - 1
    chains = mcmc(chains, net, 200)

    print(f"device={device}  N={N}  (warm-started sweep)")
    print(f"{'h/J':>5} | {'E/N nqs':>8} {'E/N ex':>8} | {'<sx>nqs':>8} {'<sx>ex':>8} | {'Mz2 nqs':>8} {'Mz2 ex':>8}")
    rows = []
    t0 = time.time()
    for h in hs:
        net, chains = train_at(net, chains, J, h, N, steps, lr, n_iters)
        chains, e_n, sx_n, mz2_n = nqs_observables(chains, net, steps, J, h, N)
        e_x, sx_x, mz2_x = exact_observables(N, J, h)
        print(f"{h:5.2f} | {e_n/N:8.4f} {e_x/N:8.4f} | {sx_n:8.4f} {sx_x:8.4f} | {mz2_n:8.4f} {mz2_x:8.4f}")
        rows.append((h, e_n / N, e_x / N, sx_n, sx_x, mz2_n, mz2_x))
    print(f"swept {len(hs)} fields in {time.time()-t0:.1f}s on {device}")

    a = np.array(rows)
    a = a[a[:, 0].argsort()]   # sort by h for clean exact lines
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot(a[:, 0], a[:, 4], "k-", lw=2, label="exact")
    ax[0].plot(a[:, 0], a[:, 3], "o", color="tab:blue", ms=7, label="NQS")
    ax[0].axvline(1.0, ls="--", color="gray"); ax[0].set_xlabel("h / J")
    ax[0].set_ylabel(r"$\langle \sigma^x \rangle$"); ax[0].set_title("Transverse magnetization")
    ax[0].legend(); ax[0].grid(alpha=0.3)
    ax[1].plot(a[:, 0], a[:, 6], "k-", lw=2, label="exact")
    ax[1].plot(a[:, 0], a[:, 5], "s", color="tab:red", ms=7, label="NQS")
    ax[1].axvline(1.0, ls="--", color="gray"); ax[1].set_xlabel("h / J")
    ax[1].set_ylabel(r"$\langle M_z^2 \rangle$"); ax[1].set_title(r"Order parameter $\langle M_z^2\rangle$")
    ax[1].legend(); ax[1].grid(alpha=0.3)
    fig.suptitle(f"TFIM quantum phase transition (N={N}) — neural network vs exact")
    fig.tight_layout()
    fig.savefig("phase_transition.png", dpi=130)
    print("saved plot -> sims/phase_transition.png")


if __name__ == "__main__":
    main()
