//! kerr_rs -- NON-RIGOROUS compiled replacement for MNFlow.P / Pinv / py_of (mn_numerics.py), for the B15 constructor
//! stage only (the frozen B14 constructor is untouched; it is plugged in through the same adapter). A second compiled
//! implementation next to kerr_p.cpp, independent of it except for the field: the same B10-regularised MN/Kerr reduced
//! field, generated (mn_codegen_rs.py) from the same gated symbolic source and CSE as gen/mn_field.h, in f64, with the
//! Jacobian by forward-mode dual numbers (exact derivatives of the same expression; no finite differences).
//! Integrator: an own Dormand-Prince 5(4) with Hairer's dense output (dopri5.rs; kerr_p.cpp uses Boost.Odeint's, with
//! a different error norm), rtol = atol = 1e-12 by default; events located by bisection on the dense output to
//! |dt| <= 1e-14 (1 + t). Same semantics as MNFlow.P: start on y = 0 with p_y > 0 lifted from H = -1/2; return = the
//! next crossing of y = 0 with ydot > 0 at t > 1e-6, n times (y reset to 0 at each); jac: the 2x2 section derivative
//! with the same on-shell D_in and the same "slide along the flow back to y = 0" correction, once at the end. Pinv:
//! the reversed flow, first crossing with direction -1 at t > 1e-6.
//! Same C ABI as kerr_p.cpp. Status: candidate for a REGISTERED amendment of B15's map implementation, after the gate.
mod dopri5;
mod mn_field;
mod scalar;
use dopri5::Dopri;
use mn_field::{mn_field, mn_lift};
use scalar::D4;
use std::sync::RwLock;

struct Cfg { c: [f64; 5], rtol: f64, atol: f64 }
static CFG: RwLock<Cfg> = RwLock::new(Cfg { c: [39.0, -0.625, 0.0, 0.98, 222.5], rtol: 1e-12, atol: 1e-12 });

fn field(c: &[f64; 5], z: &[f64], f: &mut [f64; 4]) { mn_field::<f64>(&[z[0], z[1], z[2], z[3]], f, c); }
fn field_jac(c: &[f64; 5], z: &[f64], f: &mut [f64; 4], j: &mut [[f64; 4]; 4]) {
    let inp = [D4::var(z[0], 0), D4::var(z[1], 1), D4::var(z[2], 2), D4::var(z[3], 3)];
    let cc = [D4::c(c[0]), D4::c(c[1]), D4::c(c[2]), D4::c(c[3]), D4::c(c[4])];
    let mut out = [D4::c(0.0); 4];
    mn_field::<D4>(&inp, &mut out, &cc);
    for i in 0..4 { f[i] = out[i].v; j[i] = out[i].d; }
}

/// integrate from s until the first event (y crosses 0 with direction dir) at t > 1e-6; None if the step start passes
/// tmax. N = 4 (state) or 20 (state + row-major 4x4 variational matrix). sign = -1 integrates the reversed field.
fn to_event<const N: usize>(s: &mut [f64; N], cfg: &Cfg, sign: f64, dir: f64, tmax: f64) -> Option<f64> {
    let c = cfg.c;
    let rhs = move |z: &[f64; N], dz: &mut [f64; N]| {
        let mut f = [0.0; 4];
        if N == 4 { field(&c, z, &mut f); for i in 0..4 { dz[i] = sign * f[i]; } return; }
        let mut j = [[0.0; 4]; 4];
        field_jac(&c, z, &mut f, &mut j);
        for i in 0..4 { dz[i] = sign * f[i]; }
        for i in 0..4 { for k in 0..4 { let mut a = 0.0; for m in 0..4 { a += j[i][m] * z[4 + 4 * m + k]; } dz[4 + 4 * i + k] = sign * a; } }
    };
    let mut ig = Dopri::new(rhs, *s, 1e-6, cfg.rtol, cfg.atol);
    loop {
        let st = ig.step();
        let (t0, t1) = (st.t0, st.t0 + st.h);
        if t0 > tmax { return None; }
        let (ya, yb) = (st.r[0][1], ig.y[1]);
        let cross = if dir > 0.0 { ya < 0.0 && yb >= 0.0 } else { ya > 0.0 && yb <= 0.0 };
        if cross && t1 > 1e-6 {
            let (mut lo, mut hi) = (t0.max(1e-6), t1);
            let mut it = 0;
            while it < 200 && hi - lo > 1e-14 * (1.0 + hi) {
                let mid = 0.5 * (lo + hi); let m = st.at(mid);
                let before = if dir > 0.0 { m[1] < 0.0 } else { m[1] > 0.0 };
                if before { lo = mid; } else { hi = mid; }
                it += 1;
            }
            *s = st.at(hi);
            return Some(hi);
        }
    }
}

#[no_mangle]
pub extern "C" fn kerr_set(k: f64, alpha: f64, beta: f64, e: f64, l: f64, rtol: f64, atol: f64) {
    let mut g = CFG.write().unwrap(); g.c = [k, alpha, beta, e, l]; g.rtol = rtol; g.atol = atol;
}

fn py_of(c: &[f64; 5], x: f64, px: f64) -> f64 {
    let mut g = [0.0; 3]; mn_lift::<f64>(&[x, 0.0], &mut g, c);
    let r = (-1.0 - g[0] * px * px - 2.0 * g[2]) / g[1];
    if r > 0.0 { r.sqrt() } else { f64::NAN }
}

#[no_mangle]
pub extern "C" fn kerr_py(x: f64, px: f64) -> f64 { py_of(&CFG.read().unwrap().c, x, px) }

/// out: x, px, T, and if jac: DP (2x2 row-major) -> 7 doubles. Returns 1 on success, 0 if no return within tmax.
/// # Safety: out must point to 3 (jac = 0) or 7 (jac != 0) writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_P(x: f64, px: f64, n: i32, jac: i32, tmax: f64, out: *mut f64) -> i32 {
    let cfg = CFG.read().unwrap();
    let py = py_of(&cfg.c, x, px); if py.is_nan() { return 0; }
    let mut t_tot = 0.0;
    if jac == 0 {
        let mut s = [x, 0.0, px, py];
        for _ in 0..n { match to_event(&mut s, &cfg, 1.0, 1.0, tmax) { Some(te) => { s[1] = 0.0; t_tot += te; } None => return 0 } }
        let o = std::slice::from_raw_parts_mut(out, 3); o[0] = s[0]; o[1] = s[2]; o[2] = t_tot;
        return 1;
    }
    let mut s = [0.0; 20]; s[0] = x; s[2] = px; s[3] = py; for i in 0..4 { s[4 + 5 * i] = 1.0; }
    for _ in 0..n { match to_event(&mut s, &cfg, 1.0, 1.0, tmax) { Some(te) => { s[1] = 0.0; t_tot += te; } None => return 0 } }
    let mut f0 = [0.0; 4]; field(&cfg.c, &[x, 0.0, px, py], &mut f0);
    let (hx, hpx, hpy) = (-f0[2], f0[0], f0[1]);
    let din = [[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [-hx / hpy, -hpx / hpy]];
    let mut v = [[0.0; 2]; 4];
    for i in 0..4 { for j in 0..2 { let mut a = 0.0; for k in 0..4 { a += s[4 + 4 * i + k] * din[k][j]; } v[i][j] = a; } }
    let mut f = [0.0; 4]; field(&cfg.c, &s[..4], &mut f);
    let v1 = v[1];
    for i in 0..4 { for j in 0..2 { v[i][j] -= f[i] * (v1[j] / f[1]); } }   // slide back to y = 0
    let o = std::slice::from_raw_parts_mut(out, 7);
    o[0] = s[0]; o[1] = s[2]; o[2] = t_tot; o[3] = v[0][0]; o[4] = v[0][1]; o[5] = v[2][0]; o[6] = v[2][1];
    1
}

/// # Safety: out must point to 2 writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_Pinv(x: f64, px: f64, tmax: f64, out: *mut f64) -> i32 {
    let cfg = CFG.read().unwrap();
    let py = py_of(&cfg.c, x, px); if py.is_nan() { return 0; }
    let mut s = [x, 0.0, px, py];
    if to_event(&mut s, &cfg, -1.0, -1.0, tmax).is_none() { return 0; }
    let o = std::slice::from_raw_parts_mut(out, 2); o[0] = s[0]; o[1] = s[2];
    1
}
