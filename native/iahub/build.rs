fn main() {
    // FLINT 3.6.0 (Homebrew; Arb is part of FLINT 3). The C shim is compiled with the system cc, no crates.
    let out = std::env::var("OUT_DIR").unwrap();
    let obj = format!("{out}/shim.o");
    let lib = format!("{out}/libshim.a");
    let ok = std::process::Command::new("cc")
        .args(["-O2", "-c", "src/shim.c", "-I/opt/homebrew/include", "-o", &obj])
        .status().expect("cc").success();
    assert!(ok, "compiling shim.c failed");
    let ok = std::process::Command::new("ar").args(["crs", &lib, &obj]).status().expect("ar").success();
    assert!(ok, "ar failed");
    println!("cargo:rerun-if-changed=src/shim.c");
    println!("cargo:rustc-link-search=native={out}");
    println!("cargo:rustc-link-lib=static=shim");
    println!("cargo:rustc-link-search=native=/opt/homebrew/lib");
    println!("cargo:rustc-link-lib=dylib=flint");
    println!("cargo:rustc-link-lib=dylib=mpfr");
    println!("cargo:rustc-link-lib=dylib=gmp");
}
