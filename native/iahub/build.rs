fn main() {
    // FLINT 3.6.0 (Homebrew) -- Arb is part of FLINT 3
    println!("cargo:rustc-link-search=native=/opt/homebrew/lib");
    println!("cargo:rustc-link-lib=dylib=flint");
    println!("cargo:rustc-link-lib=dylib=mpfr");
    println!("cargo:rustc-link-lib=dylib=gmp");
}
