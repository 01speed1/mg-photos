# Plan de Implementación: Google Photos & Interacción

Este documento detalla el plan para evolucionar `mg-photos` de un visor de una sola imagen a un marco digital interactivo sincronizado con Google Photos.

## Estrategia: Sincronización Local

Para evitar problemas de red y caducidad de URLs en la tablet antigua, el backend (Rust) descargará las fotos localmente y el frontend (JS) las consumirá desde el almacenamiento local.

---

## Checklist de Progreso

### Fase 1: Preparación de Google Cloud (Manual en PC)

- [ ] Crear proyecto en Google Cloud Console.
- [ ] Habilitar **Google Photos Library API**.
- [ ] Crear credenciales OAuth 2.0 (Desktop App) -> Obtener `Client ID` y `Client Secret`.
- [x] Generar script para obtener tokens (`scripts/get_refresh_token.py`).
- [x] Ejecutar script y obtener `refresh_token`.
- [ ] Guardar credenciales y token en `config.json`.

### Fase 2: Backend Rust (Sincronización y API)

- [ ] **Configuración:** Migrar de `config.txt` a `config.json` para soportar credenciales.
- [ ] **OAuth:** Implementar función para canjear `refresh_token` por `access_token` usando `minreq`.
- [ ] **API Client:** Implementar búsqueda de fotos en álbum (`mediaItems.search`).
- [ ] **Sincronizador:**
  - [ ] Lógica para comparar fotos remotas vs. locales.
  - [ ] Descargar nuevas imágenes a `/data/local/tmp/photos/`.
  - [ ] (Opcional) Limpiar imágenes antiguas.
- [ ] **Servidor Web:**
  - [ ] Endpoint `GET /api/photos`: Retornar JSON con lista de archivos locales.
  - [ ] Endpoint `GET /photos/:filename`: Servir archivos estáticos desde la carpeta de fotos.

### Fase 3: Frontend (HTML/JS/CSS)

- [ ] **Estructura:** Actualizar el HTML embebido en `main.rs`.
- [ ] **Lógica JS:**
  - [ ] Fetch a `/api/photos` al inicio.
  - [ ] Temporizador (`setInterval`) para rotar imágenes.
  - [ ] Manejador de eventos (`click`) para avanzar manualmente.
- [ ] **UX/Performance:**
  - [ ] Implementar precarga de la siguiente imagen (evitar parpadeos).
  - [ ] Agregar transiciones CSS (fade in/out).

### Fase 4: Limpieza y Despliegue

- [ ] Verificar uso de memoria en la tablet (evitar OOM).
- [ ] Actualizar `copilot-instructions.md` con la nueva arquitectura.
