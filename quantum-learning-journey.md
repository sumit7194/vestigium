# Quantum Mechanics Learning Journey — Double Slit, Eraser & Foundations

A running knowledge base from an extended conversation working from the double-slit
"which-path" detector all the way down to the measurement problem and objective-collapse
experiments. Every claim here is grounded in real experiments/papers with real numbers
(the rule for these chats: no textbook cartoons). Downloaded source papers live in `papers/`.

---

## The arc at a glance
1. The which-path detector — it's **information/entanglement**, not the "kick"
2. Field theory & the "wake" question
3. What actually crosses both slits — **coherence width, not wavelength**
4. How a single quantum's wave **spreads**
5. Two interpretations of the same math — **pilot wave vs standard QM**
6. The **polarization quantum eraser**, full story
7. Foundations — quantum properties & **degrees of freedom**
8. The **measurement problem** & four interpretations
9. **Objective collapse** — the one that's testable

---

## 1. The which-path detector: information, not the "kick"

- The "bulb" in the cartoon is **Feynman's** thought experiment; its ancestor is the
  **Einstein–Bohr 1927 Solvay** debate (Einstein's recoiling-slit; Bohr's rebuttal).
- The old story (Feynman/Bohr): a momentum **kick** from the probe smears the fringes.
- **It's not the kick.** Dürr, Nonn & Rempe (Nature, **1998**): an atom interferometer that
  stored which-path info in the atom's **internal state** with essentially **zero momentum
  transfer** — and the interference **still died**. Cause = **entanglement** with the marker,
  not disturbance. (Proposed by **Scully–Englert–Walther 1991**.)
- **2026 (Pan group):** realized Einstein's recoiling-slit at the true quantum limit — fringe
  loss came from photon–atom entanglement, not classical noise. Settled in Bohr's favor.
- **Englert–Greenberger duality:** `V² + D² ≤ 1` — visibility vs which-path distinguishability.
- **Arc:** Einstein (1927, "measure the kick, keep stripes") → Bohr ("the link forbids it") →
  Feynman ("the kick smears it") → 1998 Rempe / 2026 Pan ("it was the link/information all along").

## 2. Field theory & the "wake" question

- **Photon** = excitation of the EM field — no "stiffness" (mass term) → massless → travels at `c`.
  **Electron** = excitation of a massive (Dirac) field — the mass term acts like stiffness → slower than `c`, has rest mass.
- **No wake in vacuum.** A free photon/electron leaves no lingering trail: vacuum is lossless
  (no friction for light), the excitation travels *with* the quantum, and at any fixed point the
  field stirs only as the packet sweeps through, then returns to vacuum.
- **Differences:** the electron's wavepacket **disperses** (spreads) because it's massive; light
  in vacuum does not. A massive field **"buzzes" even at rest** (Compton/rest-mass frequency);
  the EM field at zero frequency just sits flat.
- A **wake** only appears from an **accelerating** charge (radiation), not from free coasting.
- Subtle: a single-photon (Fock) state has `⟨E⟩ = 0` — no classical field wiggle. What travels is
  **energy/probability density**, not a visible oscillation.

## 3. What actually crosses both slits: coherence, not wavelength

The "a wave is naturally wide so it covers both slits" line is the *easy* (classical) half and
hides the real story. Real numbers:

| Experiment | Particle | Wavelength | Slit width / separation | Gap ÷ wavelength |
|---|---|---|---|---|
| Bach et al. 2013 | 600 eV electron | **50 pm** | 62 nm / **272 nm** | ~5,400× |
| Fein et al. 2019 | 25,000 amu molecule | **53 fm** | — / **266 nm** grating | ~5,000,000× |

- The wavelength is **thousands-to-millions of times smaller** than the slit gap. So what must
  span both slits is **not** the wavelength but the **transverse coherence width** — the sideways
  patch over which the wave keeps a definite phase.
- That width is **engineered** (van Cittert–Zernike): a small/distant (point-like) source gives a
  wide, in-step wavefront. Requirement for fringes: **coherence width ≥ slit separation.**
- **How far apart can slits go?** No fixed quantum limit — set by how much coherence you can
  engineer; the deep wall is **decoherence** (any record of the path, anywhere, kills it).

## 4. How a single quantum's wave spreads

- Mechanism = **diffraction**, pure uncertainty principle: a wave squeezed to width `w` fans out by
  `θ ≈ λ / (π w)`. Narrow → spreads fast; wide → slow. In vacuum it spreads **without limit**
  (linearly with distance); only a lens/gravity refocuses it.
- A **single photon genuinely spreads** (the user's "only many photons spread" was wrong):
  single-photon **self-interference** — Taylor **1909** (candle-mile-away, 3-month exposure),
  Grangier–Roger–Aspect **1986** (anticorrelation α ≈ 0.019, ~146σ below the classical bound),
  Jacques **2005**. One indivisible photon, one spread, interfering wavefront.
- **Transverse vs forward:** a photon with definite momentum (laser, far-field starlight) spreads
  only **sideways**, not backward/all-directions. A full sphere happens only for an isolated point
  emitter (single-atom dipole `sin²θ`).
- **Andromeda:** the photon comes *forward*; its transverse wavefront is huge (idealized ≈ distance
  travelled) but the **measurable coherent patch** at Earth is only **meters–hundreds of meters** —
  exactly what stellar interferometry measures (**HBT, Sirius, 10 m baseline, 1956**).
- The wavefront is a **forward-bulging spherical cap** (middle leads), locally flat far away — not a
  flat disc. (An earlier diagram bug drew it concave; corrected.)
- **"Expand + collimate"** = reshape the photon's **amplitude** with lenses: expand widens the mode
  to cover both slits; collimate flattens the wavefront. We shape the wave, not grab a particle.

## 5. Two interpretations of the same math

- **Pilot wave (de Broglie–Bohm):** a real point particle with a **definite path** through one slit,
  carried by a real wave through both. The branch through the un-taken slit = the **"empty wave."**
  Guidance: `v = (1/m)∇S`; equivalently a **quantum potential** `Q = −(ℏ²/2m)(∇²R)/R`. Bohmian
  trajectories computed by **Philippidis, Dewdney & Hiley 1979**; average photon trajectories
  reconstructed by **Kocsis et al., Science 2011** (but those are ensemble flow-lines, equally
  predicted by standard QM). *(The user independently reinvented this picture.)*
- **Standard QM:** the **probability amplitude** goes through both slits; for N particles it lives in
  **3N-dim configuration space** (why the "ripple in real space" picture breaks for entanglement).
  Born rule `|ψ|²`; "each photon interferes only with itself" (Dirac).
- **Honest status:** pilot wave is **empirically identical** to standard QM — an interpretation, not
  a rival theory. Minority view; nonlocal; **no clean relativistic/QFT version**; empty waves
  undetectable. Can't be proven or disproven against the alternatives.

## 6. The polarization quantum eraser — full story

- **"Tagging" = a correlation/entanglement**, not a sticker. You make one of the photon's own
  features (polarization) line up with which slit it took.
- **Malus's law** `I = I₀cos²θ`: unpolarized → first polarizer **50%**; second at 45° → ×½ →
  **25% of original**. (User's "65–70%" was wrong; it's a clean 50% per stage.)
- **Real setup — Walborn et al. 2002 (`papers/`):** Argon pump **351.1 nm** → 1 mm **BBO** → entangled
  **702.2 nm** pairs; double slit **42 cm** away, slits **200 µm** wide/apart; **quarter-wave plates
  at ±45°** over the slits mark paths with **R/L circular** polarization; eraser = polarizer **POL1
  on the entangled partner photon**; interference recovered **only in coincidence**; works under
  **delayed erasure** (erase *after* the screen photon is detected).
- **History:** Scully–Drühl **1982** (original — used **atoms'** internal states, *not* polarization);
  SEW **1991** (micromaser cavities); **Walborn 2002** = first **real double-slit** eraser;
  Hillmer–Kwiat **2007** DIY (linear H/V + analyzer); root law = **Fresnel–Arago ~1818**
  (perpendicular polarizations don't interfere).
- **Mechanism (the crux):** interference lives in the **PATH**; polarization is the **marker**. After
  marking, each polarization is fed by only **one** slit → two single-slit **blobs**, no fringes
  (not two fringe-sets). A 45° filter projects both labels onto a **common axis** → erases path info →
  the still-superposed paths interfere → **fringes return** (in the ~50% that pass).
- **Local eraser** (photon's own polarization; fringes appear directly in surviving light) vs
  **entangled eraser** (Walborn; marker on a partner photon; fringes only in coincidence).
- **Tagging = entanglement, NOT collapse.** Nothing collapses at the slits; the superposition lives to
  the screen. The filter works *because* nothing collapsed. **Delayed erasure proves it** (Walborn's
  own conclusion: a collapse at detection "does not prohibit" recovering the fringes).
- **Partial tag (the dial):** `V = |cos(angle between tags)|`, `D = sin(angle)`, `V² + D² = 1`.
  - H & V (90°) → V = 0 (two blobs); H & H (0°) → V = 1 (full fringes); **H & 45° → V ≈ 0.71** — a
    single **reduced-contrast** pattern, troughs at ~17% of peak (NOT two patches + separate fringes).
  - With an analyzer at angle φ after the slits: transmitted `= [cos²(φ−α)+cos²(φ−β)]/2`,
    `V = 2|cos(φ−α)cos(φ−β)| / [cos²(φ−α)+cos²(φ−β)]`. For H & 45° tags: analyzer at the **bisector
    (22.5°) → V = 1 at 85%** light; at 90° → V = 0 (single-slit blob).
  - Measured continuously by **Schwindt, Kwiat & Englert 1999** (`papers/`): `V² + K² ≤ 1`, hit 0.998.

## 7. Foundations: quantum properties & degrees of freedom

- **Path = position** = the *founding* quantum property — the wavefunction `ψ(x)` *is* the quantum
  state of position (Schrödinger 1926). Polarization/spin are **separate, internal** add-ons.
- **Everything is quantum at bottom**; the classical world emerges via **decoherence**. "In a quantum
  state" is always true; "in a superposition" is **basis-relative** (H = (D+A)/√2).
- **Degrees of freedom** = a **finite, fixed menu per particle**, combined by **tensor product**
  (dimensions **multiply**: N two-state properties = `2ᴺ`, not a cube). Photon = spatial wavefunction
  **+ 2 polarizations**. Frequency/OAM are *features* of the spatial part, not extra properties.
- **Who sets the menu?** Physics, via **mass + spin** (**Wigner 1939**). Photon (massless spin-1) →
  momentum + 2 polarizations; electron (massive spin-½) → momentum + 2 spins. **Spin comes from
  spacetime symmetry** (rotations); **charge/color** from separate **internal gauge** spaces.
- Internal properties don't "decide" position, but can **steer** it via interactions
  (**Stern–Gerlach**: spin → which way it deflects; spin-orbit coupling).
- **Frontier (speculative):** spacetime/position itself may be **emergent from entanglement**
  (holography, ER=EPR, Van Raamsdonk 2010).

## 8. The measurement problem & four interpretations

- Marking **entangles** the photon's path with its own polarization (or another system). Entanglement
  happens whenever an interaction makes the marker's state depend on the path.
- **Why entangle at the slit but "collapse" at the detector?** The detector entangles **too** — but
  with ~10²³ DOF, amplified and radiated irreversibly → **decoherence** makes it an effective collapse.
  Marker (small, reversible) vs detector (huge, irreversible) is a **continuum, not a wall**. "Collapse"
  = entanglement spread so far it can't be undone (Zeh 1970, Zurek).
- **The unsolved residue — why ONE outcome:**

| Interpretation | Why one outcome | Collapse? | Testably different? |
|---|---|---|---|
| Copenhagen | Measurement collapses ψ (postulated) | Yes (added by hand) | No |
| Many-worlds | All happen; you're one branch | No | No |
| Pilot wave | It always had a definite position | No (apparent only) | No |
| Objective collapse | Big systems trigger a real collapse | Yes (new law) | **Yes** |

- Only **objective collapse** makes new, testable predictions.

## 9. Objective collapse — the testable one

- **CSL** parameters: rate **λ** (per nucleon) and length **r_C ≈ 100 nm**. Benchmarks:
  **GRW λ ≈ 10⁻¹⁶ s⁻¹**, **Adler λ ≈ 10⁻⁸**. Collapse rate amplified by **N²** with mass → tiny things
  stay quantum forever, macroscopic things collapse instantly; the testable window is ~10⁴–10¹⁰ amu.
- **Matter-wave interferometry** (Arndt molecules): the most *direct* test, bounds **λ ≳ 10⁻⁶** — still
  ~8–10 orders above GRW. (Toroš & Bassi.)
- **Non-interferometric** are *stronger*: spontaneous **X-ray** emission (IGEX/Majorana, ~10⁻⁸),
  **LISA Pathfinder** (~10⁻⁹), ultracold cantilevers. (Carlesso et al., Nat. Phys. 2022.)
- **Scorecard:** **Diósi–Penrose parameter-free → RULED OUT** (Donadi/Curceanu/Bassi, Nat. Phys. **2021**,
  Gran Sasso, X-rays 10–10⁵ keV, R₀ ≳ 1 Å). **Adler's value → excluded/squeezed.** **GRW value → still
  alive** (~8 orders away).
- **Two knobs:** growing the **marker** maps **decoherence** (settled — Arndt's heated-C₇₀ thermal-photon
  experiment 2004; Haroche cavity QED, Nobel 2012). Growing the **isolated flying particle** tests
  **collapse** — because with a marker present, standard QM and collapse models *agree*, so the marker
  erases the signal. Isolation is the whole game.

---

## Key principles (cheat-sheet)

- **It's information/entanglement, not disturbance** that kills interference.
- **Tagging = entanglement (reversible) ≠ collapse (irreversible).** A reversible label you control can
  be erased; an irreversible record loose in the environment is gone forever.
- **Interference lives in the PATH;** polarization (etc.) is just the marker.
- **Coherence width (engineered), not wavelength, spans both slits.**
- `V = |cos(tag angle)|`, and `V² + D² ≤ 1`.
- **Decoherence = entanglement spread to many irreversible degrees of freedom.**
- **Properties combine by tensor product (`2ᴺ`),** with a fixed menu set by mass + spin (Wigner).

## Papers (in `papers/`)
- `walborn-2002…` — first real double-slit quantum eraser (the H/V-tag experiment).
- `schwindt-kwiat-englert-1999…` — measured the V/D duality dial (the 45° partial-tag question).
- `aspden-2016…` — true single-photon double slit, full dimensions.
- `vetlugin-2024…` — modern single-photon Young setup, tabletop numbers.
- `jacques…` — one photon refuses to split yet interferes with itself.
- `federico-jauslin…` — energy density of a single emitted photon.

## Where we paused / open threads
- **Visual widgets** for the experiments are **pinned** (user to specify exactly what they want).
- **Open frontier:** the measurement problem (why one outcome); objective collapse (being squeezed in
  the lab); spacetime-from-entanglement.
- **Next direction under consideration:** building **small quantum simulations** (start with the
  double-slit/eraser as a direct state-vector calc; possibly Neural Quantum States later).
