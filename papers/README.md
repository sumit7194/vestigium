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

## Classic results used as targets (textbook / not downloaded)

- Kaluza (1921), Klein (1926) — the mass tower `m_n = n/R` reproduced in `kk_projection.py`
- Bekenstein (1973), Hawking (1975) — horizon entropy and temperature
- Jacobson (1995), *Thermodynamics of spacetime* — [gr-qc/9504004](https://arxiv.org/abs/gr-qc/9504004)
- Bennett et al. (1993) — teleportation protocol in `teleport.py`
- Mermin (1990) — the GHZ argument in `bell_game.html`
- Itano et al. (1990) — trapped-ion quantum Zeno data reproduced in `zeno.py`
- Philippidis, Dewdney & Hiley (1979); Kocsis et al. (2011) — the Bohmian fan in `bohmian_fan.py`
- Calabrese & Cardy (2004); Casini & Huerta — entanglement entropy log coefficients used in `log_coefficient_boundary.py`
