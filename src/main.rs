use std::alloc::System;
use std::fs;
use std::thread;
use std::time::Duration;
use tiny_http::{Method, Response, Server};

#[global_allocator]
static GLOBAL: System = System;

// Función para obtener la ruta según el sistema
fn get_base_path() -> &'static str {
    if cfg!(target_os = "android") {
        "/data/local/tmp/"
    } else {
        "./" // En tu PC guardará todo en la carpeta del proyecto
    }
}

fn get_config_path() -> String {
    format!("{}config.txt", get_base_path())
}

fn get_photo_path() -> String {
    format!("{}current.jpg", get_base_path())
}

fn main() {
    let port = if cfg!(target_os = "android") {
        9000 // Puerto para la tablet (Build)
    } else {
        8080 // Puerto para tu PC/WSL (Pruebas)
    };

    let addr = format!("0.0.0.0:{}", port);

    thread::spawn(|| {
        loop {
            if let Ok(url) = fs::read_to_string(get_config_path()) {
                let url = url.trim();
                if !url.is_empty() {
                    println!("Descargando foto desde: {}", url);
                    // Usamos minreq con rustls para saltar los certs viejos de la tablet
                    if let Ok(response) = minreq::get(url).send() {
                        let _ = fs::write(get_photo_path(), response.as_bytes());
                        println!("✅ Foto actualizada");
                    }
                }
            }
            thread::sleep(Duration::from_secs(300)); // Revisa cada 5 minutos
        }
    });

    // 2. Servidor Web
    let server = Server::http(&addr).expect("No se pudo iniciar el servidor");
    println!("🚀 Motor listo en el puerto {}", port);

    for request in server.incoming_requests() {
        match (request.method(), request.url()) {
            (&Method::Get, "/") => {
                let html = r#"<html><head><meta http-equiv="refresh" content="60">
                    <style>body{margin:0;background:#000;display:flex;justify-content:center;align-items:center;height:100vh;}
                    img{max-width:100%;max-height:100%;object-fit:contain;}</style></head>
                    <body><img src="/foto.jpg"></body></html>"#;
                request
                    .respond(
                        Response::from_string(html).with_header(
                            "Content-Type: text/html"
                                .parse::<tiny_http::Header>()
                                .unwrap(),
                        ),
                    )
                    .unwrap();
            }
            (&Method::Get, "/foto.jpg") => {
                if let Ok(file) = fs::File::open(get_photo_path()) {
                    request.respond(Response::from_file(file)).unwrap();
                } else {
                    request
                        .respond(Response::from_string("No hay foto").with_status_code(404))
                        .unwrap();
                }
            }
            (&Method::Get, "/config") => {
                let html = "<h1>Configura tu Porta Retratos</h1><form action='/save' method='get'>URL de imagen: <input name='url' style='width:80%'><button>Guardar</button></form>";
                request
                    .respond(
                        Response::from_string(html).with_header(
                            "Content-Type: text/html"
                                .parse::<tiny_http::Header>()
                                .unwrap(),
                        ),
                    )
                    .unwrap();
            }
            (&Method::Get, url) if url.starts_with("/save") => {
                // Extraer URL de los parámetros (forma ultra simple para ahorrar RAM)
                if let Some(pos) = url.find("url=") {
                    let new_url = &url[pos + 4..];
                    let decoded_url = new_url.replace("%3A", ":").replace("%2F", "/");
                    let _ = fs::write(get_config_path(), decoded_url);
                    request
                        .respond(Response::from_string(
                            "Guardado. Reinicia la tablet o espera 5 min.",
                        ))
                        .unwrap();
                }
            }
            _ => {
                request.respond(Response::from_string("404")).unwrap();
            }
        }
    }
}
