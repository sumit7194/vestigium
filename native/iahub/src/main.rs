//! Setup smoke test: call Arb (FLINT 3.6.0) from Rust over a minimal hand-written FFI and print a
//! rigorous enclosure of exp(1 + i) at 192 bits, for comparison with python-flint.
use std::ffi::CStr;
use std::os::raw::{c_char, c_long, c_ulong};

#[repr(C)]
struct ArbStruct { _opaque: [u64; 6] }      // arb_struct: arf (4 words) + mag (2 words) on 64-bit
#[repr(C)]
struct AcbStruct { re: ArbStruct, im: ArbStruct }

extern "C" {
    fn acb_init(x: *mut AcbStruct);
    fn acb_clear(x: *mut AcbStruct);
    fn acb_set_si_si(x: *mut AcbStruct, re: c_long, im: c_long);
    fn acb_exp(r: *mut AcbStruct, z: *const AcbStruct, prec: c_long);
    fn arb_get_str(x: *const ArbStruct, digits: c_long, flags: c_ulong) -> *mut c_char;
    fn flint_free(p: *mut std::ffi::c_void);
}

fn main() {
    unsafe {
        let mut z: AcbStruct = std::mem::zeroed();
        let mut r: AcbStruct = std::mem::zeroed();
        acb_init(&mut z);
        acb_init(&mut r);
        acb_set_si_si(&mut z, 1, 1);
        acb_exp(&mut r, &z, 192);
        let sr = arb_get_str(&r.re, 40, 0);
        let si = arb_get_str(&r.im, 40, 0);
        println!("Rust/Arb:     {} + {}j", CStr::from_ptr(sr).to_string_lossy(), CStr::from_ptr(si).to_string_lossy());
        flint_free(sr as *mut _);
        flint_free(si as *mut _);
        acb_clear(&mut z);
        acb_clear(&mut r);
    }
}
