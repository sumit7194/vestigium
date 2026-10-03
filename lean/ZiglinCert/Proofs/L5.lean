import Mathlib
open Matrix Complex
def InRealSegment (z : ℂ) (a b : ℝ) : Prop := z.im = 0 ∧ a ≤ z.re ∧ z.re ≤ b

theorem L5_gl2_restatement (g : Matrix (Fin 2) (Fin 2) ℂ) (s : ℂ) (hs : s ^ 2 = g.det) (hs0 : s ≠ 0) :
    InRealSegment (g.trace / s) (-2) 2 ↔ InRealSegment (g.trace ^ 2 / g.det) 0 4 := by
  have key : g.trace ^ 2 / g.det = (g.trace / s) ^ 2 := by
    rw [← hs, div_pow]
  rw [key]
  generalize g.trace / s = x
  unfold InRealSegment
  simp only [sq, Complex.mul_re, Complex.mul_im]
  constructor
  · rintro ⟨him, h1, h2⟩
    refine ⟨by rw [him]; ring, by rw [him]; nlinarith, by rw [him]; nlinarith⟩
  · rintro ⟨him, h1, h2⟩
    have hprod : x.re * x.im = 0 := by linarith [mul_comm x.im x.re]
    have him0 : x.im = 0 := by
      rcases mul_eq_zero.mp hprod with h | h
      · rw [h] at h1
        have : x.im * x.im = 0 := by nlinarith [mul_self_nonneg x.im]
        exact mul_self_eq_zero.mp this
      · exact h
    rw [him0] at h2
    exact ⟨him0, by nlinarith, by nlinarith⟩
