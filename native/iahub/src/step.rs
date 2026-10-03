//! Certified Taylor step for a first-order linear system Y' = M(z) Y (PREREG_iahub_v2.md §1).
//!
//! One step z_a -> z_b, h = |z_b - z_a|, rho = 2h, rho' = 1.5 rho, rho'' = 1.5 rho'.
//!   * M_k: exact truncated-series coefficients of M = num/den at z_a (ball series arithmetic), k <= N.
//!   * sup ||M|| on D(z_a, rho'): CENTRED bound per entry,
//!       (sum_k |num_k| rho'^k + T_num) / (|den_0| - sum_{k>=1} |den_k| rho'^k - T_den),
//!     T = (crude box bound on D(z_a, rho''))·(2/3)^(N+1)/(1 - 2/3); the denominator must be certainly > 0.
//!   * m_k = ||M_k|| rho^k (k <= N, exact),  Mbar = max(max m_k, M'·(2/3)^(N+1)),  c = rho·Mbar <= cmax.
//!   * Y_0 = I, (n+1) Y_{n+1} = sum_{k<=n} M_k Y_{n-k}; b_n = ||Y_n|| rho^n, S_n = sum_{j<=n} b_j:
//!       b_{n+1} <= c S_n/(n+1)  =>  S_n <= S_N prod_{j=N+1}^{n} (1 + c/j) <= S_N (n/N)^c  for n > N.
//!     At |t| = rho/2:  tail = sum_{n>N} b_n 2^-n <= S_N sum_{n>N} (n/N)^c 2^-n
//!       <= S_N e^{c/N} 2^-(N+1) / (1 - theta),  theta = e^{c/(N+1)}/2 (ratio bound),  theta < 1 required.
//! All bound arithmetic is done in balls; only rigorous upper/lower bounds are extracted (abs_upper/abs_lower).
use crate::arb::{Ball, Ser};
use crate::slp::Slp;

pub type Mat = [[Ball; 2]; 2];

pub struct Sys {
    pub slp: Slp,
    /// (numerator register, denominator register) for each entry of M
    pub entries: [[(usize, usize); 2]; 2],
}

pub struct Params {
    pub n: i64,
    pub prec: i64,
    pub cmax: f64,
}

fn ident() -> Mat {
    [[Ball::si(1, 0), Ball::si(0, 0)], [Ball::si(0, 0), Ball::si(1, 0)]]
}

pub fn matmul(a: &Mat, b: &Mat, prec: i64) -> Mat {
    let e = |i: usize, j: usize| a[i][0].mul(&b[0][j], prec).add(&a[i][1].mul(&b[1][j], prec), prec);
    [[e(0, 0), e(0, 1)], [e(1, 0), e(1, 1)]]
}

/// rigorous upper bound of the infinity norm (max row sum of |entries|), as an exact ball
fn norm_inf(m: &Mat, prec: i64) -> Ball {
    let row = |i: usize| Ball::point(m[i][0].abs_upper(prec), 0.0).add(&Ball::point(m[i][1].abs_upper(prec), 0.0), prec);
    let (r0, r1) = (row(0), row(1));
    if r0.abs_upper(prec) >= r1.abs_upper(prec) { r0 } else { r1 }
}

fn powb(x: &Ball, k: i64, prec: i64) -> Ball {
    let mut r = Ball::si(1, 0);
    for _ in 0..k {
        r = r.mul(x, prec);
    }
    r
}

/// centred upper bound of sup |num/den| on D(za, rad); None if not certified
fn centred_sup(num: &Ser, den: &Ser, nbox: &Ball, dbox: &Ball, n: i64, rad: f64, prec: i64) -> Option<f64> {
    let mp2 = nbox.abs_upper(prec);
    let md2 = dbox.abs_upper(prec);
    if !mp2.is_finite() || !md2.is_finite() {
        return None;
    }
    let th = Ball::rational("2/3", prec);
    let tfac = powb(&th, n + 1, prec).div(&Ball::rational("1/3", prec), prec); // th^(N+1)/(1-th)
    let r = Ball::point(rad, 0.0);
    let mut num_sum = Ball::point(mp2, 0.0).mul(&tfac, prec);
    let mut rk = Ball::si(1, 0);
    for k in 0..n {
        num_sum = num_sum.add(&Ball::point(num.coeff(k).abs_upper(prec), 0.0).mul(&rk, prec), prec);
        rk = rk.mul(&r, prec);
    }
    let d0 = den.coeff(0).abs_lower(prec);
    let mut den_low = Ball::point(d0, 0.0).sub(&Ball::point(md2, 0.0).mul(&tfac, prec), prec);
    let mut rk = r.clone();
    for k in 1..n {
        den_low = den_low.sub(&Ball::point(den.coeff(k).abs_upper(prec), 0.0).mul(&rk, prec), prec);
        rk = rk.mul(&r, prec);
    }
    if !den_low.re_gt(0.0) {
        return None;
    }
    let dl = den_low.abs_lower(prec);
    if dl <= 0.0 {
        return None;
    }
    Some(Ball::point(num_sum.abs_upper(prec), 0.0).div(&Ball::point(dl, 0.0), prec).abs_upper(prec))
}

pub fn step(sys: &Sys, za: (f64, f64), zb: (f64, f64), p: &Params, bad: &[(f64, f64)]) -> Option<Mat> {
    let (n, prec) = (p.n, p.prec);
    let h = ((zb.0 - za.0).powi(2) + (zb.1 - za.1).powi(2)).sqrt();
    let rho = 2.0 * h;
    let rhop = 1.5 * rho;
    let rho2 = 1.5 * rhop;
    for b in bad {
        if ((za.0 - b.0).powi(2) + (za.1 - b.1).powi(2)).sqrt() <= 1.05 * rho2 {
            return None;
        }
    }
    let z0 = Ball::point(za.0, za.1);
    let regs = sys.slp.eval_series(&z0, n + 1, prec);
    let bregs = sys.slp.eval_ball(&Ball::boxed(za.0, za.1, rho2), prec);
    // entries: series and centred sup bounds
    let mut mser: Vec<Vec<Ser>> = Vec::new();
    let mut supm = [[0.0f64; 2]; 2];
    for i in 0..2 {
        let mut row = Vec::new();
        for j in 0..2 {
            let (ni, di) = sys.entries[i][j];
            if regs[di].coeff(0).contains_zero() {
                return None;
            }
            row.push(regs[ni].div(&regs[di], n + 1, prec));
            supm[i][j] = centred_sup(&regs[ni], &regs[di], &bregs[ni], &bregs[di], n + 1, rhop, prec)?;
        }
        mser.push(row);
    }
    let mprime = {
        let r0 = Ball::point(supm[0][0], 0.0).add(&Ball::point(supm[0][1], 0.0), prec).abs_upper(prec);
        let r1 = Ball::point(supm[1][0], 0.0).add(&Ball::point(supm[1][1], 0.0), prec).abs_upper(prec);
        r0.max(r1)
    };
    // coefficient matrices M_k and m_k = ||M_k|| rho^k
    let mk: Vec<Mat> = (0..=n)
        .map(|k| {
            [[mser[0][0].coeff(k), mser[0][1].coeff(k)], [mser[1][0].coeff(k), mser[1][1].coeff(k)]]
        })
        .collect();
    let rho_b = Ball::point(rho, 0.0);
    let mut mbar = Ball::point(mprime, 0.0).mul(&powb(&Ball::rational("2/3", prec), n + 1, prec), prec).abs_upper(prec);
    let mut rk = Ball::si(1, 0);
    for k in 0..=n {
        let v = norm_inf(&mk[k as usize], prec).mul(&rk, prec).abs_upper(prec);
        if v > mbar {
            mbar = v;
        }
        rk = rk.mul(&rho_b, prec);
    }
    let c = rho_b.mul(&Ball::point(mbar, 0.0), prec).abs_upper(prec);
    if !(c <= p.cmax) {
        return None;
    }
    // recursion Y_{n+1} = (1/(n+1)) sum_{k<=n} M_k Y_{n-k}
    let mut y: Vec<Mat> = vec![ident()];
    for m in 0..n {
        let mut acc: Mat = [[Ball::si(0, 0), Ball::si(0, 0)], [Ball::si(0, 0), Ball::si(0, 0)]];
        for k in 0..=m {
            let t = matmul(&mk[k as usize], &y[(m - k) as usize], prec);
            for i in 0..2 {
                for j in 0..2 {
                    acc[i][j] = acc[i][j].add(&t[i][j], prec);
                }
            }
        }
        let inv = Ball::rational(&format!("1/{}", m + 1), prec);
        let next: Mat = [
            [acc[0][0].mul(&inv, prec), acc[0][1].mul(&inv, prec)],
            [acc[1][0].mul(&inv, prec), acc[1][1].mul(&inv, prec)],
        ];
        y.push(next);
    }
    // evaluate at t = zb - za and S_N
    let t = Ball::point(zb.0, zb.1).sub(&z0, prec);
    let mut out: Mat = [[Ball::si(0, 0), Ball::si(0, 0)], [Ball::si(0, 0), Ball::si(0, 0)]];
    let mut tp = Ball::si(1, 0);
    let mut s_n = Ball::si(0, 0);
    let mut rk = Ball::si(1, 0);
    for k in 0..=n {
        let yk = &y[k as usize];
        for i in 0..2 {
            for j in 0..2 {
                out[i][j] = out[i][j].add(&yk[i][j].mul(&tp, prec), prec);
            }
        }
        s_n = s_n.add(&norm_inf(yk, prec).mul(&rk, prec), prec);
        tp = tp.mul(&t, prec);
        rk = rk.mul(&rho_b, prec);
    }
    // tail
    let cb = Ball::point(c, 0.0);
    let theta = cb.div(&Ball::si(n + 1, 0), prec).exp(prec).mul(&Ball::rational("1/2", prec), prec);
    if !(theta.abs_upper(prec) < 1.0) {
        return None;
    }
    let one_minus = Ball::si(1, 0).sub(&Ball::point(theta.abs_upper(prec), 0.0), prec);
    let tail = Ball::point(s_n.abs_upper(prec), 0.0)
        .mul(&cb.div(&Ball::si(n, 0), prec).exp(prec), prec)
        .mul(&powb(&Ball::rational("1/2", prec), n + 1, prec), prec)
        .div(&one_minus, prec);
    let e = tail.abs_upper(prec);
    if !e.is_finite() {
        return None;
    }
    for i in 0..2 {
        for j in 0..2 {
            out[i][j].add_error(e);
        }
    }
    Some(out)
}

/// Certified transport along a polyline. `obst` (float singular-point estimates) only chooses step sizes.
pub fn transport(
    sys: &Sys, pts: &[(f64, f64)], obst: &[(f64, f64)], bad: &[(f64, f64)], p: &Params, hmax: f64, frac: f64,
) -> Result<(Mat, u64), String> {
    let mut y = ident();
    let mut steps = 0u64;
    let dist = |z: (f64, f64)| {
        obst.iter().map(|o| ((z.0 - o.0).powi(2) + (z.1 - o.1).powi(2)).sqrt()).fold(f64::INFINITY, f64::min)
    };
    for w in pts.windows(2) {
        let (mut z, b) = (w[0], w[1]);
        loop {
            let rem = ((b.0 - z.0).powi(2) + (b.1 - z.1).powi(2)).sqrt();
            if rem == 0.0 {
                break;
            }
            let mut h = rem.min(hmax).min(frac * dist(z));
            let t;
            let zb;
            loop {
                let cand = if h >= rem { b } else { (z.0 + h * (b.0 - z.0) / rem, z.1 + h * (b.1 - z.1) / rem) };
                if let Some(tt) = step(sys, z, cand, p, bad) {
                    t = tt;
                    zb = cand;
                    break;
                }
                h /= 2.0;
                if h < 1e-7 {
                    return Err(format!("step size underflow near ({}, {})", z.0, z.1));
                }
            }
            y = matmul(&t, &y, p.prec);
            z = zb;
            steps += 1;
        }
    }
    Ok((y, steps))
}
