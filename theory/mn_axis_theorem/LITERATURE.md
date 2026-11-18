# Literature check: non-integrability of geodesics in Manko–Novikov (MN) spacetimes

- Date: 2026-11-18
- Written by: Claude Opus 5.5 (model id claude-opus-5-5), acting as a literature-search subagent.
- Method. Bibliographic data were checked against Crossref (api.crossref.org) or the arXiv API for every item marked "verified". Theorem statements were read in full text where I could open it. Full text read (relevant sections): Morales-Ruiz & Ramis I (MAA 2001, publisher PDF); Morales-Ruiz–Ramis–Simó 2007 (Numdam PDF); Kimura 1969 (Funkcialaj Ekvacioj archive PDF; tables read from page images); Kozlov 1983 survey (English translation, author's homepage PDF); Gair–Li–Mandel 2008, Lukes-Gerakopoulos–Apostolatos–Contopoulos 2010, Bambi–Barausse 2011 (equations pulled from the ar5iv LaTeX); Maciejewski–Przybylska–Stachowiak 2013 (ar5iv); Polcar–Semerák 2019 (ar5iv); Levin–Perez-Giz 2009 I (ar5iv); Xue 2020/21 (arXiv HTML); Lima Junior–Crispino–Higuchi 2020 (ar5iv); Morales-Ruiz–Peris 1999 (abstract and theorem list from PDF); Cresson 2005 (arXiv PDF); Singer 1991 (author's PDF, abstract and introduction); Seiss (arXiv PDF, introduction). Everything else comes only from an abstract, a publisher landing page, or a search snippet, and says so. "NOT VERIFIED" means I did not check that claim against a source I opened.
- I ran no computations. The one hand check (A.8) is labelled as mine.
- Quotations are kept short. Equation and theorem numbers refer to the source named.

---

## PART A. MN and related spacetimes: what is proven and what is numerical

### A.1 Manko & Novikov 1992: the metric

**Citation (verified, Crossref):** V. S. Manko, I. D. Novikov, "Generalizations of the Kerr and Kerr–Newman metrics possessing an arbitrary set of mass-multipole moments", *Class. Quantum Grav.* **9**(11), 2477–2487 (1992), doi:10.1088/0264-9381/9/11/013.
The original is paywalled and I did **not** open it, so every formula below is copied from reprints, and each is labelled with its source.

**Line element** (Gair–Li–Mandel 2008, Eq. 2; also Bambi–Barausse 2011, Eq. A1):
```
ds^2 = -f (dt - ω dφ)^2 + k^2 f^{-1} e^{2γ} (x^2 - y^2) ( dx^2/(x^2-1) + dy^2/(1-y^2) ) + k^2 f^{-1} (x^2-1)(1-y^2) dφ^2
ρ = k sqrt((x^2-1)(1-y^2)),   z = k x y
```

**General α_n form.** The source is Bambi & Barausse, "Constraining the quadrupole moment of stellar-mass black-hole candidates with the continuum fitting method", ApJ 731, 121 (2011), doi:10.1088/0004-637X/731/2/121, arXiv:1012.2007, Appendix A, Eqs. A2–A12, copied from their LaTeX:
```
f      = e^{2ψ} A/B                                             (A2)
ω      = 2k e^{-2ψ} C A^{-1} - 4kα (1-α^2)^{-1}                 (A3)
e^{2γ} = e^{2γ'} A (x^2-1)^{-1} (1-α^2)^{-2}                    (A4)
ψ      = Σ_{n=1}^{∞} α_n P_n / R^{n+1}                          (A5)
γ'     = ½ ln[(x^2-1)/(x^2-y^2)]
         + Σ_{m,n=1}^{∞} (m+1)(n+1) α_m α_n / ((m+n+2) R^{m+n+2}) (P_{m+1}P_{n+1} - P_m P_n)
         + Σ_{n=1}^{∞} α_n ( (-1)^{n+1} - 1 + Σ_{k=0}^{n} (x - y + (-1)^{n-k}(x+y)) P_k / R^{k+1} )   (A6)
A      = (x^2-1)(1+ab)^2 - (1-y^2)(b-a)^2                       (A7)
B      = [x+1+(x-1)ab]^2 + [(1+y)a + (1-y)b]^2                  (A8)
C      = (x^2-1)(1+ab)[b-a-y(a+b)] + (1-y^2)(b-a)[1+ab+x(1-ab)] (A9)
a(x,y) = -α exp[ Σ_{n=1}^{∞} 2α_n ( 1 - Σ_{k=0}^{n} (x-y) P_k / R^{k+1} ) ]                 (A10)
b(x,y) =  α exp[ Σ_{n=1}^{∞} 2α_n ( (-1)^n + Σ_{k=0}^{n} (-1)^{n-k+1} (x+y) P_k / R^{k+1} ) ]   (A11)
R = sqrt(x^2 + y^2 - 1),  P_n = P_n(xy/R),  P_n(x) = (1/(2^n n!)) d^n/dx^n (x^2-1)^n   (A12)
```
Bambi–Barausse also say: Kerr is recovered for α ≠ 0 with all α_n = 0; Schwarzschild for α = α_n = 0; the static Weyl metric for α = 0 with α_n ≠ 0; and α_1 can be set to 0 by a translation along the axis.

**Quadrupole-only subclass** (α_2 = β, all other α_n = 0), from Gair–Li–Mandel 2008, Eqs. 3a–3l, as LaTeX:
```
ψ  = β R^{-3} P_2
γ' = ½ ln[(x^2-1)/(x^2-y^2)] + (9β^2/(6R^6)) (P_3 P_3 - P_2 P_2) + β Σ_{ℓ=0}^{2} ( (x-y+(-1)^{2-ℓ}(x+y)) P_ℓ / R^{ℓ+1} - 2 )    <- as printed in GLM
a  = -α exp( -2β ( -1 + Σ_{ℓ=0}^{2} (x-y) P_ℓ / R^{ℓ+1} ) )
b  =  α exp(  2β (  1 + Σ_{ℓ=0}^{2} (-1)^{3-ℓ} (x+y) P_ℓ / R^{ℓ+1} ) )
α = (-1 + sqrt(1-χ^2))/χ,  k = M (1-α^2)/(1+α^2),  β = q M^3/k^3,  χ = S_1/M^2,  q = -(M_2 - M_2^Kerr)/M^3
```
Lukes-Gerakopoulos et al. 2010 (Eqs. 5a–5l) print the same functions with the quadratic coefficient written as 3β²/(2R⁶) (which equals 9/6), and with the −2 **outside** the sum: `β(−2 + Σ_{ℓ=0}^{2} …)`. Setting n = 2 in Bambi–Barausse (A6), (A10) and (A11) reproduces exactly the LG2010/GLM a and b and the LG2010 γ′.

**Typos and errata reported in the literature:**
- Gair–Li–Mandel (Sec. II) "correct a typo in Eq. (14)" of MN1992, following a thesis by Hua. That typo is in the **multipole-moment** formulas (their Eq. 4), not in the metric functions.
- Lukes-Gerakopoulos et al. 2010, Sec. II.1: "the −2 term in Eq. (5h) has been moved outside the sum (c.f., Eq. (3h) of Gair08) so as to avoid any confusion". Read literally, GLM's Eq. 3h puts −2 inside the ℓ-sum, which would give −6β. The −2 belongs outside: once per n, as (−1)^{n+1} − 1 = −2 for n = 2.
- Bambi–Barausse 2011, App. A: "Eqs. (A6), (A10) and (A11) correct a few typos in the original Manko-Novikov metric", citing Brink 2008 (PRD 78, 102002) and Fang 2007 (thesis). I did **not** find the specific corrections stated in the Brink 2008 text I searched. Which signs or terms were wrong in MN1992 is **NOT VERIFIED**.

**Claim, method, status:** an exact stationary axisymmetric vacuum solution, nonlinear superposition of Kerr with a static Weyl field. This is an exact solution, not a dynamics result.

### A.2 Gair, Li, Mandel 2008

**Citation (verified):** J. R. Gair, C. Li, I. Mandel, "Observable properties of orbits in exact bumpy spacetimes", *Phys. Rev. D* **77**, 024035 (2008), doi:10.1103/PhysRevD.77.024035, arXiv:0708.0628.
- **Claim:** most geodesics have an approximate fourth integral (they look triply periodic). In some oblate MN spacetimes there is an inner bound region where orbits are "apparently ergodic".
- **Method:** numerical. Bulirsch–Stoer integration, Poincaré maps of ρ vs ρ̇ at fixed z, and Fourier spectra. The authors themselves say there is no strict proof, and they raise numerical instability as an alternative explanation.
- **Parameters:** the ergodic example is χ = 0.9, q = 0.95, E = 0.95, L_z = 3M. Ergodic regions are reported for χ ≠ 0 and q > 0. Orbits look regular for χ = 0, or for q < 0.
- **Status: NUMERICAL.**

### A.3 Apostolatos, Lukes-Gerakopoulos, Contopoulos

- **(verified)** T. A. Apostolatos, G. Lukes-Gerakopoulos, G. Contopoulos, "How to observe a non-Kerr spacetime using gravitational waves", *Phys. Rev. Lett.* **103**, 111101 (2009), doi:10.1103/PhysRevLett.103.111101. I did not open the abstract. The content is assumed to match the 2010 PRD, which is **NOT VERIFIED**.
- **(verified)** G. Lukes-Gerakopoulos, T. A. Apostolatos, G. Contopoulos, "Observable signature of a background deviating from the Kerr metric", *Phys. Rev. D* **81**, 124005 (2010), doi:10.1103/PhysRevD.81.124005, arXiv:1003.3120. **Claim:** the MN geodesic system is "slightly nonintegrable". There are Birkhoff chains of islands at resonances, with plateaus in the frequency ratio during inspiral. **Method:** numerical rotation numbers and surfaces of section, with a 6th-order Runge–Kutta integrator and ΔL/L ≲ 1e-10. **Parameters:** χ = 0.9, q = 0.95, E = 0.95, L_z = 3M (and L_z = 2.995M). The theoretical basis is Poincaré–Birkhoff and KAM, invoked rather than proved. **Status: NUMERICAL.**
- **(verified)** G. Contopoulos, G. Lukes-Gerakopoulos, T. A. Apostolatos, "Orbits in a non-Kerr dynamical system", *Int. J. Bifurcation Chaos* **21**(8), 2261–2277 (2011), doi:10.1142/S0218127411029768, arXiv:1108.5057. I did not open the abstract or full text. The content (numerical, MN) is **NOT VERIFIED**.

### A.4 Brink: Killing tensors in stationary axisymmetric vacuum (SAV) spacetimes

All verified via Crossref and the arXiv API. I read the abstracts only.
- I: "Spacetime encodings. I. A spacetime reconstruction problem", PRD **78**, 102001 (2008), arXiv:0807.1178. Programmatic; no claims about Killing tensors.
- II: "Spacetime encodings. II. Pictures of integrability", PRD **78**, 102002 (2008), arXiv:0807.1179. Gives visual (numerical) evidence, in MN and Zipoy–Voorhees, that a quartic-in-momentum fourth constant "might" exist in SAV spacetimes. **Heuristic/numerical; no theorem.**
- III: "Spacetime encodings. III. Second order Killing tensors", PRD **81**, 022001 (2010), arXiv:0911.1589. Analytic. Argues that requiring a second-order Killing tensor is very restrictive: the consistency conditions reduce the field equations to a 2nd-order ODE, leaving essentially Carter's separable type-D cases. Per the abstract this is an analytic argument. Whether it is a complete classification theorem is **NOT VERIFIED**.
- IV: "Spacetime encodings. IV. The relationship between Weyl curvature and Killing tensors in stationary axisymmetric vacuum spacetimes", PRD **81**, 022002 (2010), arXiv:0911.1595. Proposes an algebraic **test** for a fourth-order Killing tensor. No existence or nonexistence result is stated.
- "Formal solution of the fourth order Killing equations for stationary axisymmetric vacuum spacetimes", PRD **84**, 104015 (2011), arXiv:0911.4161. Gives a closed-form expression that is an exact solution **only if** a certain second integral vanishes; the abstract says it is unclear which SAV spacetimes satisfy this. **No existence or nonexistence theorem for MN.**
- **Bottom line:** Brink proves no nonexistence theorem for higher-order Killing tensors in MN.

### A.5 Zipoy–Voorhees (ZV) and related Killing-tensor results

- **Kruglikov & Matveev (verified):** B. S. Kruglikov, V. S. Matveev, "Nonexistence of an integral of the 6th degree in momenta for the Zipoy-Voorhees metric", *Phys. Rev. D* **85**, 124057 (2012), arXiv:1111.4690. For **δ = 2**, there is no nontrivial integral polynomial in momenta of degree ≤ 6 (abstract: "less than 7"). **PROVEN, computer-algebra based, δ = 2 only, polynomial integrals of bounded degree only.**
- **Lukes-Gerakopoulos (verified):** "Nonintegrability of the Zipoy-Voorhees metric", *Phys. Rev. D* **86**, 044013 (2012). **NUMERICAL** (I opened only the title and Crossref record).
- **Maciejewski, Przybylska, Stachowiak (verified):** "Nonexistence of the final first integral in the Zipoy-Voorhees space-time", *Phys. Rev. D* **88**, 064003 (2013), arXiv:1302.4234. Read on ar5iv.
  - **Theorem** (Theorem 3, Sec. VI): "There does not exist an additional, meromorphic first integral of the geodesic motion in the Zipoy-Voorhees metric (1)". Metric (1) is the case **δ = 2** only.
  - **Other δ:** Sec. V says the method needs a separate Kovacic run for each δ. "we have verified that δ=1/2 is also nonintegrable" (Maple, numeric parameter values). General δ is **not** covered.
  - **Particular solution:** a particle "moving along a straight line, through the center in the equatorial plane": y = 0, p₃ = 0 (prolate coordinates; the solution involves only x and p₁). For the exceptional energy levels μ = 0, μ² = 1, μ² = 5 they use other solutions with p₃ = 1 (Sec. IV.2).
  - **Order:** the **first-order** NVE was enough. The NVE is a 2×2 system in the (y, p₂) directions (Eq. 13). After a change of dependent variable (Eq. 14) and taking x as the independent variable, it becomes ξ″ = r(x)ξ with **rational** r (Eqs. 15–17). Poles are at x = −1, 0, 1, (μ−1)/(μ+1), (μ+1)/(μ−1), all of order 2. r has order 4 at ∞. Non-solvability comes from **Kovacic's algorithm** (cases 1–3 excluded by exponent arguments; Eqs. 22–25). Kimura's theorem is not used.
  - **Class excluded:** first integrals "meromorphic in the phase-space variables". These are the canonical variables (q₀, q₁, q₂, q₃) = (t, x, y, φ) with conjugate momenta, which makes them prolate coordinates. They state Morales–Ramis as their Theorem 1 ("completely integrable with meromorphic first integrals … identity component … is Abelian").
  - **Points at infinity:** x = ∞ is treated as a singular point of the rational NVE, with its exponents entering the Kovacic degree count. They justify passing from time u to x by saying it "does not change the identity component" only if x(u) is a finite cover (citing Singer). *My reading, not stated by them:* the rational-coefficient equation they analyse is Fuchsian (double poles, order 4 at ∞). By the Morales–Ramis remark quoted in B.1 below, the Galois groups over Γ, Γ̄ and Γ̄′ then coincide, so the result excludes integrals meromorphic near the curve, with no growth condition at infinity.
  - **Status: PROVEN (rigorous, computer-assisted Kovacic), δ = 2; δ = 1/2 claimed.**
- **Comment and reply:** "Comment on 'Nonexistence of the final first integral in the Zipoy-Voorhees space-time'", *Phys. Rev. D* **88**, 108501 (2013), arXiv:1310.1097. Crossref lists G. Lukes-Gerakopoulos as sole author; the arXiv listing shows Lukes-Gerakopoulos, Maciejewski, Przybylska and Stachowiak. The comment says the disagreement with the 2012 numerics is "due to different choice of coordinates", not numerical accuracy. The author list conflict is unresolved and the reply text is **NOT VERIFIED**.
- **Vollmer:** *The prompt's dating is off.* The reducibility paper is **2015**: A. Vollmer, "Reducibility of valence-3 Killing tensors in Weyl's class of stationary and axially symmetric spacetimes", *Phys. Rev. D* **92**, 084036 (2015), arXiv:1506.06926 (verified). Per the abstract, for static axisymmetric vacuum (Weyl class) metrics every valence-3 Killing tensor is reducible (generated by Killing vectors and quadratic Killing tensors); for ZV, by Killing vectors and the metric. **PROVEN.** The 2017 paper is a different one: A. Vollmer, "Killing tensors in stationary and axially symmetric space-times", *J. Geom. Phys.* **115**, 28–36 (2017), arXiv:1602.08968 (verified). It uses computer algebra to show there are no nontrivial Killing tensors for Tomimatsu–Sato up to valence 7, the C-metric up to valence 9, and ZV up to valence 11 (abstract only; which TS and ZV parameters is **NOT VERIFIED**). **PROVEN, bounded valence.**
- **Markakis (verified):** C. Markakis, "Constants of motion in stationary axisymmetric gravitational fields", *MNRAS* **441**(4), 2974–2985 (2014), arXiv:1202.5228. *This contradicts the prompt's framing:* per the abstract, the nonexistence of quartic constants (his second theorem) is proven for the **Newtonian analogue** (stationary axisymmetric vacuum potentials), not for GR geodesics.

### A.6 Rigorous non-integrability results for geodesics (or related) in GR

| Item | Verified citation | What / method | Status |
|---|---|---|---|
| Moeckel 1992 | R. Moeckel, "A nonintegrable model in general relativity", *Commun. Math. Phys.* **150**(2), 415–430 (1992), doi:10.1007/BF02096667 | From the abstract (search snippet): the geodesic flow of a perturbation of Schwarzschild, a relativistic analogue of **Hill's problem**, has a **chaotic invariant set**. Method and exact theorem **NOT VERIFIED**. No Majumdar–Papapetrou content was found. | Rigorous (per abstract) |
| Bombelli & Calzetta 1992 | "Chaos around a black hole", *Class. Quantum Grav.* **9**(12), 2573–2599, doi:10.1088/0264-9381/9/12/004 | Abstract not opened: content **NOT VERIFIED**. Calzetta also has "Homoclinic chaos around a black hole", CQG **10**, S203 (1993). | NOT VERIFIED |
| Letelier & Vieira 1997 | "Chaos in black holes surrounded by gravitational waves", *CQG* **14**(5), 1249–1257, gr-qc/9706025 | Schwarzschild plus a special class of gravitational waves; **Melnikov** method with an explicit homoclinic orbit; "simple graphical checks". | Perturbative Melnikov; first order in ε; graphical zeros |
| Vieira & Letelier 1996 | "Chaos around a Hénon-Heiles-inspired exact perturbation of a black hole", *PRL* **76**, 1409 (erratum 4098) | Abstract not opened; numerical sections assumed, **NOT VERIFIED**. The "core–halo" paper is likely Letelier & Vieira, "Chaos and rotating black holes with halos", *PRD* **56**, 8095 (1997), or Vieira & Letelier, *ApJ* **513**, 383 (1999, core–shell). Which one the prompt meant is unclear. | NOT VERIFIED |
| Santoprete & Cicogna 2002 | "Chaos in black holes surrounded by electromagnetic fields", *GRG* **34**(7), 1107–1119, nlin/0110046 | Charged particle, Schwarzschild plus uniform E and B fields; Poincaré–Melnikov. The abstract says they "prove" chaos. | Rigorous within first-order Melnikov (claimed) |
| Polcar & Semerák 2019 (**not** "Polcar, Suková, Semerák") | "Free motion around black holes with discs or rings: Between integrability and chaos. VI. The Melnikov method", *PRD* **100**, 103013, arXiv:1911.09790 | The main analysis uses the **pseudo-Newtonian Nowak–Wagoner** potential; it also covers Schwarzschild plus Bach–Weyl ring or inverted Morgan–Morgan disc, and extreme RN plus MP ring. Holmes–Marsden style reduction with J_ϑ = L − ℓ_φ. Melnikov integrals evaluated **numerically** at specific parameters. Claims simple zeros "proves that the homoclinic orbit really breaks up" to first order; **no non-integrability theorem**. Paper V is ApJ 877:16 (2019) (search snippet; **NOT VERIFIED**). | Semi-rigorous / numerical |
| Sota, Suzuki, Maeda 1996 | "Chaos in static axisymmetric spacetimes: I. Vacuum case", *CQG* **13**(5), 1241–1260, gr-qc/9505036 | Weyl-curvature local-instability criterion plus homoclinic tangle; "at least qualitatively". | Heuristic/numerical |
| Guéron & Letelier 2002 | "Geodesic chaos around quadrupolar deformed centers of attraction", *PRE* **66**, 046611 | Abstract not opened. | NOT VERIFIED (numerical assumed) |
| Han 2008 | not identified | No matching record found. | NOT VERIFIED |
| Morales-Ruiz & Raposo 2023 | "A note on the geodesic deviation equation for null geodesics in the Schwarzschild black-hole", arXiv:2308.07098 (no journal ref found) | Relates Morales–Ramis integrability to Galois integrability of the geodesic-deviation (Jacobi) equation; null geodesics in Schwarzschild, which is integrable. | Rigorous, integrable case |
| Ramond 2026 | "Quadrupolar tidal effects destroy the integrability of black hole geodesics: analytic proof and numerical evidence of chaos", arXiv:2607.27129 (preprint, 29 Jul 2026) | Shows no **deformation of the Carter constant** stays conserved for a tidally deformed non-spinning body in Kerr, at leading order. That is not a Morales–Ramis or Melnikov theorem (the search snippet says a global Morales–Ramis/Melnikov proof is still open). | Partial analytic + numerical; unrefereed |
| MN, Erez–Rosen, q-metric, Curzon, Tomimatsu–Sato, Johannsen–Psaltis, Bonnor, double BH (Ziglin/Morales–Ramis) | — | **Several searches found no rigorous Morales–Ramis, Ziglin, Painlevé or Melnikov non-integrability theorem for any of these.** The only Morales–Ramis result for a vacuum Weyl/SAV geodesic flow I found is ZV (A.5). | None found |

### A.7 Kerr geodesic facts

- **Homoclinic orbits (verified):** J. Levin, G. Perez-Giz, "Homoclinic orbits around spinning black holes. I. Exact solution for the Kerr separatrix", *PRD* **79**, 124013 (2009), arXiv:0811.3814; and G. Perez-Giz, J. Levin, "… II. The phase space portrait", *PRD* **79**, 124014 (2009), arXiv:0811.3815. Paper I gives the **equatorial** homoclinic orbits in closed form, parametrized by r (τ(r), t(r), φ(r), Eqs. 26a–c), in one-to-one correspondence with unstable circular orbits with E_u < 1 (Sec. II.4). Inclined orbits are explicitly deferred: "(We leave for a future work the non-equatorial case.)" I found **no** source here giving closed-form **inclined** Kerr homoclinic orbits (**NOT VERIFIED** either way). Paper II gives exact actions and frequencies (abstract).
- **(verified, abstracts not opened)** R. O'Shaughnessy, "Transition from inspiral to plunge for eccentric equatorial Kerr orbits", *PRD* **67**, 044004 (2003). K. Glampedakis, D. Kennefick, "Zoom and whirl: …", *PRD* **66**, 044002 (2002).
- **Isofrequency pairing (verified):** N. Warburton, L. Barack, N. Sago, "Isofrequency pairing of geodesic orbits in Kerr geometry", *PRD* **87**, 084012 (2013), arXiv:1301.3918. Abstract: in a strong-field region, distinct orbits share the same frequencies, so the map from (E, L, Q) to the frequencies is not injective. *My inference, not stated in the abstract:* the frequency map is therefore degenerate (vanishing Jacobian) somewhere, which is why Kolmogorov non-degeneracy cannot hold globally.
- **KAM for Kerr:** J. Xue, "KAM and geodesic dynamics of blackholes", arXiv:2012.03046; published as *Ann. Appl. Math.* **37**(3), 291–336 (2021), doi:10.4208/aam.oa-2021-0002 (Crossref). Sec. 1.2 says "we do not expect that KAM nondegeneracy condition holds globally" for Kerr. For Schwarzschild, Theorem 3.2 proves a **twist** condition (not KAM non-degeneracy) on an open set, anchored at one parameter value checked numerically (E = 0.97, L_z = 3). For Kerr, Theorem 4.4 asserts an open set of (a, M, E) where twist holds, but Sec. 4.3.1 relies on plots (a = 0.8, E = 0.96 and 0.92) and notes a critical point of ν. **I found no paper with a proof that the Kerr frequency map is (iso-energetically) non-degenerate on an open set.** Status: **not proven in the literature found.**
- **(verified)** W. Schmidt, "Celestial mechanics in Kerr spacetime", *CQG* **19**(10), 2743–2764 (2002), gr-qc/0202090. Action–angle variables and fundamental frequencies as quadratures, evaluated numerically. No non-degeneracy claim (abstract).
- **(verified)** Y. Mino, "Perturbative approach to an orbital evolution around a supermassive black hole", *PRD* **67**, 084027 (2003). Mino time (abstract not opened).

### A.8 Geodesic deviation along the symmetry axis

- **I found no general closed-form formula** in the literature expressing on-axis transverse deviation through f(z) = −g_tt on the axis, or through the Ernst potential, for a general SAV spacetime.
- Closest source (verified): H. C. D. Lima Junior, L. C. B. Crispino, A. Higuchi, "On-axis tidal forces in Kerr spacetime", *Eur. Phys. J. Plus* **135**(3) (2020) (article number not shown in Crossref; NOT VERIFIED), doi:10.1140/epjp/s13360-020-00342-7, arXiv:2003.09506. Kerr only, written in Boyer–Lindquist r: K_{1̂1̂} = K_{3̂3̂} = Mr(r²−3a²)/(r²+a²)³ (Eqs. 34, 36), K_{2̂2̂} = −2Mr(r²−3a²)/(r²+a²)³ (Eq. 35), and D²η/Dτ² = −K η (Eq. 33). They use neither Ψ₂ nor metric functions.
- *My hand check, not from the literature:* on the Kerr axis, f = 1 − 2Mr/(r²+a²) and dz = dr. Then f″(r) = −4Mr(r²−3a²)/(r²+a²)³ = −4K_{1̂1̂}, so the transverse equation is d²η/dτ² = (1/4) f″(z) η, independent of E. This agrees with the formula in the prompt with μ = 1 for Kerr. Kerr is type D and the axis is a principal direction, so the boost invariance this uses may fail for MN. A general SAV derivation remains to be done.
- Related: Brink IV (Weyl curvature and Killing tensors); Taub–NUT on-axis deviation (arXiv:2205.00166, not opened).

---

## PART B. Exact statements of the mathematical theorems

### B.1 Morales–Ramis

**Citations (verified):** J. J. Morales-Ruiz, J. P. Ramis, "Galoisian obstructions to integrability of Hamiltonian systems", *Methods Appl. Anal.* **8**(1), 33–96 (2001), doi:10.4310/MAA.2001.v8.n1.a3 (read). "… II", same issue, 97–112, doi:10.4310/MAA.2001.v8.n1.a4 (not opened). Book: J. J. Morales-Ruiz, *Differential Galois Theory and Non-Integrability of Hamiltonian Systems*, Birkhäuser (Progress in Math. 179), 1999; Crossref lists chapter DOIs under 10.1007/978-3-0348-0723-4 (e.g. Ch. "Non-integrability Theorems", pp. 65–95). **I did not open the book, so its theorem numbering is NOT VERIFIED.** The statements below are from MR I.

Setting (MR I, §5.2, p. 72): "Let Γ be the abstract Riemann surface defined by a non stationary connected integral curve i(Γ) of an analytic Hamiltonian system X_H with n degrees of freedom on a symplectic complex manifold M."

- **(a) Non-compact Γ, field of meromorphic functions on Γ.** **Theorem 7** (p. 72): "If there are n meromorphic first integrals of X_H which are in involution and independent over a neighbourhood of the curve i(Γ) (not necessarily on Γ itself), then the Galois group of the VE over Γ is n-involutive Ziglin. This Galois group is the Zariski closure of the monodromy group. Furthermore, the identity component of the Galois group of the VE over Γ is abelian."
  The NVE version is **Corollary 8** (p. 79): with f₁,…,f_k independent over Γ, the Galois group of the NVE is (n−k)-involutive Ziglin and its identity component is abelian.
- **(b) Adding points.** **Theorem 8** (p. 73) adds equilibrium points to get Γ̄. It needs integrals "meromorphic and in involution over a neighbourhood of the curve Γ̄ and independent in a neighbourhood of Γ̄ (not necessarily on Γ itself)"; the conclusion concerns the identity component of the Galois group of the meromorphic VE over Γ̄. **Theorem 9** (p. 73) also adds points at infinity, M′ = M ∪ M_∞ and Γ̄′. It needs integrals "meromorphic and in involution over a neighbourhood of the curve Γ′ in M′ (in particular meromorphic at infinity)", and the conclusion is the same for the VE over Γ̄′. The authors warn: "our abelian criterion is less and less precise (the set of allowed first integrals is smaller at each step…)" (p. 73).
- **Fuchsian remark** (pp. 73–74): "if the meromorphic VE over Γ̄′ is regular singular (i.e. of Fuchs type), then our three differential Galois groups coincide". One then obstructs n integrals "meromorphic on the initial manifold M … (An arbitrary growth at infinity is allowed.)"
- **(c) Recovering Ziglin.** Theorem 7 already says the Galois group over Γ "is the Zariski closure of the monodromy group". **Corollary 9** (pp. 79–80) is Ziglin's 2-dof statement. **Theorem 10** (p. 80): "Ziglin's Theorem (Theorem 1) is true mutatis mutandis if we substitute Galois group by monodromy group" (proof attributed to Churchill).
- **Covering invariance.** **Theorem 5** (§3.4, p. 51): a finite ramified covering X′ → X induces an injective Gal(∇′) → Gal(∇) that is an isomorphism on Lie algebras, so the identity component is invariant. This is the justification for changing the independent variable to an algebraic one (as MPS do).
- **Monodromy and Galois group** (§3, p. 46): "The monodromy group is contained in the Galois group and if the equation is of Fuchsian class … the Galois group is dense in the monodromy group (Zariski topology)" (sic: closure of monodromy = Galois group).
- **(d) Morales-Ruiz, Ramis, Simó 2007 (verified):** "Integrability of Hamiltonian systems and differential Galois groups of higher variational equations", *Ann. Sci. ÉNS* (4) **40**(6), 845–884, doi:10.1016/j.ansens.2007.09.002. **Theorem 2** (p. 849): if the system is completely integrable with meromorphic first integrals in a neighbourhood of Γ, "not necessarily independent on Γ itself", then for each k the identity component (G_k)⁰ of the Galois group of the k-th variational equation VE_k is commutative. Proposition 1: if (G₁)⁰ is commutative, then all (G_k)⁰ are solvable.
- **(e) Non-Hamiltonian and non-commutative versions:**
  - Ayoul & Zung (verified): "Galoisian obstructions to non-Hamiltonian integrability", *C. R. Math.* **348**(23–24), 1323–1326 (2010), doi:10.1016/j.crma.2010.10.024. Abstract: if a system is meromorphically integrable in the non-Hamiltonian (Bogoyavlenskij) sense, the Galois groups of the variational equations of any order along its solutions are virtually abelian.
  - *The prompt's year is off:* the Maciejewski & Przybylska paper is "Differential Galois obstructions for non-commutative integrability", *Phys. Lett. A* **372**(33), 5431–5435 (**2008**), doi:10.1016/j.physleta.2008.06.050 (verified by Crossref). The abstract could not be opened (403), so its statement is **NOT VERIFIED**.

### B.2 Ziglin 1982

**Citations (verified):** S. L. Ziglin, "Branching of solutions and nonexistence of first integrals in Hamiltonian mechanics. I", *Funct. Anal. Appl.* **16**(3), 181–189 (1982), doi:10.1007/BF01081586. "… II", **17**(1), 6–17 (1983), doi:10.1007/BF01083174. The originals were not opened. The statement below is as **restated in MR I, Theorem 1, p. 34**: "Suppose that the Hamiltonian system admits n − k additional analytical first integrals, independent over a neighborhood of Γ (but not necessarily on Γ itself). We assume moreover that the monodromy group of the NVE contain a non-resonant transformation g. Then any other element of the monodromy group of the NVE sends eigendirections of g into eigendirections of g."
- Non-resonant (MR I, p. 34) means there is no relation λ₁^{r₁}⋯λ_n^{r_n} = 1 with nonzero integer r (the typesetting is garbled in the PDF).
- 2-dof form (MR I, Corollary 9): with one meromorphic integral f independent of H near i(Γ), other monodromy elements preserve or swap the two eigendirections of g. MR note that Ziglin's result needs no involutivity hypothesis.

### B.3 Kimura 1969

**Citation (verified from the paper's first page):** T. Kimura, "On Riemann's equations which are solvable by quadratures", *Funkcialaj Ekvacioj* **12**, 269–281 (1969); MR0277789. Read in full (scan).
- **Notation** (§1, p. 270): exponent differences λ = ρ′−ρ, μ = σ′−σ, ν = τ′−τ. The ground field K = C(x), and exponents are arbitrary complex numbers. **Complex exponent differences are covered.**
- **Theorem I** (§8, p. 277): "In order for L to be a generalized Liouville extension of K, it is necessary and sufficient that either
  (A) At least one of λ+μ+ν, −λ+μ+ν, λ−μ+ν and λ+μ−ν is an odd integer, or
  (B) The quantities λ or −λ, μ or −μ and ν or −ν take values given in the union of the tables of Schwarz and of Hukuhara-Ōhasi".
  Generalized Liouville means the identity component of the Galois group is solvable (p. 277).
- **Union table** (p. 277): row 1 is (1/2 + l, 1/2 + m, arbitrary complex number); rows 2–15 are "the same as in the table of Schwarz". Schwarz's table (§5, p. 274–275), up to order and sign, with l, m, n integers:

| # | λ | μ | ν | condition |
|---|---|---|---|---|
| 1 | 1/2+l | 1/2+m | rational (Schwarz) / arbitrary complex (union table) | |
| 2 | 1/2+l | 1/3+m | 1/3+n | |
| 3 | 2/3+l | 1/3+m | 1/3+n | l+m+n even |
| 4 | 1/2+l | 1/3+m | 1/4+n | |
| 5 | 2/3+l | 1/4+m | 1/4+n | l+m+n even |
| 6 | 1/2+l | 1/3+m | 1/5+n | |
| 7 | 2/5+l | 1/3+m | 1/3+n | l+m+n even |
| 8 | 2/3+l | 1/5+m | 1/5+n | l+m+n even |
| 9 | 1/2+l | 2/5+m | 1/5+n | l+m+n even |
| 10 | 3/5+l | 1/3+m | 1/5+n | l+m+n even |
| 11 | 2/5+l | 2/5+m | 2/5+n | l+m+n even |
| 12 | 2/3+l | 1/3+m | 1/5+n | l+m+n even |
| 13 | 4/5+l | 1/5+m | 1/5+n | l+m+n even |
| 14 | 1/2+l | 2/5+m | 1/3+n | l+m+n even |
| 15 | 3/5+l | 2/5+m | 1/3+n | l+m+n even |

  (Rows 8–14 carry a ditto mark for "l+m+n=even". Row 15 is on p. 275.)
- **Theorem II** (p. 277–278): the Picard–Vessiot extension is a **Liouville** extension (whole group solvable) iff (λ, μ, ν) satisfy the Hukuhara–Ōhasi condition: the same (A), or (B) with the H–Ō table, which is rows 1–5 with row 1's third entry "complex number" (p. 275).
- **(0, 1/2, i√3/2):** *my application of the theorem, consistent with the prompt's belief.* The four sums ±0 ± 1/2 ± i√3/2 are non-real, so (A) fails. For row 1 (two entries in 1/2 + Z), only μ = 1/2 qualifies; λ = 0 is not a half-integer and ν is non-real. Rows 2–15 need all three entries rational. So by Theorem I the identity component is **not solvable**: **not solvable by Kimura.** Kimura places no restriction excluding λ = 0. Whether that singular point is logarithmic does not enter the criterion.
- MR I (§3.5, Example 1, p. 52–53) says the same in words: outside the one family "in which one of the parameters is an arbitrary complex number and the others two are half-integers", the allowed values are discrete.

### B.4 Poincaré's theorem in Kozlov's formulation

**Citation (verified):** V. V. Kozlov, "Integrability and non-integrability in Hamiltonian mechanics", *Russian Math. Surveys* **38**(1), 1–76 (1983) (Uspekhi Mat. Nauk 38:1, 3–67), doi:10.1070/RM1983v038n01ABEH003330. Read in English (author's homepage PDF).
- **Setting** (Ch. IV, §1, p. 33): H = H₀(I) + εH₁(I, φ) + …, analytic on D × Tⁿ. The **Poincaré set** 𝔅 is the set of I ∈ D for which there exist n−1 linearly independent k_s ∈ Zⁿ with ⟨k_s, ω(I)⟩ = 0 and the Fourier coefficients H₁,k_s(I) ≠ 0. A **key set** (set of uniqueness) for 𝔄(V) is a set on which any analytic function that vanishes there vanishes identically on V.
- **Theorem 1** (Ch. IV §1, p. 33): "Suppose that the unperturbed system is non-degenerate: det‖∂²H₀/∂I²‖ ≠ 0 in D; that I⁰ ∈ D is a non-critical point of H₀; and that in any neighbourhood U of it the Poincaré set 𝔅 is a key set for 𝔄(U). Then the Hamiltonian equations (1) do not have an integral F independent of H that can be expressed as a formal power series Σ F_s(I, φ)ε^s with coefficients analytic in D × Tⁿ."
- **Answer to the crucial question: (A).** The theorem excludes only integrals that are **formal power series in ε** with analytic coefficients. Two passages settle this. Ch. IV §2 (p. 40): "in § 1 it was proved that there are no integrals formally-analytic in e". And also on p. 40: "from this theorem one cannot deduce the non-integrability of perturbed systems for fixed values of e ≠ 0."
- Other statements: Theorem 2 (§1, p. 34) is the same with a dense Poincaré set and C^∞ coefficients. Theorem 3 (§1, p. 36) is the non-autonomous (or energy-reduced) version with the set 𝔅*.
- **On fixed ε:** Kozlov (p. 40) says that for 2 dof with H₀ non-degenerate and small fixed ε ≠ 0 there are infinitely many periodic trajectories (KAM plus Poincaré's last geometric theorem), "Unfortunately, nothing can be said about their isolation." Fixed-ε results come from splitting of asymptotic surfaces (Ch. V, see B.5): Bolotin's Theorem 1 and Theorem 3 in Ch. V §2.
- **Book (2nd source, not opened):** V. V. Kozlov, *Symmetries, Topology and Resonances in Hamiltonian Mechanics*, Springer 1996. The Crossref chapter list puts "Nonintegrability of Hamiltonian Systems Close to Integrable Ones" at pp. 148–221 (chapter DOI suffix _5; it is Ch. IV if the Introduction is unnumbered). Its theorem numbers are **NOT VERIFIED**.

### B.5 Separatrix splitting implies non-integrability (analytic, 2 dof)

- **Kozlov 1983, Ch. V** ("Bifurcation of asymptotic surfaces"; read):
  - **§1 Theorem 1 (Poincaré)** (p. 44): for H = H₀(y, x) + εH₁(y, x, t) + …, 2π-periodic in t, with hyperbolic equilibria joined by a doubly asymptotic solution, if H₁(y₊, x₊, t) = H₁(y₋, x₋, t) and ∫{H₀, H₁}(…) dt ≢ 0, then "for small e ≠ 0 the perturbed asymptotic surfaces Λ⁺_ε and Λ⁻_ε do not coincide". This is the Poincaré–Melnikov integral.
  - **§2 Theorem 3** (p. 48): n = 1 (time-periodic one degree of freedom, equivalent to 2 dof autonomous on an energy level after Whittaker reduction). If ∫{H₀, H₁}(z₀(t), t) dt ≢ 0 and, for small ε, the perturbed system has a doubly asymptotic solution near z₀, then "for small e ≠ 0 the Hamiltonian system … does not have an additional analytic integral" [ref. 65 in Kozlov]. **Transversality is not used.** The proof only needs that the separatrices "intersect and do not coincide": the iterates gⁿ(Δ) of an arc of W₂ crossing W₁ accumulate on W₁ and form a key set for analytic functions.
  - **§2 Theorem 1 (Bolotin)** (p. 46): an n-dof version near a closed doubly-asymptotic trajectory, for small fixed ε ≠ 0, with condition ∫{H₀{H₀, H₁}} ≠ 0. Theorem 2 (p. 47) needs a convergent Birkhoff transformation.
- **Cushman 1978 (verified):** R. Cushman, "Examples of nonintegrable analytic Hamiltonian vector fields with no small divisors", *Trans. AMS* **238**, 45–55 (1978), doi:10.1090/S0002-9947-1978-0478223-8. Per the abstract (search snippet only): for M = R², an analytic symplectic map with a **finite contact** homoclinic point is nonintegrable, so **non-transversal contact is allowed**. The full text was not opened (403).
- **Cresson** (read): "About analytic non integrability", arXiv:math/0509547 (2005). It summarizes the state of the art:
  - Moser's theorem (*Stable and Random Motions*, Ann. Math. Stud. 77, 1973) covers a transverse homoclinic crossing.
  - Cresson's **Theorem 2.3**: an analytic diffeomorphism of R² with a hyperbolic fixed point whose 1-D stable and unstable manifolds "intersect at an isolated homoclinic point B, B ≠ p, which is not of Newhouse type" has no nontrivial analytic first integral. Cresson notes this also follows from Moser plus Conley: a degenerate non-coincident intersection has transverse points nearby (via Rayskin, DCDS 12 (2005)). He also says that for analytic maps, non-coincident intersecting manifolds necessarily meet with finite order.
  - **Theorem 2.4**: positive topological entropy implies no nontrivial analytic integral for analytic diffeos of R² (Katok plus Moser).
  - Cresson's JDE paper: "Hyperbolicity, transversality and analytic first integrals", *J. Differential Equations* **196**, 289–300 (2004) (verified by Crossref).
- **Moser 1973:** the book is verified (Crossref record of the 2001 Princeton reprint, doi:10.1515/9781400882694). The exact theorem number is **NOT VERIFIED**; the content is as attributed by Cresson.
- **Ziglin 1980:** *the actual title differs from the prompt's.* It is S. L. Ziglin, "Dichotomy of the separatrices, bifurcation of solutions and nonexistence of an integral in the dynamics of a rigid body" (another translation of the same Russian title), *Trudy Moskov. Mat. Obshch.* **41**, 287–303 (1980) (mathnet/mathdoc record via search). The content is **NOT VERIFIED**. Related, also from the abstract only: Ziglin, "Splitting of the separatrices and the nonexistence of first integrals in systems of differential equations of Hamiltonian type with two degrees of freedom", *Math. USSR-Izv.* **31**(2), 407–421 (1988) (Izv. AN SSSR 51:5 (1987) 1088–1103), doi:10.1070/IM1988v031n02ABEH001082. It relates splitting of real **and complex** separatrices of hyperbolic cycles to the absence of additional **meromorphic** integrals.
- **Churchill & Rod 1980 (verified):** "Pathology in dynamical systems. III. Analytic Hamiltonians", *J. Differential Equations* **37**(1), 23–38 (1980), doi:10.1016/0022-0396(80)90085-6. The content (whether transversality is required) is **NOT VERIFIED**.
- **Dovbysh:** I could not identify a 1989 paper. Cresson cites S. Dovbysh, "Transversal intersection of separatrices and branching of solutions as obstructions to the existence of an analytic integral in many-dimensional systems I", *Collectanea Math.* **50**(2), 119–197 (1999) (this citation is NOT VERIFIED). Crossref has Dovbysh short notes in *Russ. Math. Surveys* **51**(4) 730 (1996) and **55**(3) 574 (2000). The 1989 item is **NOT VERIFIED**.
- **Burns & Weiss 1995 (verified):** "A geometric criterion for positive topological entropy", *Commun. Math. Phys.* **172**(1), 95–118 (1995), doi:10.1007/BF02104512. Per bibliographic and abstract fragments: a homoclinic point with a **topological crossing** (possibly infinite-order contact) gives positive topological entropy. Combined with Cresson's Theorem 2.4 for analytic maps of R², this rules out an analytic integral. The full text was not opened. Addendum: Homburg & Weiss, CMP **208**, 267–273 (1999) (homoclinic tangencies).
- **Summary for B.5:** in the analytic 2-dof (area-preserving map) setting, transversality is **not required**. "The asymptotic curves intersect but do not coincide" suffices (Kozlov Ch. V §2 Thm 3; Cushman for finite contact; Cresson Thm 2.3 via Conley/Rayskin). Analyticity is what forces a non-coincident intersection to have finite order.

### B.6 Melnikov method for autonomous 2-dof Hamiltonians

- **Holmes & Marsden 1982 (verified):** "Horseshoes in perturbations of Hamiltonian systems with two degrees of freedom", *Commun. Math. Phys.* **82**(4), 523–544 (1982), doi:10.1007/BF01961239. Only the abstract (Caltech record) was read: small coupling perturbations of pendulum ⊕ oscillator, possibly with ± damping, "breaks the integrability" by producing horseshoes. **The exact hypotheses are NOT VERIFIED**: the form H = F(q, p) + G(I) + εH₁, G′(I) ≠ 0, the Melnikov function M(θ₀) = ∫{F, H₁} along the homoclinic orbit, simple zeros, and the conclusion (transverse homoclinic orbits in the energy level, hence a Smale horseshoe and no analytic integral). Polcar–Semerák 2019 apply exactly this reduction (J fixed is "equivalent to fixing the energy surface", using the conjugate angle as time).
- **Robinson 1988 (verified, but Crossref lacks the author field):** C. Robinson, "Horseshoes for autonomous Hamiltonian systems using the Melnikov integral", *Ergodic Theory Dynam. Systems* **8** (Conley memorial issue), 395–409 (1988), doi:10.1017/S0143385700009500. The author name comes from the Crossref record of the companion paper, "Melnikov method for autonomous Hamiltonians", Contemp. Math. 198 (1996), 45–53. Abstract: a unified treatment of autonomous perturbations of completely integrable Hamiltonians, joining Holmes–Marsden with Lerman–Umanskii, and showing two forms of the Melnikov integral agree. Hypotheses are **NOT VERIFIED**.
- **Morales-Ruiz & Peris 1999 (verified, read abstract and structure):** "On a Galoisian approach to the splitting of separatrices", *Ann. Fac. Sci. Toulouse Math.* (6) **8**(1), 125–141 (1999), doi:10.5802/afst.925. It concerns 2-dof analytic Hamiltonians with a homoclinic orbit to a **saddle-center** (not a hyperbolic saddle). It relates the Galois obstruction to Lerman's theorem on transversal homoclinic orbits, via Grotta-Ragazzo's interpretation (Theorems 3–4, Props. 2–3).
- Wiggins' book: not consulted.

### B.7 Dependence of differential Galois groups on parameters

- **Seiss (read the introduction):** M. Seiss, "Root parametrized differential equations for the classical groups", arXiv:1609.05535 (journal **NOT VERIFIED**). **Theorem 0.1 (Specialization Bound):** "The differential Galois group H(C) of the specialized equation ∂(y) = A(σ(t))y over C(z) is a subgroup of G(C)", where G is the group of the parameter equation over the differential field C⟨t⟩. The parameters are *differential* indeterminates, specialized to C[z], with σ extending to suitable localizations. Seiss notes Goldman 1957 had "a similar approach using so-called analytic specializations". **This is the citable "specialization is a subgroup of generic" statement**, with (up to conjugacy) the setting caveats above.
- **Goldman 1957 (verified):** L. Goldman, "Specialization and Picard-Vessiot theory", *Trans. AMS* **85**(2), 327–356 (1957), doi:10.1090/S0002-9947-1957-0087645-5. The text was not opened, so the statement is **NOT VERIFIED**.
- **Singer 1993 (verified, abstract read):** M. F. Singer, "Moduli of linear differential equations on the Riemann sphere with fixed Galois groups", *Pacific J. Math.* **160**(2), 343–395 (1993), doi:10.2140/pjm.1993.160.343. Order-n equations with polynomial coefficients of degree ≤ m, with fixed exponents and determining factors at singular points (positions free). For G in a large class (finite, connected, G⁰ semisimple or unipotent), the set with fixed Galois group G and fixed G-module "forms a constructible set". There is an example where this fails.
- **Feng & Wibmer (read in part):** "Differential Galois groups, specializations and Matzat's conjecture", arXiv:2209.01581 (v2, 2024). The good specializations contain an "ad×Jac-open" subset and are Zariski dense (Theorem B / Thm 4.26). They state that good specializations **need not** form a Zariski open or constructible set (example: y′ = (α/x)y). **The prompt's "countable union of proper closed subsets" form: I did not find it stated in any source I opened (NOT VERIFIED).**
- Katz (1990), André (2004), Hrushovski (2002): cited by Feng–Wibmer as studying specialization. Their statements are **NOT VERIFIED**.

### B.8 Singer 1991

**Citation (verified):** M. F. Singer, "Liouvillian solutions of linear differential equations with Liouvillian coefficients", *J. Symbolic Comput.* **11**(3), 251–273 (1991), doi:10.1016/S0747-7171(08)80048-X. The abstract and §1 were read.

Singer gives a decision procedure for whether L(y) = b has a nonzero solution in K, when K is an **elementary extension of C(x)** or an algebraic extension of a purely transcendental Liouvillian extension of C(x), over a computable algebraically closed C. From this he builds a procedure to find a basis of the solutions of L(y) = 0 that are **Liouvillian over K**. Singer's own examples include C(x, eˣ, e^{x²}). C(x, exp(r(x))) with r rational is an elementary extension of C(x), so **an algorithm exists** for second-order equations over that field, in particular deciding whether Liouvillian solutions exist. For order 2 this is equivalent to the identity component of the Galois group over K being solvable.

Caveat: this concerns the Galois group over C(x, e^{r}). That is a subfield of the meromorphic functions on Γ, so its group can be **larger** than the group over M(Γ) appearing in MR Theorem 7 (MR p. 72–73). A non-abelian result over C(x, e^{r}) corresponds to the weaker theorems of the 8/9 type, unless one shows that the groups coincide.

### B.9 Essential singularities, accumulating singular points, exponential potentials

- **I found nothing** in the sources I opened on differential Galois groups or monodromy of second-order ODEs with infinitely many regular singular points accumulating at an essential singularity, or on Morales–Ramis/Ziglin proofs using a hypergeometric local model near such a point. The searches for exponential and Toda-like potentials with Kimura returned only generic Morales–Ramis material.
- Loosely related items:
  - MR I, Theorem 12 (Appendix, p. 89–90) treats meromorphic connections on an arbitrary connected Riemann surface X with poles on a discrete set S. This covers infinitely many singular points on a non-compact Γ, i.e. the Theorem 7 framework is set up for that.
  - MR I says the Riemann surface may be open: "If the Riemann surface is open it is a transcendental problem" (p. 73).
  - H. Yoshida, "A criterion for the non-existence of an additional integral in Hamiltonian systems with a homogeneous potential", *Physica D* **29**(1–2), 128–142 (1987), doi:10.1016/0167-2789(87)90050-9 (verified by Crossref; content not opened). This is the classical use of Kimura's theorem for homogeneous potentials.
  - Rothos & Bountis, chao-dyn/9903029 (1999): infinite branching of solutions in complex time; abstract only, no Galois content.

---

## PROVEN vs NUMERICAL: summary table

| System / claim | Source | Status | Parameters covered |
|---|---|---|---|
| MN geodesics: chaos / loss of 4th integral | Gair–Li–Mandel 2008 | NUMERICAL | χ = 0.9, q = 0.95, E = 0.95, L_z = 3M (q > 0, χ ≠ 0 oblate) |
| MN: Birkhoff islands, resonance plateaus | Apostolatos et al. 2009; LG et al. 2010; CLA 2011 | NUMERICAL | same family (χ = 0.9, q = 0.95) |
| SAV: possible quartic Killing tensor | Brink II (2008) | HEURISTIC/NUMERICAL | MN, ZV examples |
| SAV: second-order KT very restrictive | Brink III (2010) | analytic argument (classification status NOT VERIFIED) | SAV |
| SAV: fourth-order KT formal solution | Brink 2011 | conditional formal solution; no theorem | SAV |
| ZV: no polynomial integral of degree ≤ 6 | Kruglikov–Matveev 2012 | PROVEN (computer algebra) | δ = 2 |
| ZV: no additional meromorphic integral | Maciejewski–Przybylska–Stachowiak 2013 | PROVEN (Morales–Ramis + Kovacic, 1st-order NVE, equatorial radial solution) | δ = 2 (δ = 1/2 claimed) |
| ZV chaos | Lukes-Gerakopoulos 2012 | NUMERICAL | δ > 1 and δ < 1 samples |
| Weyl class: valence-3 KTs reducible | Vollmer 2015 | PROVEN | all static vacuum Weyl |
| TS / C-metric / ZV: no KT up to valence 7 / 9 / 11 | Vollmer 2017 | PROVEN (computer algebra) | specific parameters (NOT VERIFIED) |
| Newtonian SAV potentials: no quartic integrals | Markakis 2014 | PROVEN (Newtonian only) | Newtonian analogue |
| Schwarzschild + Hill-type perturbation: chaotic invariant set | Moeckel 1992 | PROVEN (per abstract) | perturbative |
| Schwarzschild + EM fields | Santoprete–Cicogna 2002 | Melnikov "proof" (first order) | small fields |
| Schwarzschild + GWs | Letelier–Vieira 1997 | Melnikov, graphical | small amplitude |
| BH + ring/disc (mostly pseudo-Newtonian) | Polcar–Semerák 2019 | Melnikov evaluated numerically; no theorem | specific configurations |
| Static axisymmetric vacuum chaos criterion | Sota–Suzuki–Maeda 1996 | HEURISTIC | several Weyl metrics |
| Kerr + tidal quadrupole: no deformed Carter constant | Ramond 2026 (preprint) | partial analytic + numerical | generic spin, generic coupling |
| **MN (any α_n ≠ 0): rigorous non-integrability** | — | **nothing found in the literature** | — |
| Kerr frequency-map non-degeneracy on an open set | Xue 2021 (twist only, with plots); WBS 2013 (non-injectivity) | **not proven in sources found** | — |
| Kerr equatorial homoclinic orbits, closed form | Levin–Perez-Giz 2009 | PROVEN (explicit) | equatorial only; inclined deferred |
| On-axis transverse deviation via f″(z) | no general source; Kerr explicit (Lima Junior et al. 2020) | Kerr only (my hand check matches f″/4) | Kerr |

## Could not verify

- MN 1992 original: the formulas as printed and the specific typos. All formulas here are from GLM 2008, LG 2010 and Bambi–Barausse 2011. The exact corrections credited to Brink 2008 and Fang 2007 are not checked.
- Apostolatos et al. PRL 2009 and Contopoulos et al. IJBC 2011: content (bibliography verified).
- Brink III: whether the restriction is a full classification theorem.
- Vollmer 2017: which Tomimatsu–Sato and ZV parameter values.
- The author-list discrepancy for the ZV Comment (PRD 88, 108501), and the Reply.
- Moeckel 1992: method and exact theorem (abstract snippet only).
- Bombelli & Calzetta 1992; Vieira & Letelier 1996 (PRL, and which "core–halo" paper is meant); Guéron & Letelier 2002: content.
- "Han 2008": not identified at all.
- Polcar, Suková, Semerák 2019 "V" (ApJ 877, 16): bibliography from a search snippet only.
- Inclined Kerr homoclinic orbits in closed form: no source found.
- Lima Junior et al. EPJ Plus: article number.
- Morales-Ruiz 1999 book: theorem numbers. MR II (2001): content.
- Maciejewski & Przybylska 2008 (non-commutative integrability): statement.
- Ziglin 1982 originals (statement taken from MR I's restatement). Ziglin 1980 Trudy MMO: content.
- Kozlov 1996 book: chapter and theorem numbering.
- Cushman 1978: full text (abstract only). Churchill & Rod 1980: content. Dovbysh "1989": not identified (a 1999 Collectanea paper is cited by Cresson; that citation is also unverified). Moser 1973: theorem number.
- Holmes & Marsden 1982 and Robinson 1988: exact hypotheses and conclusions (abstracts only).
- Goldman 1957, Katz, André 2004, Hrushovski 2002: statements. Seiss 1609.05535: journal.
- Any "countable union of proper closed subsets" statement for parameter dependence of Galois groups: not found.
- B.9: no source found for essential singularities with accumulating regular singular points.
