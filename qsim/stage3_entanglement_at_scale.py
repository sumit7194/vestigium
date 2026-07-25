"""
Stage 3: entanglement at scale -- the neural network holds it, and it peaks at the
quantum critical point.

We reuse the symmetry-aware CNN Neural Quantum State (from ../sims/nqs_cnn.py) to find
the TFIM ground state, then extract the *entanglement entropy* of half the chain by
SVD of the amplitude tensor (the Schmidt decomposition).  This is the genuinely
quantum, non-factorizable content -- the same quantity that was 1 bit for the Bell
pair in Stage 2, now for a whole interacting chain.

Two results:
  A) sweep the field h: entanglement entropy PEAKS at the critical point h/J=1.
     (low in both gapped phases, maximal where the phase transition happens.)
  B) scale N: in a gapped phase entanglement SATURATES (the "area law" -- why small
     networks can compress these states); at criticality it GROWS (the hard frontier).

NN values are checked against exact diagonalization throughout.
"""
import copy
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sims"))
from nqs_tfim import mcmc, local_energy            # noqa: E402
from nqs_cnn import TransInvCNN                     # noqa: E402


def all_configs(N):
    idx = np.arange(1 << N, dtype=np.int64)
    bits = ((idx[:, None] >> np.arange(N)) & 1).astype(np.float32)
    return 1.0 - 2.0 * bits                         # [2^N, N] of +/-1


def entropy_bits(psi, N):
    half = N // 2
    M = psi.reshape(1 << half, 1 << (N - half))
    sv = np.linalg.svd(M, compute_uv=False)
    lam = sv ** 2
    lam = lam[lam > 1e-14]
    lam = lam / lam.sum()
    return float(-np.sum(lam * np.log2(lam)))


def exact_psi(N, J, h):
    dim = 1 << N
    st = np.arange(dim, dtype=np.int64)
    sp_ = np.stack([1 - 2 * ((st >> i) & 1) for i in range(N)], axis=1)
    zz = sum(sp_[:, i] * sp_[:, (i + 1) % N] for i in range(N))
    rows, cols, data = [st], [st], [(-J * zz).astype(float)]
    for i in range(N):
        rows.append(st); cols.append(st ^ (1 << i)); data.append(np.full(dim, -h))
    H = sp.coo_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(dim, dim)).tocsr()
    _, v = spla.eigsh(H, k=1, which="SA")
    return v[:, 0]


def nn_psi(net, N, device, chunk=1 << 13):
    cfg = all_configs(N)
    out = []
    with torch.no_grad():
        for i in range(0, cfg.shape[0], chunk):
            out.append(net(torch.tensor(cfg[i:i + chunk], device=device)).cpu().numpy())
    f = np.concatenate(out); f = f - f.max()
    psi = np.exp(f); psi /= np.linalg.norm(psi)
    return psi


def train(net, chains, N, J, h, iters=600, lr=5e-3):
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    for _ in range(iters):
        chains = mcmc(chains, net, 4 * N)
        El = local_energy(chains, net, J, h); Em = El.mean()
        f = net(chains); loss = 2.0 * ((El - Em).detach() * f).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return net, chains


def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    J, N = 1.0, 14
    torch.manual_seed(0)
    hs = [1.6, 1.4, 1.2, 1.1, 1.0, 0.9, 0.8, 0.6, 0.4]   # high->low (warm start)

    print(f"device={device}  N={N}  (entanglement entropy of half the chain, in bits)")
    print(f"{'h/J':>5} | {'S_NN':>7} {'S_exact':>8}")
    net = TransInvCNN(16, 5, 3).to(device)
    chains = torch.randint(0, 2, (1024, N), device=device).float() * 2 - 1
    chains = mcmc(chains, net, 200)
    rows, snaps = [], {}
    t0 = time.time()
    for h in hs:
        net, chains = train(net, chains, N, J, h)
        s_nn = entropy_bits(nn_psi(net, N, device), N)
        s_ex = entropy_bits(exact_psi(N, J, h), N)
        print(f"{h:5.2f} | {s_nn:7.3f} {s_ex:8.3f}")
        rows.append((h, s_nn, s_ex))
        if abs(h - 1.0) < 1e-9 or abs(h - 1.6) < 1e-9:
            snaps[round(h, 2)] = copy.deepcopy(net)
    print(f"(field sweep trained in {time.time()-t0:.1f}s)\n")

    # Part B: exact entanglement scaling, critical vs gapped, + NN spot-checks at N=14
    Ns = [6, 8, 10, 12, 14, 16, 18]
    crit = [(n, entropy_bits(exact_psi(n, J, 1.0), n)) for n in Ns]
    gap = [(n, entropy_bits(exact_psi(n, J, 1.6), n)) for n in Ns]
    sc14 = entropy_bits(nn_psi(snaps[1.0], 14, device), 14)
    sg14 = entropy_bits(nn_psi(snaps[1.6], 14, device), 14)
    print("Part B (area law vs critical growth, exact):")
    print(f"  critical h=1.0:  S(N) = {[round(s,3) for _,s in crit]}   (grows)")
    print(f"  gapped   h=1.6:  S(N) = {[round(s,3) for _,s in gap]}   (saturates -> area law)")
    print(f"  NN spot-check at N=14:  critical {sc14:.3f}  gapped {sg14:.3f}")

    a = np.array(rows)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].plot(a[:, 0], a[:, 2], "k-", lw=2, label="exact")
    ax[0].plot(a[:, 0], a[:, 1], "o", color="tab:red", ms=7, label="neural network")
    ax[0].axvline(1.0, ls="--", color="gray")
    ax[0].set_xlabel("field  h / J"); ax[0].set_ylabel("entanglement entropy (bits)")
    ax[0].set_title(f"Entanglement peaks at the critical point (N={N})")
    ax[0].legend(); ax[0].grid(alpha=0.3)

    cn = np.array(crit); gn = np.array(gap)
    ax[1].plot(cn[:, 0], cn[:, 1], "-o", color="tab:red", label="critical h=1.0 (grows)")
    ax[1].plot(gn[:, 0], gn[:, 1], "-s", color="tab:blue", label="gapped h=1.6 (area law)")
    ax[1].plot([14], [sc14], "*", color="black", ms=14, label="NN check (N=14)")
    ax[1].plot([14], [sg14], "*", color="black", ms=14)
    ax[1].set_xlabel("chain length N"); ax[1].set_ylabel("entanglement entropy (bits)")
    ax[1].set_title("Why it's compressible: area law vs critical growth")
    ax[1].legend(); ax[1].grid(alpha=0.3)
    fig.suptitle("Stage 3 - a neural network holds entanglement, and it peaks at criticality")
    fig.tight_layout()
    fig.savefig("stage3_entanglement_at_scale.png", dpi=130)
    print("\nsaved plot -> qsim/stage3_entanglement_at_scale.png")


if __name__ == "__main__":
    main()
