//! Straight-line programs: the equation's numerators/denominators compiled ONCE (by the Python front end) into a
//! flat list of instructions, evaluated either as truncated power series (Taylor coefficients) or as scalar
//! balls over a box (crude Cauchy bounds). Same program, two numeric domains -- no tree walking at run time.
use crate::arb::{Ball, Ser};

#[derive(Clone, Debug)]
pub enum Ins {
    Var,              // z0 + t   (series) / the box itself (scalar)
    Const(String),    // exact rational "p/q"
    Add(usize, usize),
    Sub(usize, usize),
    Mul(usize, usize),
    Neg(usize),
    Inv(usize),
    Exp(usize),
}

pub struct Slp {
    pub ins: Vec<Ins>,
    pub consts: Vec<Option<Ball>>, // precomputed Const balls (by instruction index)
}

impl Slp {
    pub fn new(ins: Vec<Ins>, prec: i64) -> Self {
        let consts = ins
            .iter()
            .map(|i| match i {
                Ins::Const(s) => Some(Ball::rational(s, prec)),
                _ => None,
            })
            .collect();
        Slp { ins, consts }
    }

    /// Evaluate as series of length n at z0. Returns all registers (outputs are indices into it).
    pub fn eval_series(&self, z0: &Ball, n: i64, prec: i64) -> Vec<Ser> {
        let mut r: Vec<Ser> = Vec::with_capacity(self.ins.len());
        for (k, i) in self.ins.iter().enumerate() {
            let v = match i {
                Ins::Var => Ser::var(z0),
                Ins::Const(_) => Ser::constant(self.consts[k].as_ref().unwrap()),
                Ins::Add(a, b) => r[*a].add(&r[*b], n, prec),
                Ins::Sub(a, b) => r[*a].sub(&r[*b], n, prec),
                Ins::Mul(a, b) => r[*a].mul(&r[*b], n, prec),
                Ins::Neg(a) => r[*a].neg(),
                Ins::Inv(a) => r[*a].inv(n, prec),
                Ins::Exp(a) => r[*a].exp(n, prec),
            };
            r.push(v);
        }
        r
    }

    /// Evaluate as scalar balls on `x` (a box): rigorous enclosure of the range over the box.
    pub fn eval_ball(&self, x: &Ball, prec: i64) -> Vec<Ball> {
        let mut r: Vec<Ball> = Vec::with_capacity(self.ins.len());
        for (k, i) in self.ins.iter().enumerate() {
            let v = match i {
                Ins::Var => x.clone(),
                Ins::Const(_) => self.consts[k].as_ref().unwrap().clone(),
                Ins::Add(a, b) => r[*a].add(&r[*b], prec),
                Ins::Sub(a, b) => r[*a].sub(&r[*b], prec),
                Ins::Mul(a, b) => r[*a].mul(&r[*b], prec),
                Ins::Neg(a) => r[*a].neg(),
                Ins::Inv(a) => r[*a].inv(prec),
                Ins::Exp(a) => r[*a].exp(prec),
            };
            r.push(v);
        }
        r
    }
}
