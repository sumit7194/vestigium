/-
  OnlyKerr.Glue -- machine-checked GLUE for the "Only Kerr" argument.
  Requested by the Bridge for Sumit, 2026-11-21. Written by Claude Opus 5.5 (session "Quantum").

  Nothing numerical is re-run here. Certified numeric facts enter ONLY as explicitly named hypotheses
  (see `CertCases` below). Lean checks the exact algebra and the logic that joins them.

  1a. `elim_identity`: the E-elimination identity  D^2 G1 / E^2 = (1-t) S^2 + 2 t S + H^2 + 2 i y t S,  t = 1/E^2.
  1b. `curzon_tr_h1`, `curzon_tr_h2`, `curzon_tr_comm`: the Curzon trace identities.
  2.  `glue_re_pos`, `re_pos`, `G1_ne_zero`: the T19 case-split glue. From the three certified cases (hypothesis
      `CertCases`), Re(D^2 G1 / E^2) > 0, hence G1 != 0, for all a in (0,1), real y and t = 1/E^2 in (0,1].
  3.  `k5_3a` .. `k5_3d`: the K5 Theorem 1 constants (31/150, the radius 323/2400, the multiplier > 46).
-/
import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Analysis.Real.Pi.Bounds
import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.LinearAlgebra.Matrix.ZPow

open Complex Matrix

namespace OnlyKerr

/-! ## 1a. The E-elimination identity -/

/-- z = 1 + i y -/
noncomputable def zz (y : ℝ) : ℂ := 1 + (y : ℂ) * I
/-- D = z^2 + a^2 -/
noncomputable def DD (a y : ℝ) : ℂ := zz y ^ 2 + (a : ℂ) ^ 2
/-- S = y^2 + 1 - a^2 (real) -/
def SS (a y : ℝ) : ℝ := y ^ 2 + 1 - a ^ 2
/-- f0 = (z^2 - 2 z + a^2) / D -/
noncomputable def f0 (a y : ℝ) : ℂ := (zz y ^ 2 - 2 * zz y + (a : ℂ) ^ 2) / DD a y
/-- c0 = -H / D -/
noncomputable def c0 (a y : ℝ) (H : ℂ) : ℂ := -H / DD a y
/-- G1 = E^2 (f0^2 + c0^2) - f0 -/
noncomputable def G1 (a y E : ℝ) (H : ℂ) : ℂ := (E : ℂ) ^ 2 * (f0 a y ^ 2 + c0 a y H ^ 2) - f0 a y

/-- the numerator of f0 is -S -/
lemma num_eq (a y : ℝ) : zz y ^ 2 - 2 * zz y + (a : ℂ) ^ 2 = -((SS a y : ℝ) : ℂ) := by
  simp only [zz, SS]; push_cast; linear_combination (y : ℂ) ^ 2 * I_sq

/-- D = 1 + a^2 - y^2 + 2 i y -/
lemma DD_eq (a y : ℝ) : DD a y = 1 + (a : ℂ) ^ 2 - (y : ℂ) ^ 2 + 2 * (y : ℂ) * I := by
  simp only [DD, zz]; linear_combination (y : ℂ) ^ 2 * I_sq

/-- **1a.** the E-elimination identity, for complex H, with t := 1/E^2. -/
theorem elim_identity (a y E : ℝ) (H : ℂ) (hE : E ≠ 0) (hD : DD a y ≠ 0) :
    DD a y ^ 2 * G1 a y E H / (E : ℂ) ^ 2 =
      (1 - 1 / (E : ℂ) ^ 2) * ((SS a y : ℝ) : ℂ) ^ 2 + 2 * (1 / (E : ℂ) ^ 2) * ((SS a y : ℝ) : ℂ)
        + H ^ 2 + 2 * I * (y : ℂ) * (1 / (E : ℂ) ^ 2) * ((SS a y : ℝ) : ℂ) := by
  have hE' : (E : ℂ) ≠ 0 := by exact_mod_cast hE
  have hf : f0 a y = -((SS a y : ℝ) : ℂ) / DD a y := by rw [f0, num_eq]
  -- pure algebra: D^2 G1 / E^2 = S^2 + H^2 + S D / E^2
  have h1 : DD a y ^ 2 * G1 a y E H / (E : ℂ) ^ 2 =
      ((SS a y : ℝ) : ℂ) ^ 2 + H ^ 2 + ((SS a y : ℝ) : ℂ) * DD a y / (E : ℂ) ^ 2 := by
    rw [G1, hf, c0]; field_simp; ring
  rw [h1, DD_eq]; simp only [SS]; push_cast; field_simp; ring

/-! ## 1b. The Curzon trace identities -/

section Curzon
variable {K : Type*} [Field K]

/-- M0 = [[1,1],[0,1]] -/
def M0 : Matrix (Fin 2) (Fin 2) K := !![1, 1; 0, 1]
/-- its inverse [[1,-1],[0,1]] -/
def M0i : Matrix (Fin 2) (Fin 2) K := !![1, -1; 0, 1]
/-- M_a = [[u, -(1+u^2)/tau],[tau, -u]] -/
def Ma (u τ : K) : Matrix (Fin 2) (Fin 2) K := !![u, -(1 + u ^ 2) / τ; τ, -u]

lemma M0_mul_M0i : (M0 : Matrix (Fin 2) (Fin 2) K) * M0i = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [M0, M0i, Matrix.mul_apply, Fin.sum_univ_two]

/-- M0i really is M0⁻¹ -/
lemma M0_inv : (M0 : Matrix (Fin 2) (Fin 2) K)⁻¹ = M0i := Matrix.inv_eq_right_inv M0_mul_M0i

/-- g_k = M0^k M_a M0^(-k), for k = 0, 1, 2 (written with M0⁻¹ = M0i, `M0_inv`) -/
def g0 (u τ : K) : Matrix (Fin 2) (Fin 2) K := Ma u τ
def g1 (u τ : K) : Matrix (Fin 2) (Fin 2) K := M0 * Ma u τ * M0i
def g2 (u τ : K) : Matrix (Fin 2) (Fin 2) K := M0 ^ 2 * Ma u τ * M0i ^ 2
def h1 (u τ : K) : Matrix (Fin 2) (Fin 2) K := g0 u τ * g1 u τ
def h2 (u τ : K) : Matrix (Fin 2) (Fin 2) K := g0 u τ * g2 u τ

/-- the g_k are the conjugates with the true inverse -/
lemma g1_conj (u τ : K) : g1 u τ = M0 * Ma u τ * M0⁻¹ := by rw [M0_inv]; rfl
lemma g2_conj (u τ : K) : g2 u τ = M0 ^ 2 * Ma u τ * (M0 ^ 2)⁻¹ := by
  rw [← Matrix.inv_pow', M0_inv]; rfl

lemma det_Ma (u τ : K) (hτ : τ ≠ 0) : (Ma u τ).det = 1 := by
  rw [Ma, Matrix.det_fin_two_of]; field_simp; ring

/-- **1b(i).** tr h1 = -2 - tau^2 -/
theorem curzon_tr_h1 (u τ : K) (hτ : τ ≠ 0) : (h1 u τ).trace = -2 - τ ^ 2 := by
  simp only [h1, g0, g1, Ma, M0, M0i, Matrix.trace_fin_two, Matrix.mul_apply, Fin.sum_univ_two,
    Matrix.of_apply, Matrix.cons_val', Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.empty_val',
    Matrix.cons_val_fin_one]
  field_simp; ring

/-- **1b(ii).** tr h2 = -2 - 4 tau^2 -/
theorem curzon_tr_h2 (u τ : K) (hτ : τ ≠ 0) : (h2 u τ).trace = -2 - 4 * τ ^ 2 := by
  simp only [h2, g0, g2, Ma, M0, M0i, pow_two, Matrix.trace_fin_two, Matrix.mul_apply, Fin.sum_univ_two,
    Matrix.of_apply, Matrix.cons_val', Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.empty_val',
    Matrix.cons_val_fin_one]
  field_simp; ring

lemma det_h1 (u τ : K) (hτ : τ ≠ 0) : (h1 u τ).det = 1 := by
  have h0 : (M0 : Matrix (Fin 2) (Fin 2) K).det = 1 := by simp [M0, Matrix.det_fin_two_of]
  have hi : (M0i : Matrix (Fin 2) (Fin 2) K).det = 1 := by simp [M0i, Matrix.det_fin_two_of]
  simp only [h1, g0, g1, Matrix.det_mul, det_Ma u τ hτ, h0, hi]; ring

lemma det_h2 (u τ : K) (hτ : τ ≠ 0) : (h2 u τ).det = 1 := by
  have h0 : (M0 : Matrix (Fin 2) (Fin 2) K).det = 1 := by simp [M0, Matrix.det_fin_two_of]
  have hi : (M0i : Matrix (Fin 2) (Fin 2) K).det = 1 := by simp [M0i, Matrix.det_fin_two_of]
  simp only [h2, g0, g2, Matrix.det_mul, Matrix.det_pow, det_Ma u τ hτ, h0, hi]; ring

/-- for det = 1 the inverse is the adjugate -/
lemma inv_of_det_one (A : Matrix (Fin 2) (Fin 2) K) (h : A.det = 1) : A⁻¹ = A.adjugate := by
  rw [Matrix.inv_def, h]; simp

/-- **1b(iii).** tr[h1, h2] - 2 = -4 tau^6, with [h1, h2] = h1 h2 h1⁻¹ h2⁻¹ -/
theorem curzon_tr_comm (u τ : K) (hτ : τ ≠ 0) :
    (h1 u τ * h2 u τ * (h1 u τ)⁻¹ * (h2 u τ)⁻¹).trace - 2 = -4 * τ ^ 6 := by
  rw [inv_of_det_one _ (det_h1 u τ hτ), inv_of_det_one _ (det_h2 u τ hτ)]
  simp only [h1, h2, g0, g1, g2, Ma, M0, M0i, pow_two, Matrix.adjugate_fin_two, Matrix.trace_fin_two,
    Matrix.mul_apply, Fin.sum_univ_two, Matrix.of_apply, Matrix.cons_val', Matrix.cons_val_zero,
    Matrix.cons_val_one, Matrix.empty_val', Matrix.cons_val_fin_one]
  field_simp; ring

end Curzon

/-! ## 2. The T19 case-split glue

  H := -(z^2 + a^2) c0 at z = 1 + i y, H = H_r + i H_i. The T19 certificates are stated for rescalings of H by
  POSITIVE REAL factors (H~ = H/a, H~_theta = H/(a sqrt(1+s)), s > 0); `rescale_*` below show that each certified
  inequality is equivalent to (or implies) the corresponding statement about H itself. -/

/-- **The certified facts, as hypotheses** (from the T19 interval certificates, NOT proved in Lean), stated for H:
    Case 1 (k <= 0, any y):          Re(H^2) > 0;
    Case 2b (0 < k < 30/7, |y| < a): Re H > |Im H|;
    Case 2a (0 < k < 30/7, |y| >= a): |Im H| < a.
    The certificates cover every (k, y), so at least one disjunct holds. -/
def CertCases (a y : ℝ) (H : ℂ) : Prop :=
  0 < (H ^ 2).re ∨ |H.im| < H.re ∨ (a ≤ |y| ∧ |H.im| < a)

/-- rescaling by a positive real does not change the Case 1 condition -/
lemma rescale_case1 (H : ℂ) (c : ℝ) (hc : 0 < c) : 0 < ((H / (c : ℂ)) ^ 2).re ↔ 0 < (H ^ 2).re := by
  have : ((H / (c : ℂ)) ^ 2).re = (H ^ 2).re / c ^ 2 := by
    rw [div_pow, ← Complex.ofReal_pow, Complex.div_ofReal_re]
  rw [this]; exact div_pos_iff_of_pos_right (by positivity)

/-- rescaling by a positive real does not change the Case 2b condition -/
lemma rescale_case2b (H : ℂ) (c : ℝ) (hc : 0 < c) :
    |(H / (c : ℂ)).im| < (H / (c : ℂ)).re ↔ |H.im| < H.re := by
  rw [Complex.div_ofReal_im, Complex.div_ofReal_re, abs_div, abs_of_pos hc]
  exact div_lt_div_iff_of_pos_right hc

/-- the Case 2a certificate |Im(H/a)| < 1 is |Im H| < a -/
lemma rescale_case2a (H : ℂ) (a : ℝ) (ha : 0 < a) : |(H / (a : ℂ)).im| < 1 ↔ |H.im| < a := by
  rw [Complex.div_ofReal_im, abs_div, abs_of_pos ha, div_lt_one ha]

lemma SS_pos (a y : ℝ) (ha0 : 0 < a) (ha1 : a < 1) : 0 < SS a y := by
  unfold SS; nlinarith [sq_nonneg y]

/-- S >= 1 when |y| >= a -/
lemma SS_ge_one (a y : ℝ) (ha0 : 0 < a) (hy : a ≤ |y|) : 1 ≤ SS a y := by
  unfold SS
  have : a ^ 2 ≤ y ^ 2 := by
    rw [← sq_abs y]; exact pow_le_pow_left₀ ha0.le hy 2
  linarith

/-- convexity: (1-t) S^2 + 2 t S >= min(S^2, 2S) for t in [0,1] -/
lemma convex_min (S t : ℝ) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    min (S ^ 2) (2 * S) ≤ (1 - t) * S ^ 2 + 2 * t * S := by
  have h1 := min_le_left (S ^ 2) (2 * S); have h2 := min_le_right (S ^ 2) (2 * S)
  nlinarith [mul_le_mul_of_nonneg_left h1 (by linarith : (0:ℝ) ≤ 1 - t), mul_le_mul_of_nonneg_left h2 ht0]

/-- **2(i).** the glue inequality: min(S^2, 2S) + H_r^2 - H_i^2 > 0 in every certified case -/
theorem glue_min_pos (a y : ℝ) (H : ℂ) (ha0 : 0 < a) (ha1 : a < 1) (hc : CertCases a y H) :
    0 < min (SS a y ^ 2) (2 * SS a y) + (H.re ^ 2 - H.im ^ 2) := by
  have hS := SS_pos a y ha0 ha1
  have hmin : 0 < min (SS a y ^ 2) (2 * SS a y) := lt_min (by positivity) (by linarith)
  have hre : (H ^ 2).re = H.re ^ 2 - H.im ^ 2 := by simp [pow_two, Complex.mul_re]
  rcases hc with h | hr | ⟨hy, hi⟩
  · -- Case 1
    rw [← hre]; linarith
  · -- Case 2b: H_r > |H_i| >= 0, so H_r^2 > H_i^2
    have h0 := abs_nonneg H.im
    have : H.im ^ 2 < H.re ^ 2 := by rw [← sq_abs H.im]; nlinarith
    linarith
  · -- Case 2a: H_i^2 < a^2 < 1 <= min(S^2, 2S), and H_r^2 >= 0
    have hS1 := SS_ge_one a y ha0 hy
    have hm1 : 1 ≤ min (SS a y ^ 2) (2 * SS a y) := le_min (by nlinarith) (by linarith)
    have hi2 : H.im ^ 2 < 1 := by
      have := abs_nonneg H.im
      rw [← sq_abs H.im]; nlinarith
    nlinarith [sq_nonneg H.re]

/-- **2(ii).** the real part of the right-hand side of 1a is positive, for t in (0,1]
    (the 2 i y t S term is purely imaginary) -/
theorem glue_re_pos (a y t : ℝ) (H : ℂ) (ha0 : 0 < a) (ha1 : a < 1) (ht0 : 0 < t) (ht1 : t ≤ 1)
    (hc : CertCases a y H) :
    0 < ((1 - (t : ℂ)) * ((SS a y : ℝ) : ℂ) ^ 2 + 2 * (t : ℂ) * ((SS a y : ℝ) : ℂ) + H ^ 2
          + 2 * I * (y : ℂ) * (t : ℂ) * ((SS a y : ℝ) : ℂ)).re := by
  have hre : ((1 - (t : ℂ)) * ((SS a y : ℝ) : ℂ) ^ 2 + 2 * (t : ℂ) * ((SS a y : ℝ) : ℂ) + H ^ 2
          + 2 * I * (y : ℂ) * (t : ℂ) * ((SS a y : ℝ) : ℂ)).re
        = (1 - t) * SS a y ^ 2 + 2 * t * SS a y + (H.re ^ 2 - H.im ^ 2) := by
    simp [pow_two, Complex.mul_re, Complex.mul_im]
  rw [hre]
  have := convex_min (SS a y) t ht0.le ht1
  have := glue_min_pos a y H ha0 ha1 hc
  linarith

/-- **2(iii).** the conclusion: Re(D^2 G1 / E^2) > 0 and so G1 != 0, for every a in (0,1), real y, real E with
    t = 1/E^2 in (0,1], D != 0, and complex H in a certified case. -/
theorem re_pos (a y E : ℝ) (H : ℂ) (ha0 : 0 < a) (ha1 : a < 1) (hE : E ≠ 0) (hE1 : 1 ≤ E ^ 2)
    (hD : DD a y ≠ 0) (hc : CertCases a y H) : 0 < (DD a y ^ 2 * G1 a y E H / (E : ℂ) ^ 2).re := by
  have ht0 : 0 < 1 / E ^ 2 := by positivity
  have ht1 : 1 / E ^ 2 ≤ 1 := by rw [div_le_one (by positivity)]; exact hE1
  have hpos := glue_re_pos a y (1 / E ^ 2) H ha0 ha1 ht0 ht1 hc
  rw [elim_identity a y E H hE hD]
  push_cast at hpos ⊢
  exact hpos

theorem G1_ne_zero (a y E : ℝ) (H : ℂ) (ha0 : 0 < a) (ha1 : a < 1) (hE : E ≠ 0) (hE1 : 1 ≤ E ^ 2)
    (hD : DD a y ≠ 0) (hc : CertCases a y H) : G1 a y E H ≠ 0 := by
  intro h0
  have := re_pos a y E H ha0 ha1 hE hE1 hD hc
  rw [h0] at this; simp at this

/-! ## 3. The K5 Theorem 1 constants (pure arithmetic, nothing assumed)
  Source: neon_work/onlykerr T21/T28 summaries (T24: the referee's repair of the false "> 28" bound). -/

/-- **3a.** for integer m with |m| >= 2: 3m^2/(3m^2 - 4) <= 3/2 -/
theorem k5_3a (m : ℤ) (hm : 2 ≤ |m|) : (3 * (m : ℝ) ^ 2) / (3 * (m : ℝ) ^ 2 - 4) ≤ 3 / 2 := by
  have h4 : (4 : ℝ) ≤ (m : ℝ) ^ 2 := by
    have : (2 : ℝ) ≤ |(m : ℝ)| := by exact_mod_cast hm
    rw [← sq_abs]; nlinarith
  rw [div_le_iff₀ (by linarith)]; linarith

/-- **3b.** for complex eta with |eta| <= 1/15: |2 eta + eta^2| <= 31/225, and (3/2)(31/225) = 31/150 -/
theorem k5_3b (η : ℂ) (hη : ‖η‖ ≤ 1 / 15) : ‖2 * η + η ^ 2‖ ≤ 31 / 225 := by
  have h0 := norm_nonneg η
  calc ‖2 * η + η ^ 2‖ ≤ ‖2 * η‖ + ‖η ^ 2‖ := norm_add_le _ _
    _ = 2 * ‖η‖ + ‖η‖ ^ 2 := by rw [norm_mul, norm_pow]; norm_num
    _ ≤ 31 / 225 := by nlinarith

theorem k5_3b' : (3 / 2 : ℝ) * (31 / 225) = 31 / 150 := by norm_num

/-- **3c.** r = 323/2400: (1/2)(31/150 + r^2) <= r, and r < 1 -/
theorem k5_3c : (1 / 2 : ℝ) * (31 / 150 + (323 / 2400) ^ 2) ≤ 323 / 2400 ∧ (323 / 2400 : ℝ) < 1 := by
  constructor <;> norm_num

/-- **3d.** exp(pi sqrt 2 (1 - 323/2400)) > 46 -/
theorem k5_3d : (46 : ℝ) < Real.exp (Real.pi * Real.sqrt 2 * (1 - 323 / 2400)) := by
  have hpi := Real.pi_gt_d6
  have hs : (1.4142 : ℝ) < Real.sqrt 2 := by
    rw [Real.lt_sqrt (by norm_num)]; norm_num
  -- the exponent exceeds 3 + 4 y with y = 0.21122
  set y : ℝ := 0.21122
  have harg : 3 + 4 * y < Real.pi * Real.sqrt 2 * (1 - 323 / 2400) := by
    have : (3.141592 : ℝ) * 1.4142 < Real.pi * Real.sqrt 2 := by
      have := mul_lt_mul'' hpi hs (by norm_num) (by norm_num); linarith
    simp only [y]; nlinarith
  have hsplit : Real.exp (3 + 4 * y) = Real.exp 1 ^ 3 * Real.exp y ^ 4 := by
    rw [Real.exp_add, ← Real.exp_nat_mul, ← Real.exp_nat_mul]; norm_num
  have he := Real.exp_one_gt_d9
  have hy : (1 + y + y ^ 2 / 2 : ℝ) ≤ Real.exp y := Real.quadratic_le_exp_of_nonneg (by norm_num [y])
  have hy0 : (0 : ℝ) ≤ 1 + y + y ^ 2 / 2 := by norm_num [y]
  have h3 : (2.7182818283 : ℝ) ^ 3 < Real.exp 1 ^ 3 := by gcongr
  have h4 : (1 + y + y ^ 2 / 2 : ℝ) ^ 4 ≤ Real.exp y ^ 4 := by gcongr
  have hnum : (46 : ℝ) < 2.7182818283 ^ 3 * (1 + y + y ^ 2 / 2) ^ 4 := by norm_num [y]
  calc (46 : ℝ) < 2.7182818283 ^ 3 * (1 + y + y ^ 2 / 2) ^ 4 := hnum
    _ ≤ Real.exp 1 ^ 3 * Real.exp y ^ 4 := by
        apply mul_le_mul h3.le h4 (by positivity) (by positivity)
    _ = Real.exp (3 + 4 * y) := hsplit.symm
    _ < Real.exp (Real.pi * Real.sqrt 2 * (1 - 323 / 2400)) := Real.exp_lt_exp.mpr harg

end OnlyKerr
