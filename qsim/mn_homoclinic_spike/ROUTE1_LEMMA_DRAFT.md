# Route 1, the missing piece: a parameter-dependent C² bound for the local unstable manifold (DRAFT for a non-author read)

Written 2026-11-28 by Claude Opus 5.5 (office "Quantum"). Maths only, 0 core-h.
- Status: **read CORRECT by the Bridge (2026-11-28), after fix F1 (the domain δ*, folded in) and with F2 open (a citation for
  (0) checked at source).** Earlier status: DRAFT; it is not to be used in any certifying run before the Bridge's non-author read (a separate AI
  session; not human peer review).
- Starting point: Neon's sketch (FOLLOWUPS_answers.md, card 2, B), re-derived here from scratch, with every step
  written out.
- Related: EXPLICIT_BETA_ROUTES_DRAFT.md (route 1); A11 (the 2-D cone lemma, read CORRECT).

## 0. Why it is needed
- Route 1 certifies 0 ∉ [t′] on β-intervals, where t(β) = v_x/v_px is the slope of W^u at the symmetric point p(β).
- The tangent v(β) starts from the local unstable manifold at its start point w^u(s(β), β). Then:
  - t′ needs ∂_β of that start point and of its tangent;
  - because s(β) moves with β, t′ also needs the curvature of W^u_loc.
- The A11 cone lemma gives only a Lipschitz graph with slope in [−L, L]. That is enough for t, but it gives no
  derivative in β or in u.
- This lemma supplies enclosures of h_β, h_uu and h_uβ, uniformly over a β-interval.

## 1. Setting and notation
- **The family.** P_β is the analytic area-preserving return map (on the section Σ, coordinates w = (x, p_x)), for
  β ∈ I = [β₋, β₊].
  - w_β is its hyperbolic fixed point, analytic in β (it is enclosed, together with c′(β) = dw_β/dβ, by a parametric
    Krawczyk; §4).
- **A FIXED invertible frame matrix T** (for example, Kerr's eigenvectors at w₀), with columns ũ and s̃.
- **Frame coordinates centred at the TRUE fixed point:**
  - F_β(z) := T⁻¹(P_β(w_β + Tz) − w_β), with z = (u, s).
  - Then F_β(0) = 0 for every β. F is analytic in (z, β).
  - Write F = (F^u, F^s).
  - **Note, so that no enclosure omits it:** F_β includes the fixed point's drift,
    ∂_β F = T⁻¹(∂_β P(w_β + Tz) + (DP(w_β + Tz) − I) c′(β)), with c′(β) = dw_β/dβ. The same c′ enters F_uβ and F_sβ
    through D²P.
- **The box:** B = [−δ, δ]², and Z = B × I.
  - Every partial derivative of F below is enclosed over Z, with w_β ranging over its enclosure.
  - Sup-bounds are written ‖·‖ (the sup over Z of the absolute value of the interval enclosure).
- **The graph domain (F1, the Bridge's read).** A11 guarantees the graph only over |u| ≤ δ*. With the frame centred at
  the TRUE fixed point, ρ′ = 0, and L ≤ 1, that is δ* = δ/(A + bL) < δ (A is defined below).
  - All statements about h are on D := [−δ*, δ*] × I.
  - The derivative enclosures of F stay over Z = B × I, which contains every graph point over D: |u| ≤ δ* ≤ δ and
    |h| ≤ Lδ* ≤ δ.
- **First-order bounds over Z:**
  - a := inf F^u_u;  A := ‖F^u_u‖ (its upper bound);  b := ‖F^u_s‖;  c := ‖F^s_u‖;  d := ‖F^s_s‖.

## 2. Hypotheses (each is an interval inequality, checkable over Z)
- **(K1) A11's cone conditions, uniformly in β ∈ I.** For some 0 < L ≤ 1:
  - μ := a − bL > 1;
  - c + dL ≤ Lμ;
  - ν := c/L + d < 1.
- **(K2) β-contraction:** κ := d + Lb < 1.
- **(K3)** κ < μ² and κ < μ. Both are automatic from (K1) and (K2), since μ > 1 > κ. They are listed so the reader
  sees which factor enters where.
- **(K4) Finiteness:** every second-order partial of F (the uu, us, ss, uβ, sβ partials), and F_β, is finitely
  enclosed over Z.
  - This is the NaN rule; it fails closed.

## 3. Lemma (the parameter-dependent C² graph bound)
**Assume (K1)–(K4).** For each β ∈ I, write W^u_loc,β ∩ (frame box) as the graph s = h(u, β), |u| ≤ δ* (A11). All the sups below are over D = [−δ*, δ*] × I.
  Then:
- **(a)** h(0, β) = 0 and |h_u| ≤ L on D. These are A11's conclusions, applied for each β.
- **(b)** |h_β| ≤ H_β := Q_β / (1 − κ), with Q_β := ‖F^s_β‖ + L‖F^u_β‖. Moreover h_β(0, β) = 0.
- **(c)** |h_uu| ≤ H_uu := Q_uu / (μ² − κ), with
  Q_uu := ‖F^s_uu‖ + 2L‖F^s_us‖ + L²‖F^s_ss‖ + L(‖F^u_uu‖ + 2L‖F^u_us‖ + L²‖F^u_ss‖).
- **(d)** |h_uβ| ≤ H_uβ := Q_uβ / (μ − κ), with
  Q_uβ := ‖F^s_uβ‖ + H_β‖F^s_us‖ + L‖F^s_sβ‖ + L H_β‖F^s_ss‖ + H_uu G_β (A + bL)
          + L(‖F^u_uβ‖ + H_β‖F^u_us‖ + L‖F^u_sβ‖ + L H_β‖F^u_ss‖),
  where G_β := ‖F^u_β‖ + b H_β bounds |g_β| (g is defined in the proof). The order of computation is H_β, then
  H_uu, then H_uβ.

### Proof
- **(0) Regularity, the one standard fact (cited, not re-proved).** For an analytic family of maps with a
  hyperbolic fixed point, the local unstable manifold is an analytic graph, jointly analytic in (u, β).
  - Standard: the unstable manifold theorem with parameters; equivalently, the parametrisation method with
    parameters, e.g. Hirsch–Pugh–Shub, Invariant Manifolds, LNM 583 (1977), or Cabré–Fontich–de la Llave, "The
    parameterization method for invariant manifolds I", IUMJ 52 (2003) 283–328.
  - **Neither has been read at source yet** (the CFdlL preprint host refused automated fetches); the coordinator has
    been asked to fetch one.
  - Only C² JOINT regularity in (u, β) is used here, not analyticity.
  - So h, h_u, h_β, h_uu and h_uβ exist and are continuous on the compact set D. Their sups m_β, m_uu and
    m_uβ are therefore FINITE. That finiteness is all the "sup" argument below needs.
  - (A11, which was read CORRECT, already identifies W^u_loc,β ∩ B as the graph, with slope ≤ L, for each fixed β.)
- **(1) The invariance equation.**
  - Put g(u) := F^u(u, h(u)) (with β implicit).
  - **(i) g is expanding.** g(0) = 0 and g′ = F^u_u + F^u_s h_u ≥ a − bL = μ > 1.
    - So for every v ∈ [−δ*, δ*] there is a unique u = g⁻¹(v), and it satisfies |u| ≤ |v|/μ < δ*.
  - **(ii) The image stays in the box.** |F^s(u, h(u))| ≤ (c + dL)|u| ≤ Lμ|u| ≤ L|g(u)| ≤ Lδ* ≤ δ.
    - So, for |g(u)| ≤ δ*, P maps the graph point (u, h(u)) into B, with u-coordinate in [−δ*, δ*].
    - The image point's backward orbit (the graph point, then that point's backward orbit) stays in B. So the image
      lies in W^u_loc ∩ B with |u| ≤ δ*, i.e. on the graph over D (A11).
  - Hence, for every u with |g(u)| ≤ δ*: **h(g(u, β), β) = F^s(u, h(u, β), β).** (★)
  - Every derivative below is a derivative of (★), and is legitimate by (0).
- **(b) h_β.**
  - Differentiate (★) in β, with h_β evaluated at u on the left and at v = g(u) on the right:
    F^s_β + F^s_s h_β(u) = h_u(v) g_β + h_β(v), where g_β = F^u_β + F^u_s h_β(u).
  - So h_β(v) = [F^s_s − h_u(v) F^u_s] h_β(u) + [F^s_β − h_u(v) F^u_β].
  - Take the sup over v ∈ [−δ*, δ*], which is possible because u = g⁻¹(v) ∈ [−δ*, δ*] by (1-i):
    m_β ≤ (d + Lb) m_β + Q_β = κ m_β + Q_β.
  - With m_β finite and κ < 1, m_β ≤ Q_β/(1 − κ).
  - h(0, β) = 0 for all β (the frame is centred at w_β), so h_β(0, β) = 0.
- **(c) h_uu.**
  - Differentiate (★) in u once: F^s_u + F^s_s h_u = h_u(v) g′. (★u)
  - Differentiate again: F^s_uu + 2F^s_us h_u + F^s_ss h_u² + F^s_s h_uu(u) = h_uu(v) g′² + h_u(v) g″, where
    g″ = F^u_uu + 2F^u_us h_u + F^u_ss h_u² + F^u_s h_uu(u).
  - So h_uu(v) g′² = [F^s_s − h_u(v) F^u_s] h_uu(u) + {F^s_uu + 2F^s_us h_u + F^s_ss h_u² − h_u(v)(F^u_uu
    + 2F^u_us h_u + F^u_ss h_u²)}.
  - With g′ ≥ μ: μ² m_uu ≤ κ m_uu + Q_uu, so m_uu ≤ Q_uu/(μ² − κ).
- **(d) h_uβ.**
  - Differentiate (★u) in β. Here h_u(u) depends on β directly, and h_u(v) depends on β both directly and through
    v = g(u, β):
    F^s_uβ + F^s_us h_β + F^s_sβ h_u + F^s_ss h_β h_u + F^s_s h_uβ(u)
      = [h_uu(v) g_β + h_uβ(v)] g′ + h_u(v) ∂_β g′,
    where ∂_β g′ = F^u_uβ + F^u_us h_β + F^u_sβ h_u + F^u_ss h_β h_u + F^u_s h_uβ(u).
  - So h_uβ(v) g′ = [F^s_s − h_u(v)F^u_s] h_uβ(u) + {F^s_uβ + F^s_us h_β + F^s_sβ h_u + F^s_ss h_β h_u
    − h_uu(v) g_β g′ − h_u(v)(F^u_uβ + F^u_us h_β + F^u_sβ h_u + F^u_ss h_β h_u)}.
  - Bound the braces by Q_uβ, using |h_β| ≤ H_β, |h_uu| ≤ H_uu, |g_β| ≤ G_β and |g′| ≤ A + bL.
  - Then μ m_uβ ≤ κ m_uβ + Q_uβ, so m_uβ ≤ Q_uβ/(μ − κ). ∎

### Notes for the reader
- **N1.** All second partials are taken over the whole box Z, so the bounds hold uniformly in β ∈ I. The factors are
  1/(1 − κ), 1/(μ² − κ) and 1/(μ − κ). These match Neon's "κ, κ/μ², κ/μ" structure: its ratios are our κ, κ/μ²
  and κ/μ.
- **N2.** In Q_uβ, |g′| is bounded ABOVE by A + bL, with A = ‖F^u_u‖. The lower bound μ = a − bL enters only on the
  left-hand side. (A first draft had a + bL here; it was corrected before the read.)
- **N3.** Each sup over v uses u = g⁻¹(v) ∈ [−δ*, δ*], from (1-i). Each sup on the right-hand side is over the same
  box, so the inequalities are "m ≤ κm + Q" with the same m on both sides. That is valid because m < ∞, by (0).
- **N4.** At the start point s(β) ≈ 2e−12 used by the BVP, the slope h_u(s) can be tightened beyond [−L, L]:
  h_u(s) ∈ h_u(0, β) + H_uu|s|, where h_u(0, β) is the eigenvector slope in frame T. This is optional; with the cone
  form t′ widens, but it stays finite.

## 4. How route 1 would use it (outline; the details belong to a registration)
- **The start point:** w^u(s, β) = w_β + T(s, h(s, β)).
  - ∂_s w^u = T(1, h_u); ∂_β w^u = c′(β) + T(0, h_β); ∂_s∂_β w^u = T(0, h_uβ); ∂_s² w^u = T(0, h_uu).
- **The tangent at p:** v(β) = D(P^m)(w^u(s(β), β)) T(1, h_u(s(β), β)).
- **Then t′(β)** comes from v′ = [D²(P^m)·(∂_s w^u s′ + ∂_β w^u) + ∂_β D(P^m)] T(1, h_u) + D(P^m) T(0, h_uu s′ + h_uβ),
  with s′(β) from the parametric half-BVP (implicit function theorem, enclosed by a parametric Krawczyk).
- **Needed from CAPD:**
  - C² of P_β, with β carried as a state variable (β′ = 0);
  - the parametric fixed point w_β and c′(β);
  - the second partials of F over Z, for (K1)–(K4).
- **The pilot's open question (EXPLICIT_BETA_ROUTES_DRAFT, "the blocker"):** Z's β-extent drags w_β (|c′| ≈ 1.1) and
  the BVP nodes along with it. The derivative enclosures must therefore carry the β-dependence affinely (β as a state
  variable, with a parallelepiped aligned with c′), not as a box, or they widen by about the measured curvature.
  - The lemma itself is not affected; its hypotheses just get harder to satisfy if the enclosures are wide.

## 5. For the non-author reader
1. (1-ii): the image of a graph point stays in B and is on the graph. This uses c + dL ≤ Lμ and L ≤ 1, as A11 does.
2. Differentiating (★): especially the chain rule in (d), where h_u(v) depends on β through v = g(u, β).
3. The "m ≤ κm + Q" step, and its use of (0) for finiteness.
4. N2: the upper bound of g′ in Q_uβ (A + bL).
5. Whether citing the analytic dependence of the local manifold on parameters (0) is acceptable as a cited standard
   fact, or should be replaced by a parametrisation-method enclosure.
