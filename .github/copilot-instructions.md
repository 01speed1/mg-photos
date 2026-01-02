# MG-Photos AI Coding Instructions

## Project Overview

`mg-photos` is a lightweight Rust application designed to turn an old Android tablet into a digital photo frame. It runs a local HTTP server to display photos and periodically downloads new images from a configured URL.

## Architecture & Core Patterns

### Dual-Target Logic

The codebase explicitly handles two environments using `cfg!(target_os = "android")` and `std::env::var("TARGET")`:

- **Android (Target):**
  - Base Path: `/data/local/tmp/`
  - Port: `9000`
  - Requires `src/compat.c` linked via `build.rs` for legacy libc compatibility.
- **Local (Dev/WSL):**
  - Base Path: `./` (current directory)
  - Port: `8080`

### Key Components

- **Web Server (`tiny_http`):**
  - `GET /`: Auto-refreshing HTML displaying the current photo.
  - `GET /foto.jpg`: Serves the downloaded image.
  - `GET /config`: Form to update the source URL.
  - `GET /save`: Updates `config.txt`.
- **Background Worker:** A spawned thread checks `config.txt` every 5 minutes and downloads the image using `minreq`.
- **Networking:** Uses `minreq` with `rustls` features to bypass potential SSL certificate issues on older Android devices.

### Critical Files

- `src/main.rs`: Application entry point, server logic, and background worker.
- `src/compat.c`: C compatibility layer for the specific Android target.
- `build.rs`: Compiles and links `compat.c` only when targeting `armv7-linux-androideabi`.

## Workflows & Commands

### Build & Deploy

The project uses custom shell scripts for the build-deploy cycle, bridging WSL and Windows ADB.

- **Full Cycle (`call.sh`):**

  1. Cleans the project.
  2. Builds for release (`--release`).
  3. Removes old binary from device.
  4. Calls `deploy.sh`.
  5. Runs the binary on the device with `LD_DEBUG=1`.

- **Deploy Only (`deploy.sh`):**
  1. Copies binary to Windows ADB directory.
  2. Pushes binary to `/data/local/tmp/` on the device using `adb.exe`.

### Cross-Compilation

- Target: `armv7-linux-androideabi`
- Ensure `config.toml` or environment variables are set up for the cross-linker if modifying build configuration.

## Coding Conventions

- **Resource Constraints:** Keep dependencies minimal. The target is an old device.
- **Error Handling:** Simple error handling is preferred (e.g., `expect`, `unwrap`, or ignoring non-critical errors) to keep the binary small and logic simple.
- **Panic Strategy:** `panic = "abort"` is configured in `Cargo.toml` for both profiles.
- **Paths:** Always use `get_base_path()` or helper functions (`get_config_path`, `get_photo_path`) instead of hardcoding paths in logic.
