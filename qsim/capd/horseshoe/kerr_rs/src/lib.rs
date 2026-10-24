//! kerr_rs -- NON-RIGOROUS compiled replacement for MNFlow.P / Pinv / py_of (mn_numerics.py), for the B15 constructor
//! stage only (the frozen B14 constructor is untouched; it is plugged in through the same adapter). A second compiled
//! implementation next to kerr_p.cpp, independent of it except for the field: the same B10-regularised MN/Kerr reduced
//! field, generated (mn_codegen_rs.py) from the same gated symbolic source and CSE as gen/mn_field.h, in f64, with the
//! Jacobian by forward-mode dual numbers (exact derivatives of the same expression; no finite differences).
//! Integrator: an own Dormand-Prince 5(4) with Hairer's dense output (dopri5.rs; kerr_p.cpp uses Boost.Odeint's, with
//! a different error norm), rtol = atol = 1e-12 by default. Events (B15b draft rev 3, E1-E5): every accepted step is
//! sampled at 10 points of its dense output and may change side at most once (E5, a detection heuristic); the event is
//! bisected in the step-local theta to 4e-16 (E1); the state at the event comes from a real integration to it, checked
//! against the interpolant to 1e-11 block-relative (E2); failures halve the step, up to 10 times, then the call returns
//! -1 (never 0, "no return"); T is summed with compensation (E4); per-call diagnostics via kerr_stats (E3).
//! Same semantics as MNFlow.P: start on y = 0 with p_y > 0 lifted from H = -1/2; return = the next crossing of y = 0
//! with ydot > 0 at t > 1e-6, n times (y reset to 0 at each); jac: the 2x2 section derivative with the same on-shell
//! D_in and the same "slide along the flow back to y = 0" correction, once at the end. Pinv: the reversed flow, first
//! crossing with direction -1 at t > 1e-6.
//! Same C ABI as kerr_p.cpp. Status: candidate for a REGISTERED amendment of B15's map implementation, after the gate.
mod dopri5;
mod mn_field;
mod scalar;
use dopri5::Dopri;
use mn_field::{mn_field, mn_lift};
use scalar::D4;
use std::sync::{Mutex, RwLock};

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

/// per-call diagnostics (E3), read back by kerr_stats
#[derive(Clone, Copy)]
struct Stats { crossings: f64, max_event_bound: f64, max_restep_diff: f64, min_transversality: f64, e2_retries: f64, e5_retries: f64 }
const STATS0: Stats = Stats { crossings: 0.0, max_event_bound: 0.0, max_restep_diff: 0.0, min_transversality: f64::INFINITY, e2_retries: 0.0, e5_retries: 0.0 };
static STATS: Mutex<Stats> = Mutex::new(STATS0);

/// failure kinds (B15b / B15b-1): Check = an E2 or E5 check failed (or the step underflowed): -1;
/// Collapse = an accepted step with h < 1e-14 max(1, |t|) (B15b-1 P1): -2, with the state kept for the certifier
#[derive(Clone, Copy, Debug)]
enum Fail { Check, Collapse }
/// the collapse state of the last -2: x, y, px, py, t (time since the start of the call)
static COLLAPSE: Mutex<[f64; 5]> = Mutex::new([f64::NAN; 5]);
const COLLAPSE_REL: f64 = 1e-14;

const NSAMP: usize = 9;          // E5: the step's endpoints and 8 interior points, theta = j / 9
const MAX_RETRY: u32 = 10;
/// E2's registered bar is 1e-11; kerr_test_e2_bar exists ONLY for the -1 negative control (never in a counted run)
static E2_BAR: RwLock<f64> = RwLock::new(1e-11);

/// E2's block-relative difference: state block (0..4) and variational block (4..N) separately
fn block_diff<const N: usize>(a: &[f64; N], b: &[f64; N]) -> f64 {
    let mut d = 0.0;
    for (lo, hi) in [(0usize, 4usize.min(N)), (4usize.min(N), N)] {
        if lo == hi { continue; }
        let sc = b[lo..hi].iter().fold(1.0f64, |m, v| m.max(v.abs()));
        for i in lo..hi { d = f64::max(d, (a[i] - b[i]).abs() / sc); }
    }
    d
}

/// integrate from s until the first event (y crosses 0 with direction dir) at t > 1e-6.
/// Ok(Some((t0, dt))): the event at t0 + dt (returned split, for compensated summation), s = the state there by a real
/// step (E2); Ok(None): the step start passed tmax; Err(Fail::Check): an E2 or E5 check failed after MAX_RETRY
/// halvings; Err(Fail::Collapse): step-size collapse, with COLLAPSE set (its t relative to this to_event's start).
/// N = 4 (state) or 20 (state + row-major 4x4 variational matrix). sign = -1 integrates the reversed field.
fn to_event<const N: usize>(s: &mut [f64; N], cfg: &Cfg, sign: f64, dir: f64, tmax: f64, stats: &mut Stats) -> Result<Option<(f64, f64)>, Fail> {
    let c = cfg.c;
    let rhs = move |z: &[f64; N], dz: &mut [f64; N]| {
        let mut f = [0.0; 4];
        if N == 4 { field(&c, z, &mut f); for i in 0..4 { dz[i] = sign * f[i]; } return; }
        let mut j = [[0.0; 4]; 4];
        field_jac(&c, z, &mut f, &mut j);
        for i in 0..4 { dz[i] = sign * f[i]; }
        for i in 0..4 { for k in 0..4 { let mut a = 0.0; for m in 0..4 { a += j[i][m] * z[4 + 4 * m + k]; } dz[4 + 4 * i + k] = sign * a; } }
    };
    // "past the section in the event direction", with the original test's convention (dir > 0: ya < 0 && yb >= 0;
    // dir < 0: ya > 0 && yb <= 0), so the wanted event is a change from false to true for either direction
    let side = move |v: f64| if dir > 0.0 { v >= 0.0 } else { v <= 0.0 };
    let mut ig = Dopri::new(rhs, *s, 1e-6, cfg.rtol, cfg.atol);
    // retry caps: E5 counts consecutive failures of the SAME step start (reset once a step passes E5); E2 counts every
    // failure for this crossing, never reset (a non-event step after a halving must not restart the count)
    let (mut e5_run, mut e2_count) = (0u32, 0u32);
    loop {
        let st = match ig.step() { Some(st) => st, None => return Err(Fail::Check) };   // step-size underflow -> -1
        let (t0, h) = (st.t0, st.h);
        if t0 > tmax { return Ok(None); }
        if h < COLLAPSE_REL * f64::max(1.0, t0.abs()) {                      // B15b-1 P1
            let y = &ig.y; *COLLAPSE.lock().unwrap() = [y[0], y[1], y[2], y[3], ig.t]; return Err(Fail::Collapse);
        }
        // E5: at most one side change per step (a detection heuristic: a root pair between samples can be missed)
        let sm: Vec<bool> = (0..=NSAMP).map(|j| side(st.at_theta(j as f64 / NSAMP as f64)[1])).collect();
        let changes: Vec<usize> = (0..NSAMP).filter(|&j| sm[j] != sm[j + 1]).collect();
        if changes.len() > 1 {
            e5_run += 1; stats.e5_retries += 1.0;
            if e5_run > MAX_RETRY { return Err(Fail::Check); }
            ig.reset_to(&st, 0.5 * h); continue;
        }
        e5_run = 0;
        let wanted = changes.len() == 1 && !sm[changes[0]] && sm[changes[0] + 1];
        if !(wanted && t0 + h > 1e-6) { continue; }
        // E1: bisection in the step-local theta, inside the sample bracket
        let j = changes[0];
        let (mut lo, mut hi) = ((j as f64 / NSAMP as f64).max((1e-6 - t0) / h).max(0.0), (j + 1) as f64 / NSAMP as f64);
        let mut it = 0;
        while it < 200 && hi - lo > 4e-16 {
            let mid = 0.5 * (lo + hi);
            if side(st.at_theta(mid)[1]) { hi = mid; } else { lo = mid; }
            it += 1;
        }
        // E2: a real step to the event, checked against the interpolant
        let interp = st.at_theta(hi);
        let stepped = ig.integrate_exact(&st.r[0], hi * h);
        let d = stepped.map(|y| block_diff(&y, &interp));
        match (stepped, d) {
            (Some(y), Some(d)) if d <= *E2_BAR.read().unwrap() => {
                let mut f = [0.0; N]; (ig.f)(&y, &mut f);
                stats.crossings += 1.0;
                stats.max_restep_diff = stats.max_restep_diff.max(d);
                stats.max_event_bound = stats.max_event_bound.max(f[1].abs() * h * (hi - lo));
                stats.min_transversality = stats.min_transversality.min(f[1].abs());
                *s = y;
                return Ok(Some((t0, hi * h)));
            }
            _ => {
                e2_count += 1; stats.e2_retries += 1.0;
                if e2_count > MAX_RETRY { return Err(Fail::Check); }
                ig.reset_to(&st, 0.5 * h);
            }
        }
    }
}

/// Kahan-compensated sum
struct Kahan { s: f64, c: f64 }
impl Kahan {
    fn add(&mut self, v: f64) { let y = v - self.c; let t = self.s + y; self.c = (t - self.s) - y; self.s = t; }
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

/// out: x, px, T, and if jac: DP (2x2 row-major) -> 7 doubles. Returns 1 on success, 0 if no return within tmax,
/// -1 if an integration check (E2 / E5) failed: a numerical failure, never to be read as "no return"; -2 if the step
/// size collapsed (B15b-1): kerr_collapse gives the state, for the adapter's plunge certificate.
/// # Safety: out must point to 3 (jac = 0) or 7 (jac != 0) writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_P(x: f64, px: f64, n: i32, jac: i32, tmax: f64, out: *mut f64) -> i32 {
    let cfg = CFG.read().unwrap(); let mut st = STATS0;
    let r = p_impl(&cfg, x, px, n, jac != 0, tmax, &mut st);
    *STATS.lock().unwrap() = st;
    match r {
        Ok(Some(v)) => { let k = if jac != 0 { 7 } else { 3 }; std::slice::from_raw_parts_mut(out, k).copy_from_slice(&v[..k]); 1 }
        Ok(None) => 0,
        Err(Fail::Check) => -1,
        Err(Fail::Collapse) => -2,
    }
}

/// a collapse in the k-th return: make COLLAPSE's t relative to the start of the call
fn shift<T>(r: Result<T, Fail>, t_before: f64) -> Result<T, Fail> {
    if let Err(Fail::Collapse) = r { COLLAPSE.lock().unwrap()[4] += t_before; }
    r
}

fn p_impl(cfg: &Cfg, x: f64, px: f64, n: i32, jac: bool, tmax: f64, st: &mut Stats) -> Result<Option<[f64; 7]>, Fail> {
    let py = py_of(&cfg.c, x, px); if py.is_nan() { return Ok(None); }
    let mut t = Kahan { s: 0.0, c: 0.0 };
    if !jac {
        let mut s = [x, 0.0, px, py];
        for _ in 0..n { match shift(to_event(&mut s, cfg, 1.0, 1.0, tmax, st), t.s)? { Some((a, b)) => { s[1] = 0.0; t.add(a); t.add(b); } None => return Ok(None) } }
        return Ok(Some([s[0], s[2], t.s, 0.0, 0.0, 0.0, 0.0]));
    }
    let mut s = [0.0; 20]; s[0] = x; s[2] = px; s[3] = py; for i in 0..4 { s[4 + 5 * i] = 1.0; }
    for _ in 0..n { match shift(to_event(&mut s, cfg, 1.0, 1.0, tmax, st), t.s)? { Some((a, b)) => { s[1] = 0.0; t.add(a); t.add(b); } None => return Ok(None) } }
    let mut f0 = [0.0; 4]; field(&cfg.c, &[x, 0.0, px, py], &mut f0);
    let (hx, hpx, hpy) = (-f0[2], f0[0], f0[1]);
    let din = [[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [-hx / hpy, -hpx / hpy]];
    let mut v = [[0.0; 2]; 4];
    for i in 0..4 { for j in 0..2 { let mut a = 0.0; for k in 0..4 { a += s[4 + 4 * i + k] * din[k][j]; } v[i][j] = a; } }
    let mut f = [0.0; 4]; field(&cfg.c, &s[..4], &mut f);
    let v1 = v[1];
    for i in 0..4 { for j in 0..2 { v[i][j] -= f[i] * (v1[j] / f[1]); } }   // slide back to y = 0 (y row copied first)
    Ok(Some([s[0], s[2], t.s, v[0][0], v[0][1], v[2][0], v[2][1]]))
}

/// Returns 1 / 0 / -1 / -2 as kerr_P. # Safety: out must point to 2 writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_Pinv(x: f64, px: f64, tmax: f64, out: *mut f64) -> i32 {
    let cfg = CFG.read().unwrap(); let mut st = STATS0;
    let py = py_of(&cfg.c, x, px);
    let r = if py.is_nan() { Ok(None) } else { let mut s = [x, 0.0, px, py]; to_event(&mut s, &cfg, -1.0, -1.0, tmax, &mut st).map(|o| o.map(|_| s)) };
    *STATS.lock().unwrap() = st;
    match r {
        Ok(Some(s)) => { let o = std::slice::from_raw_parts_mut(out, 2); o[0] = s[0]; o[1] = s[2]; 1 }
        Ok(None) => 0,
        Err(Fail::Check) => -1,
        Err(Fail::Collapse) => -2,
    }
}

/// the state of the last -2: x, y, px, py, t (since the start of the call) -> 5 doubles.
/// # Safety: out must point to 5 writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_collapse(out: *mut f64) { std::slice::from_raw_parts_mut(out, 5).copy_from_slice(&*COLLAPSE.lock().unwrap()); }

/// B15b-1: the state at time tstar from (x, 0, px, py(x, px)), forward (sign +1) or reversed (-1), by a plain integration
/// (no events; the last piece a real integration to tstar). out: x, y, px, py. Returns 1, or -1 / -2 as kerr_P.
/// # Safety: out must point to 4 writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_state_at(x: f64, px: f64, tstar: f64, sign: f64, out: *mut f64) -> i32 {
    let cfg = CFG.read().unwrap();
    let py = py_of(&cfg.c, x, px); if py.is_nan() { return 0; }
    let c = cfg.c;
    let rhs = move |z: &[f64; 4], dz: &mut [f64; 4]| { let mut f = [0.0; 4]; field(&c, z, &mut f); for i in 0..4 { dz[i] = sign * f[i]; } };
    let mut ig = Dopri::new(rhs, [x, 0.0, px, py], 1e-6, cfg.rtol, cfg.atol);
    loop {
        let st = match ig.step() { Some(st) => st, None => return -1 };
        if st.h < COLLAPSE_REL * f64::max(1.0, st.t0.abs()) { let y = &ig.y; *COLLAPSE.lock().unwrap() = [y[0], y[1], y[2], y[3], ig.t]; return -2; }
        if st.t0 + st.h >= tstar {
            return match ig.integrate_exact(&st.r[0], tstar - st.t0) {
                Some(y) => { std::slice::from_raw_parts_mut(out, 4).copy_from_slice(&y); 1 }
                None => -1,
            };
        }
    }
}

/// TEST HOOK, negative control only: set E2's bar (registered value 1e-11; a negative bar makes every crossing fail)
#[no_mangle]
pub extern "C" fn kerr_test_e2_bar(bar: f64) { *E2_BAR.write().unwrap() = bar; }

/// E3 diagnostics of the last kerr_P / kerr_Pinv call: crossings, max |ydot| h dtheta, max E2 difference,
/// min |ydot| at a crossing, E2 retries, E5 retries -> 6 doubles.  # Safety: out must point to 6 writable doubles.
#[no_mangle]
pub unsafe extern "C" fn kerr_stats(out: *mut f64) {
    let s = *STATS.lock().unwrap();
    std::slice::from_raw_parts_mut(out, 6).copy_from_slice(&[s.crossings, s.max_event_bound, s.max_restep_diff, s.min_transversality, s.e2_retries, s.e5_retries]);
}
