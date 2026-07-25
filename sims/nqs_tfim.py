"""
Neural Quantum State for the 1D Transverse-Field Ising Model (TFIM), via
Variational Monte Carlo (VMC).  A small neural network *is* the wavefunction:
it maps a spin configuration s -> log-amplitude f(s), so psi(s) = exp(f(s)).

No training data. The only "teacher" is the Hamiltonian, fed in through the loss
(the variational energy).  We then check the answer against exact diagonalization.

Why TFIM: it is sign-problem-free (stoquastic), so the ground state is real and
positive -> a REAL-valued network suffices -> no complex numbers -> MPS is happy.

H = -J * sum_i  sigma^z_i sigma^z_{i+1}   -  h * sum_i sigma^x_i      (periodic)

Knobs to experiment with are all at the top of main().
"""
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import torch
import torch.nn as nn


# ----------------------------------------------------------------------------
# 1) Exact diagonalization (the ground-truth benchmark, feasible for N <= ~16)
# ----------------------------------------------------------------------------
def exact_ground_energy(N, J, h):
    dim = 1 << N
    states = np.arange(dim, dtype=np.int64)
    spins = np.stack([1 - 2 * ((states >> i) & 1) for i in range(N)], axis=1)  # +/-1
    zz = sum(spins[:, i] * spins[:, (i + 1) % N] for i in range(N))
    diag = -J * zz
    rows = [states]; cols = [states]; data = [diag.astype(np.float64)]
    for i in range(N):                       # transverse field flips one spin
        rows.append(states); cols.append(states ^ (1 << i))
        data.append(np.full(dim, -h, dtype=np.float64))
    H = sp.coo_matrix((np.concatenate(data),
                       (np.concatenate(rows), np.concatenate(cols))),
                      shape=(dim, dim)).tocsr()
    e = spla.eigsh(H, k=1, which="SA", return_eigenvectors=False)
    return float(e[0])


# ----------------------------------------------------------------------------
# 2) The neural network ansatz: spins (+/-1) -> f(s) = log psi(s)   [REAL]
# ----------------------------------------------------------------------------
class LogPsi(nn.Module):
    def __init__(self, N, hidden):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(N, hidden), nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, s):           # s: [batch, N] of +/-1 floats
        return self.net(s).squeeze(-1)


# ----------------------------------------------------------------------------
# 3) Metropolis sampler: draw spin configs ~ |psi|^2 (persistent chains)
# ----------------------------------------------------------------------------
@torch.no_grad()
def mcmc(chains, net, n_steps):
    nC, N = chains.shape
    dev = chains.device
    f_cur = net(chains)
    idx = torch.arange(nC, device=dev)
    for _ in range(n_steps):
        j = torch.randint(0, N, (nC,), device=dev)            # site to flip per chain
        prop = chains.clone()
        prop[idx, j] = -prop[idx, j]
        f_prop = net(prop)
        accept = torch.rand(nC, device=dev) < torch.exp(2.0 * (f_prop - f_cur))
        chains[accept] = prop[accept]
        f_cur = torch.where(accept, f_prop, f_cur)
    return chains


# ----------------------------------------------------------------------------
# 4) Local energy  E_loc(s) = sum_s' H_{s,s'} psi(s')/psi(s)
# ----------------------------------------------------------------------------
@torch.no_grad()
def local_energy(chains, net, J, h):
    f0 = net(chains)
    zz = (chains * torch.roll(chains, shifts=-1, dims=1)).sum(dim=1)   # diagonal zz
    E = -J * zz
    for i in range(chains.shape[1]):                                  # off-diag x flips
        flip = chains.clone()
        flip[:, i] = -flip[:, i]
        E = E - h * torch.exp(net(flip) - f0)
    return E


# ----------------------------------------------------------------------------
# 5) Train
# ----------------------------------------------------------------------------
def main():
    # ---- knobs ----
    N        = 10        # number of spins  (exact check feasible up to ~16)
    J        = 1.0
    h        = 1.0       # h/J = 1 is the (hardest) critical point
    hidden   = 32        # network width  -> ~385 parameters total
    n_chains = 1024      # parallel Metropolis walkers / batch size
    mcmc_steps = 4 * N   # decorrelation steps between gradient updates
    lr       = 5e-3
    n_iters  = 800
    device   = "mps" if torch.backends.mps.is_available() else "cpu"
    torch.manual_seed(0)
    # ---------------

    print(f"device={device}  N={N}  h/J={h/J}  hidden={hidden}  chains={n_chains}")
    E_exact = exact_ground_energy(N, J, h)
    print(f"exact ground energy      E/N = {E_exact/N:.6f}   (E = {E_exact:.6f})")

    net = LogPsi(N, hidden).to(device)
    n_params = sum(p.numel() for p in net.parameters())
    print(f"network parameters: {n_params}")
    opt = torch.optim.Adam(net.parameters(), lr=lr)

    chains = (torch.randint(0, 2, (n_chains, N), device=device).float() * 2 - 1)
    chains = mcmc(chains, net, 200)   # thermalize

    t0 = time.time()
    for it in range(1, n_iters + 1):
        chains = mcmc(chains, net, mcmc_steps)
        Eloc = local_energy(chains, net, J, h)        # no grad
        Emean = Eloc.mean()
        f = net(chains)                               # with grad
        loss = 2.0 * ((Eloc - Emean).detach() * f).mean()   # VMC gradient surrogate
        opt.zero_grad(); loss.backward(); opt.step()

        if it % 50 == 0 or it == 1:
            E = Emean.item()
            rel = abs(E - E_exact) / abs(E_exact)
            print(f"iter {it:4d}   E/N = {E/N:+.6f}   exact {E_exact/N:+.6f}   "
                  f"rel.err {rel:.2e}")
    dt = time.time() - t0

    # final estimate averaged over a few fresh sample batches (lower variance)
    with torch.no_grad():
        vals = []
        for _ in range(20):
            chains = mcmc(chains, net, mcmc_steps)
            vals.append(local_energy(chains, net, J, h).mean().item())
    E_final = float(np.mean(vals))
    rel = abs(E_final - E_exact) / abs(E_exact)
    print("-" * 60)
    print(f"NQS    E/N = {E_final/N:+.6f}")
    print(f"exact  E/N = {E_exact/N:+.6f}")
    print(f"relative error = {rel:.3e}   ({rel*100:.3f}%)")
    print(f"trained {n_iters} iters in {dt:.1f}s on {device}")


if __name__ == "__main__":
    main()
