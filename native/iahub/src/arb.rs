//! Safe owned wrappers over the C shim (opaque handles). No FLINT layout is assumed in Rust.
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int, c_long};

#[repr(C)]
pub struct RawBall {
    _p: [u8; 0],
}
#[repr(C)]
pub struct RawSer {
    _p: [u8; 0],
}

extern "C" {
    fn ib_new() -> *mut RawBall;
    fn ib_free(b: *mut RawBall);
    fn ib_set(r: *mut RawBall, a: *const RawBall);
    fn ib_set_si(r: *mut RawBall, re: c_long, im: c_long);
    fn ib_set_rational(r: *mut RawBall, s: *const c_char, prec: c_long) -> c_int;
    fn ib_set_d_d(r: *mut RawBall, re: c_double, im: c_double);
    fn ib_set_box(r: *mut RawBall, re: c_double, im: c_double, rad: c_double);
    fn ib_add(r: *mut RawBall, a: *const RawBall, b: *const RawBall, prec: c_long);
    fn ib_sub(r: *mut RawBall, a: *const RawBall, b: *const RawBall, prec: c_long);
    fn ib_mul(r: *mut RawBall, a: *const RawBall, b: *const RawBall, prec: c_long);
    fn ib_div(r: *mut RawBall, a: *const RawBall, b: *const RawBall, prec: c_long);
    fn ib_neg(r: *mut RawBall, a: *const RawBall);
    fn ib_inv(r: *mut RawBall, a: *const RawBall, prec: c_long);
    fn ib_exp(r: *mut RawBall, a: *const RawBall, prec: c_long);
    fn ib_is_finite(a: *const RawBall) -> c_int;
    fn ib_abs_upper(a: *const RawBall, prec: c_long) -> c_double;
    fn ib_abs_lower(a: *const RawBall, prec: c_long) -> c_double;
    fn ib_add_error(r: *mut RawBall, e: c_double);
    fn ib_re_gt(a: *const RawBall, c: c_double) -> c_int;
    fn ib_re_lt(a: *const RawBall, c: c_double) -> c_int;
    fn ib_im_ne0(a: *const RawBall) -> c_int;
    fn ib_contains_zero(a: *const RawBall) -> c_int;
    fn ib_get_str(a: *const RawBall, digits: c_long) -> *mut c_char;
    fn ib_free_str(s: *mut c_char);

    fn is_new() -> *mut RawSer;
    fn is_free(s: *mut RawSer);
    fn is_set(r: *mut RawSer, a: *const RawSer);
    fn is_set_ball(r: *mut RawSer, c: *const RawBall);
    fn is_set_var(r: *mut RawSer, z0: *const RawBall);
    fn is_add(r: *mut RawSer, a: *const RawSer, b: *const RawSer, n: c_long, prec: c_long);
    fn is_sub(r: *mut RawSer, a: *const RawSer, b: *const RawSer, n: c_long, prec: c_long);
    fn is_mul(r: *mut RawSer, a: *const RawSer, b: *const RawSer, n: c_long, prec: c_long);
    fn is_neg(r: *mut RawSer, a: *const RawSer);
    fn is_inv(r: *mut RawSer, a: *const RawSer, n: c_long, prec: c_long);
    fn is_div(r: *mut RawSer, a: *const RawSer, b: *const RawSer, n: c_long, prec: c_long);
    fn is_exp(r: *mut RawSer, a: *const RawSer, n: c_long, prec: c_long);
    fn is_get_coeff(c: *mut RawBall, a: *const RawSer, k: c_long);
}

/// A complex Arb ball.
pub struct Ball(*mut RawBall);
// Each Ball is owned by one thread at a time; Arb objects are independent heap allocations.
unsafe impl Send for Ball {}

impl Drop for Ball {
    fn drop(&mut self) {
        unsafe { ib_free(self.0) }
    }
}
impl Clone for Ball {
    fn clone(&self) -> Self {
        let b = Ball::zero();
        unsafe { ib_set(b.0, self.0) };
        b
    }
}

impl Ball {
    pub fn zero() -> Self {
        Ball(unsafe { ib_new() })
    }
    pub fn si(re: i64, im: i64) -> Self {
        let b = Ball::zero();
        unsafe { ib_set_si(b.0, re as c_long, im as c_long) };
        b
    }
    /// exact rational "p/q" or integer string
    pub fn rational(s: &str, prec: i64) -> Self {
        let b = Ball::zero();
        let c = CString::new(s).unwrap();
        let bad = unsafe { ib_set_rational(b.0, c.as_ptr(), prec as c_long) };
        assert!(bad == 0, "bad rational {s}");
        b
    }
    /// exact dyadic complex point
    pub fn point(re: f64, im: f64) -> Self {
        let b = Ball::zero();
        unsafe { ib_set_d_d(b.0, re, im) };
        b
    }
    /// box containing the disk |z - c| <= rad
    pub fn boxed(re: f64, im: f64, rad: f64) -> Self {
        let b = Ball::zero();
        unsafe { ib_set_box(b.0, re, im, rad) };
        b
    }
    pub fn add(&self, o: &Ball, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_add(r.0, self.0, o.0, prec as c_long) };
        r
    }
    pub fn sub(&self, o: &Ball, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_sub(r.0, self.0, o.0, prec as c_long) };
        r
    }
    pub fn mul(&self, o: &Ball, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_mul(r.0, self.0, o.0, prec as c_long) };
        r
    }
    pub fn div(&self, o: &Ball, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_div(r.0, self.0, o.0, prec as c_long) };
        r
    }
    pub fn neg(&self) -> Ball {
        let r = Ball::zero();
        unsafe { ib_neg(r.0, self.0) };
        r
    }
    pub fn inv(&self, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_inv(r.0, self.0, prec as c_long) };
        r
    }
    pub fn exp(&self, prec: i64) -> Ball {
        let r = Ball::zero();
        unsafe { ib_exp(r.0, self.0, prec as c_long) };
        r
    }
    pub fn is_finite(&self) -> bool {
        unsafe { ib_is_finite(self.0) != 0 }
    }
    /// rigorous upper bound of |self| (rounded up), +inf if not finite
    pub fn abs_upper(&self, prec: i64) -> f64 {
        unsafe { ib_abs_upper(self.0, prec as c_long) }
    }
    /// rigorous lower bound of |self| (rounded down)
    pub fn abs_lower(&self, prec: i64) -> f64 {
        unsafe { ib_abs_lower(self.0, prec as c_long) }
    }
    pub fn add_error(&mut self, e: f64) {
        unsafe { ib_add_error(self.0, e) }
    }
    pub fn re_gt(&self, c: f64) -> bool {
        unsafe { ib_re_gt(self.0, c) != 0 }
    }
    pub fn re_lt(&self, c: f64) -> bool {
        unsafe { ib_re_lt(self.0, c) != 0 }
    }
    pub fn im_nonzero(&self) -> bool {
        unsafe { ib_im_ne0(self.0) != 0 }
    }
    pub fn contains_zero(&self) -> bool {
        unsafe { ib_contains_zero(self.0) != 0 }
    }
    pub fn to_str(&self, digits: i64) -> String {
        unsafe {
            let p = ib_get_str(self.0, digits as c_long);
            let s = CStr::from_ptr(p).to_string_lossy().into_owned();
            ib_free_str(p);
            s
        }
    }
}

/// A truncated complex power series (Arb acb_poly).
pub struct Ser(*mut RawSer);
unsafe impl Send for Ser {}

impl Drop for Ser {
    fn drop(&mut self) {
        unsafe { is_free(self.0) }
    }
}
impl Clone for Ser {
    fn clone(&self) -> Self {
        let s = Ser::new();
        unsafe { is_set(s.0, self.0) };
        s
    }
}

impl Ser {
    pub fn new() -> Self {
        Ser(unsafe { is_new() })
    }
    pub fn constant(c: &Ball) -> Self {
        let s = Ser::new();
        unsafe { is_set_ball(s.0, c.0) };
        s
    }
    /// the series of z0 + t
    pub fn var(z0: &Ball) -> Self {
        let s = Ser::new();
        unsafe { is_set_var(s.0, z0.0) };
        s
    }
    pub fn add(&self, o: &Ser, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_add(r.0, self.0, o.0, n as c_long, prec as c_long) };
        r
    }
    pub fn sub(&self, o: &Ser, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_sub(r.0, self.0, o.0, n as c_long, prec as c_long) };
        r
    }
    pub fn mul(&self, o: &Ser, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_mul(r.0, self.0, o.0, n as c_long, prec as c_long) };
        r
    }
    pub fn neg(&self) -> Ser {
        let r = Ser::new();
        unsafe { is_neg(r.0, self.0) };
        r
    }
    pub fn inv(&self, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_inv(r.0, self.0, n as c_long, prec as c_long) };
        r
    }
    pub fn div(&self, o: &Ser, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_div(r.0, self.0, o.0, n as c_long, prec as c_long) };
        r
    }
    pub fn exp(&self, n: i64, prec: i64) -> Ser {
        let r = Ser::new();
        unsafe { is_exp(r.0, self.0, n as c_long, prec as c_long) };
        r
    }
    pub fn coeff(&self, k: i64) -> Ball {
        let b = Ball::zero();
        unsafe { is_get_coeff(b.0, self.0, k as c_long) };
        b
    }
}
