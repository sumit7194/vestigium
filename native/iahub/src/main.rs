//! iahub native core: certified monodromy of Y' = M(z) Y along given loops (PREREG_iahub_v2.md).
//!
//! Job file (text, written by the Python front end; points are exact doubles printed with 17 significant digits):
//!   PREC <bits> | N <order> | CMAX <c> | HMAX <h> | FRAC <f> | THREADS <k>
//!   I VAR | I CONST p/q | I ADD a b | I SUB a b | I MUL a b | I NEG a | I INV a | I EXP a
//!   ENTRY i j <num_reg> <den_reg>        (four lines, i, j in {0,1})
//!   BAD re im                             (essential/non-analytic points: no step disk may reach them)
//!   OBST re im                            (float singular-point estimates: step-size choice only)
//!   LOOP <name> <npts>  followed by npts lines  P re im
//! Output: per loop "LOOP name", "STATUS ok|err <msg>", "STEPS n", "M i j <re ball>|<im ball>".
mod arb;
mod slp;
mod step;

use slp::{Ins, Slp};
use std::fs;
use step::{Params, Sys};

struct Job {
    ins: Vec<Ins>,
    entries: [[(usize, usize); 2]; 2],
    bad: Vec<(f64, f64)>,
    obst: Vec<(f64, f64)>,
    loops: Vec<(String, Vec<(f64, f64)>)>,
    prec: i64,
    n: i64,
    cmax: f64,
    hmax: f64,
    frac: f64,
    threads: usize,
}

fn parse(text: &str) -> Job {
    let mut j = Job {
        ins: vec![], entries: [[(0, 0); 2]; 2], bad: vec![], obst: vec![], loops: vec![],
        prec: 192, n: 100, cmax: 4.0, hmax: 0.25, frac: 0.2, threads: 4,
    };
    let mut lines = text.lines().map(|l| l.trim()).filter(|l| !l.is_empty() && !l.starts_with('#'));
    let f = |s: &str| s.parse::<f64>().expect("float");
    let u = |s: &str| s.parse::<usize>().expect("index");
    while let Some(l) = lines.next() {
        let w: Vec<&str> = l.split_whitespace().collect();
        match w[0] {
            "PREC" => j.prec = w[1].parse().unwrap(),
            "N" => j.n = w[1].parse().unwrap(),
            "CMAX" => j.cmax = f(w[1]),
            "HMAX" => j.hmax = f(w[1]),
            "FRAC" => j.frac = f(w[1]),
            "THREADS" => j.threads = u(w[1]),
            "I" => j.ins.push(match w[1] {
                "VAR" => Ins::Var,
                "CONST" => Ins::Const(w[2].to_string()),
                "ADD" => Ins::Add(u(w[2]), u(w[3])),
                "SUB" => Ins::Sub(u(w[2]), u(w[3])),
                "MUL" => Ins::Mul(u(w[2]), u(w[3])),
                "NEG" => Ins::Neg(u(w[2])),
                "INV" => Ins::Inv(u(w[2])),
                "EXP" => Ins::Exp(u(w[2])),
                o => panic!("unknown instruction {o}"),
            }),
            "ENTRY" => j.entries[u(w[1])][u(w[2])] = (u(w[3]), u(w[4])),
            "BAD" => j.bad.push((f(w[1]), f(w[2]))),
            "OBST" => j.obst.push((f(w[1]), f(w[2]))),
            "LOOP" => {
                let k = u(w[2]);
                let mut pts = Vec::with_capacity(k);
                for _ in 0..k {
                    let p: Vec<&str> = lines.next().unwrap().split_whitespace().collect();
                    assert_eq!(p[0], "P");
                    pts.push((f(p[1]), f(p[2])));
                }
                j.loops.push((w[1].to_string(), pts));
            }
            o => panic!("unknown directive {o}"),
        }
    }
    j
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() >= 2 && args[1] == "--smoke" {
        let z = arb::Ball::si(1, 1).exp(192);
        println!("exp(1+i) = {}", z.to_str(40));
        return;
    }
    let job = parse(&fs::read_to_string(&args[1]).expect("job file"));
    let p = Params { n: job.n, prec: job.prec, cmax: job.cmax };
    let results: Vec<String> = std::thread::scope(|s| {
        let chunks: Vec<Vec<usize>> = (0..job.threads.max(1))
            .map(|t| (0..job.loops.len()).filter(|i| i % job.threads.max(1) == t).collect())
            .collect();
        let handles: Vec<_> = chunks
            .into_iter()
            .map(|idx| {
                let job = &job;
                let p = &p;
                s.spawn(move || {
                    let sys = Sys { slp: Slp::new(job.ins.clone(), job.prec), entries: job.entries };
                    idx.into_iter()
                        .map(|i| {
                            let (name, pts) = &job.loops[i];
                            let mut out = format!("LOOP {name}\n");
                            match step::transport(&sys, pts, &job.obst, &job.bad, p, job.hmax, job.frac) {
                                Ok((m, steps)) => {
                                    out += &format!("STATUS ok\nSTEPS {steps}\n");
                                    for a in 0..2 {
                                        for b in 0..2 {
                                            out += &format!("M {a} {b} {}\n", m[a][b].to_str(60));
                                        }
                                    }
                                }
                                Err(e) => out += &format!("STATUS err {e}\n"),
                            }
                            (i, out)
                        })
                        .collect::<Vec<_>>()
                })
            })
            .collect();
        let mut all: Vec<(usize, String)> = handles.into_iter().flat_map(|h| h.join().unwrap()).collect();
        all.sort_by_key(|x| x.0);
        all.into_iter().map(|x| x.1).collect()
    });
    for r in results {
        print!("{r}");
    }
}
