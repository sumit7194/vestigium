# Source papers

The PDFs themselves are **not committed** — arXiv postings carry varying licenses and
they are not ours to redistribute. Every source used while building this repository is
listed here by arXiv ID so you can fetch it yourself.

## Double slit, which-path, and the quantum eraser

| Paper | arXiv | Used for |
|---|---|---|
| Walborn et al. (2002), *Double-slit quantum eraser* | [quant-ph/0106078](https://arxiv.org/abs/quant-ph/0106078) | the non-local eraser reproduced in `stage2_bell_eraser.py` and the two-photon mode of `double_slit_app.html` |
| Schwindt, Kwiat & Englert (1999), *Quantitative wave–particle duality* | [quant-ph/9908072](https://arxiv.org/abs/quant-ph/9908072) | the V² + D² ≤ 1 duality relation checked throughout `bench.py` and `decoherence_frames.py` |
| Aspden et al. (2016), *Video recording true single-photon double-slit interference* | [1602.05987](https://arxiv.org/abs/1602.05987) | dot-by-dot Born-sampled fringe accumulation |
| Vetlugin et al. (2024), *Young's double-slit with single photons* | [2401.02351](https://arxiv.org/abs/2401.02351) | modern single-photon interference parameters |
| Jacques et al., *Single-photon wavefront splitting* | [2011.12664](https://arxiv.org/abs/2011.12664) | transverse coherence width vs. slit separation |
| Federico & Jauslin, *Single-photon energy density* | [2403.13622](https://arxiv.org/abs/2403.13622) | photon localization and energy-density subtleties |

## Results probed or reproduced elsewhere in the repo

| Paper | arXiv / journal | Used for |
|---|---|---|
| Dorau & Much (2026), *From quantum relative entropy to the semiclassical Einstein equations* | [2510.24491](https://arxiv.org/abs/2510.24491), PRL | the Longo relative-entropy identity verified in `entropic_hinge.py` / `hinge_mp.py` |
| Barontini (2026), *Testing the problem of time with cold atoms* | [2509.07745](https://arxiv.org/abs/2509.07745), PRR 8 L022047 | the entropic-time construction probed for coarse-graining dependence in `entropic_time.py` |

## Corner entanglement in 3d CFTs

Used for the `a(θ)` work in `qsim/` and the imported result in `corner_function/`. No PDFs held;
the full 52-entry bibliography compiled by the originating workspace is in
[`corner_function/references.md`](../corner_function/references.md).

| Paper | arXiv | Used for |
|---|---|---|
| Bueno, Myers & Witczak-Krempa (2015), *Universality of corner entanglement* | [1505.04804](https://arxiv.org/abs/1505.04804) | σ = π²C_T/24, the smooth-limit theorem |
| Bueno, Myers & Witczak-Krempa (2015), *Universal corner entanglement from twist operators* | [1507.06997](https://arxiv.org/abs/1507.06997) | κ_n = (1/π)∫c_n(t)dt, the strip connection; checked for a κ–C_T bound (none exists) |
| Bueno & Witczak-Krempa (2016), *Bounds on corner entanglement* | [1511.04077](https://arxiv.org/abs/1511.04077) | the BWK16 bound a(θ) ≥ (π²C_T/3)log[1/sin(θ/2)] — the theorem that caught the a(120°) defect |
| Casini, Huerta & Leitao (2009) | [0811.1968](https://arxiv.org/abs/0811.1968) | the SSA + Lorentz inequality (C3) |
| Casini & Huerta (2012), *Positivity, entanglement entropy, and minimal surfaces* | [1203.4007](https://arxiv.org/abs/1203.4007) | reflection positivity / the Hankel conditions (C4) |
| Casini, Huerta, Magán & Pontello (2021), *Is the EMI model a QFT?* | [2105.11464](https://arxiv.org/abs/2105.11464) | the EMI shape is not a CFT corner function |
| Blanco, Casini et al., *Rényi MI inequalities from Rindler positivity* | [1909.03144](https://arxiv.org/abs/1909.03144) | checked for a cross-n inequality (fixed n only) |
| Cuomo, He & Komargodski (2024), *Impurities with a cusp* | [2406.10186](https://arxiv.org/abs/2406.10186) | checked and **not applicable** — cusped line defects, a different object from an entangling corner |

The first six IDs above are cross-checked against
[`corner_function/references.md`](../corner_function/references.md), which the originating
workspace verified. The last two are not in that bibliography: `1909.03144` was confirmed by
fetching the abstract directly; `2406.10186` comes from a search result and is **not**
independently verified here.

## Classic results used as targets (textbook / not downloaded)

- Kaluza (1921), Klein (1926) — the mass tower `m_n = n/R` reproduced in `kk_projection.py`
- Bekenstein (1973), Hawking (1975) — horizon entropy and temperature
- Jacobson (1995), *Thermodynamics of spacetime* — [gr-qc/9504004](https://arxiv.org/abs/gr-qc/9504004)
- Bennett et al. (1993) — teleportation protocol in `teleport.py`
- Mermin (1990) — the GHZ argument in `bell_game.html`
- Itano et al. (1990) — trapped-ion quantum Zeno data reproduced in `zeno.py`
- Philippidis, Dewdney & Hiley (1979); Kocsis et al. (2011) — the Bohmian fan in `bohmian_fan.py`
- Calabrese & Cardy (2004); Casini & Huerta — entanglement entropy log coefficients used in `log_coefficient_boundary.py`
