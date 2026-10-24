//! The scalar trait the generated field is written over: f64, and D4 (value + gradient in 4 variables, forward-mode
//! automatic differentiation: exact derivatives of the same expression, no finite differences).
use std::ops::{Add, Div, Mul, Neg, Sub};

pub trait Sc: Copy + Add<Output = Self> + Sub<Output = Self> + Mul<Output = Self> + Div<Output = Self> + Neg<Output = Self> {
    fn from_i(n: i64) -> Self;
    fn sqrt_(self) -> Self;
    fn exp_(self) -> Self;
}
#[inline] pub fn sqrt<S: Sc>(x: S) -> S { x.sqrt_() }
#[inline] pub fn mn_exp<S: Sc>(x: S) -> S { x.exp_() }

impl Sc for f64 {
    #[inline] fn from_i(n: i64) -> Self { n as f64 }
    #[inline] fn sqrt_(self) -> Self { self.sqrt() }
    #[inline] fn exp_(self) -> Self { self.exp() }
}

#[derive(Clone, Copy, Debug)]
pub struct D4 { pub v: f64, pub d: [f64; 4] }
impl D4 {
    pub fn c(v: f64) -> Self { D4 { v, d: [0.0; 4] } }
    pub fn var(v: f64, i: usize) -> Self { let mut d = [0.0; 4]; d[i] = 1.0; D4 { v, d } }
}
impl Add for D4 { type Output = D4; #[inline] fn add(self, b: D4) -> D4 { let mut r = self; r.v += b.v; for i in 0..4 { r.d[i] += b.d[i]; } r } }
impl Sub for D4 { type Output = D4; #[inline] fn sub(self, b: D4) -> D4 { let mut r = self; r.v -= b.v; for i in 0..4 { r.d[i] -= b.d[i]; } r } }
impl Neg for D4 { type Output = D4; #[inline] fn neg(self) -> D4 { let mut r = self; r.v = -r.v; for i in 0..4 { r.d[i] = -r.d[i]; } r } }
impl Mul for D4 { type Output = D4; #[inline] fn mul(self, b: D4) -> D4 { let mut r = D4::c(self.v * b.v); for i in 0..4 { r.d[i] = self.d[i] * b.v + self.v * b.d[i]; } r } }
impl Div for D4 { type Output = D4; #[inline] fn div(self, b: D4) -> D4 { let mut r = D4::c(self.v / b.v); for i in 0..4 { r.d[i] = (self.d[i] * b.v - self.v * b.d[i]) / (b.v * b.v); } r } }
impl Sc for D4 {
    #[inline] fn from_i(n: i64) -> Self { D4::c(n as f64) }
    #[inline] fn sqrt_(self) -> Self { let s = self.v.sqrt(); let mut r = D4::c(s); for i in 0..4 { r.d[i] = self.d[i] / (2.0 * s); } r }
    #[inline] fn exp_(self) -> Self { let e = self.v.exp(); let mut r = D4::c(e); for i in 0..4 { r.d[i] = self.d[i] * e; } r }
}
