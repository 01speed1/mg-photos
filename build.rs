fn main() {
    // Solo compilar el parche si el destino es la tablet (Android)
    if std::env::var("TARGET").unwrap_or_default() == "armv7-linux-androideabi" {
        cc::Build::new().file("src/compat.c").compile("compat");
        println!("cargo:rustc-link-lib=static=compat");
    }
}
