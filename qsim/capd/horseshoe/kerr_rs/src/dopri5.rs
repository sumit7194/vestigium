//! Dormand-Prince 5(4) with Hairer's continuous extension (DOPRI5 dense output), adaptive step, FSAL.
//! Error norm: RMS of e_i / (atol + rtol * max(|y0_i|, |y1_i|)); step factor 0.9 err^(-1/5) clamped to [0.2, 10].
const A21: f64 = 1.0 / 5.0;
const A31: f64 = 3.0 / 40.0; const A32: f64 = 9.0 / 40.0;
const A41: f64 = 44.0 / 45.0; const A42: f64 = -56.0 / 15.0; const A43: f64 = 32.0 / 9.0;
const A51: f64 = 19372.0 / 6561.0; const A52: f64 = -25360.0 / 2187.0; const A53: f64 = 64448.0 / 6561.0; const A54: f64 = -212.0 / 729.0;
const A61: f64 = 9017.0 / 3168.0; const A62: f64 = -355.0 / 33.0; const A63: f64 = 46732.0 / 5247.0; const A64: f64 = 49.0 / 176.0; const A65: f64 = -5103.0 / 18656.0;
const B1: f64 = 35.0 / 384.0; const B3: f64 = 500.0 / 1113.0; const B4: f64 = 125.0 / 192.0; const B5: f64 = -2187.0 / 6784.0; const B6: f64 = 11.0 / 84.0;
const E1: f64 = 71.0 / 57600.0; const E3: f64 = -71.0 / 16695.0; const E4: f64 = 71.0 / 1920.0; const E5: f64 = -17253.0 / 339200.0; const E6: f64 = 22.0 / 525.0; const E7: f64 = -1.0 / 40.0;
const D1: f64 = -12715105075.0 / 11282082432.0; const D3: f64 = 87487479700.0 / 32700410799.0; const D4C: f64 = -10690763975.0 / 1880347072.0;
const D5: f64 = 701980252875.0 / 199316789632.0; const D6: f64 = -1453857185.0 / 822651844.0; const D7: f64 = 69997945.0 / 29380423.0;

/// one accepted step: start time and state, length, and the dense-output coefficients
pub struct Step<const N: usize> { pub t0: f64, pub h: f64, pub r: [[f64; N]; 5] }
impl<const N: usize> Step<N> {
    /// dense output at local time th = (t - t0) / h in [0, 1]
    pub fn at_theta(&self, th: f64) -> [f64; N] {
        let th1 = 1.0 - th; let mut y = [0.0; N];
        for i in 0..N { y[i] = self.r[0][i] + th * (self.r[1][i] + th1 * (self.r[2][i] + th * (self.r[3][i] + th1 * self.r[4][i]))); }
        y
    }
}

/// a single Dormand-Prince attempt of length h from (y, k1 = f(y)): (y1, k7 = f(y1), err, dense coefficients)
pub fn attempt<const N: usize, F: Fn(&[f64; N], &mut [f64; N])>(f: &F, y: &[f64; N], k1: &[f64; N], h: f64, rtol: f64, atol: f64)
    -> ([f64; N], [f64; N], f64, [[f64; N]; 5]) {
    let mut z = [0.0; N]; let (mut k2, mut k3, mut k4, mut k5, mut k6, mut k7) = ([0.0; N], [0.0; N], [0.0; N], [0.0; N], [0.0; N], [0.0; N]);
    for i in 0..N { z[i] = y[i] + h * A21 * k1[i]; } f(&z, &mut k2);
    for i in 0..N { z[i] = y[i] + h * (A31 * k1[i] + A32 * k2[i]); } f(&z, &mut k3);
    for i in 0..N { z[i] = y[i] + h * (A41 * k1[i] + A42 * k2[i] + A43 * k3[i]); } f(&z, &mut k4);
    for i in 0..N { z[i] = y[i] + h * (A51 * k1[i] + A52 * k2[i] + A53 * k3[i] + A54 * k4[i]); } f(&z, &mut k5);
    for i in 0..N { z[i] = y[i] + h * (A61 * k1[i] + A62 * k2[i] + A63 * k3[i] + A64 * k4[i] + A65 * k5[i]); } f(&z, &mut k6);
    let mut y1 = [0.0; N];
    for i in 0..N { y1[i] = y[i] + h * (B1 * k1[i] + B3 * k3[i] + B4 * k4[i] + B5 * k5[i] + B6 * k6[i]); }
    f(&y1, &mut k7);
    let mut err = 0.0;
    for i in 0..N {
        let e = h * (E1 * k1[i] + E3 * k3[i] + E4 * k4[i] + E5 * k5[i] + E6 * k6[i] + E7 * k7[i]);
        let sc = atol + rtol * y[i].abs().max(y1[i].abs()); err += (e / sc) * (e / sc);
    }
    let err = (err / N as f64).sqrt();
    let mut r = [[0.0; N]; 5];
    for i in 0..N {
        let ydiff = y1[i] - y[i]; let bspl = h * k1[i] - ydiff;
        r[0][i] = y[i]; r[1][i] = ydiff; r[2][i] = bspl; r[3][i] = ydiff - h * k7[i] - bspl;
        r[4][i] = h * (D1 * k1[i] + D3 * k3[i] + D4C * k4[i] + D5 * k5[i] + D6 * k6[i] + D7 * k7[i]);
    }
    (y1, k7, err, r)
}

pub struct Dopri<const N: usize, F: Fn(&[f64; N], &mut [f64; N])> { pub f: F, pub rtol: f64, pub atol: f64, pub t: f64, pub y: [f64; N], pub h: f64, k1: [f64; N] }
impl<const N: usize, F: Fn(&[f64; N], &mut [f64; N])> Dopri<N, F> {
    pub fn new(f: F, y0: [f64; N], h0: f64, rtol: f64, atol: f64) -> Self {
        let mut k1 = [0.0; N]; f(&y0, &mut k1); Dopri { f, rtol, atol, t: 0.0, y: y0, h: h0, k1 }
    }
    /// one ACCEPTED step; returns the dense-output record of it, or None on step-size underflow (no panic: a panic
    /// cannot cross the C ABI)
    pub fn step(&mut self) -> Option<Step<N>> {
        loop {
            let h = self.h;
            let (y1, k7, err, r) = attempt(&self.f, &self.y, &self.k1, h, self.rtol, self.atol);
            let fac = if err == 0.0 { 10.0 } else { (0.9 * err.powf(-0.2)).clamp(0.2, 10.0) };
            if err <= 1.0 && err.is_finite() {
                let s = Step { t0: self.t, h, r };
                self.t += h; self.y = y1; self.k1 = k7; self.h = h * fac;
                return Some(s);
            }
            if !err.is_finite() { self.h = h * 0.2; } else { self.h = h * fac.min(1.0); }
            if !(self.h.abs() >= 1e-300) { return None; }
        }
    }
    /// undo: restart from the start of a previously accepted step s, with step length h
    pub fn reset_to(&mut self, s: &Step<N>, h: f64) {
        self.t = s.t0; self.y = s.r[0]; (self.f)(&self.y, &mut self.k1); self.h = h;
    }
    /// a real integration from (y0 at the step start) over length len, in 2^m equal substeps that must each pass the
    /// error test; None if no m <= 10 passes
    pub fn integrate_exact(&self, y0: &[f64; N], len: f64) -> Option<[f64; N]> {
        'outer: for m in 0..=10 {
            let n = 1usize << m; let hs = len / n as f64; let mut y = *y0; let mut k = [0.0; N]; (self.f)(&y, &mut k);
            for _ in 0..n {
                let (y1, k7, err, _) = attempt(&self.f, &y, &k, hs, self.rtol, self.atol);
                if !(err <= 1.0) { continue 'outer; }
                y = y1; k = k7;
            }
            return Some(y);
        }
        None
    }
}
