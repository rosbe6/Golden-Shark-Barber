# 📖 DOCUMENTACIÓN COMPLETA - Gold Shark Barber
**Última actualización:** Octubre 26, 2026
**Estado:** 100% Funcional ✅

---

## 📋 TABLA DE CONTENIDOS
1. [Resumen del Proyecto](#resumen)
2. [Stack Tecnológico](#stack)
3. [Estructura de Archivos](#estructura)
4. [Configuración Inicial](#config)
5. [Frontend - Páginas](#frontend-html)
6. [Backend - Rutas de la API](#backend-python)
7. [Modelos de Datos](#modelos)
8. [Servicios (Email, Telegram, Google Calendar)](#servicios)
9. [Bot de Telegram](#telegram-bot)
10. [Lógica de Horarios](#horarios)
11. [Cambios Recientes](#cambios-recientes)
12. [Deploy](#deploy)

---

## <a name="resumen"></a>
# 1️⃣ RESUMEN DEL PROYECTO

**Nombre:** Gold Shark Barber - Sistema de Citas
**Objetivo:** Plataforma web para barbería con reservas online, selección de profesional, dashboard privado para barberos/especialistas, notificaciones automáticas (email + Telegram) e integración opcional con Google Calendar.

**Características principales:**
- Landing page con carrusel de 15 reseñas estilo Google Maps
- Página "Choose Your Professional" (`professionals.html`) para elegir entre varios barberos/especialistas antes de reservar — algunos usan el sistema interno, otros Booksy o Square
- Sistema de reservas online con selección de barbero, servicio, fecha y hora
- Prevención de double-booking a nivel de base de datos (índice único parcial en MongoDB)
- Dashboard privado por barbero (JWT), con vista "admin" que ve todas las citas
- Gestión de citas: crear, completar, cancelar, reagendar
- Bloqueo de días completos o de horarios específicos (por barbero o para toda la barbería)
- Bot de Telegram para el admin (ver citas de hoy, bloquear/desbloquear días)
- Emails automáticos a clientes y notificaciones a barberos
- Integración opcional con Google Calendar (si el barbero tiene token guardado)
- Gestión de barberos vía panel admin (crear, editar, eliminar, subir foto, tipo `barber`/`skincare`)
- Responsive design (mobile first)

**Repo:** https://github.com/rosbe6/Golden-Shark-Barber
**URL en producción:** https://golden-shark-barber.onrender.com

---

## <a name="stack"></a>
# 2️⃣ STACK TECNOLÓGICO

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (mobile first, variables CSS, CSS Grid)
- **JavaScript Vanilla** - Interactividad (sin frameworks)

### Backend
- **Python 3.13**
- **Flask** - Framework web (sirve también el frontend estático)
- **Flask-CORS** - Cross-origin requests
- **python-dotenv** - Variables de entorno

### Base de Datos
- **MongoDB Atlas** - Base de datos NoSQL en la nube
- **PyMongo** - Driver de Python para MongoDB
- Índice único parcial en `citas` (`dia`, `hora`, `barbero_id` cuando `estado = 'confirmada'`) para evitar reservas duplicadas

### Email
- **smtplib** vía Gmail - Envío de emails
- **email.mime** - Formato HTML para emails

### Notificaciones
- **Telegram Bot API** (`requests`) - Notificaciones al admin + comandos de gestión

### Autenticación
- **JWT (PyJWT)** - Tokens de 7 días para barberos
- **bcrypt** - Hash de contraseñas

### Calendario
- **Google Calendar API** (`google-auth`, `google-api-python-client`) - Creación automática de eventos si el barbero tiene `google_token`

### Deploy
- **Render** - Hosting del backend
- **GitHub** - Control de versiones
- **ngrok** - Tunneling para desarrollo local (OAuth callback)

---

## <a name="estructura"></a>
# 3️⃣ ESTRUCTURA DE ARCHIVOS

```
proyecto-barberia-gold-shark - V5/
│
├── CLAUDE.md                        # Esta documentación
├── README.md
├── INSTRUCCIONES_REPARACION.md      # Fix histórico: timezone + race condition
├── SOLUCION_DOUBLE_BOOKING.md       # Detalle técnico del índice único
│
├── backend/
│   ├── app.py                       # Aplicación Flask principal (sirve API + estáticos)
│   ├── config.py                    # Configuración (.env)
│   ├── database.py                  # Conexión MongoDB
│   ├── cleanup_and_reindex.py       # Script: limpia duplicados y crea índice único
│   ├── cleanup_citas.py             # Script de limpieza de citas
│   ├── init_indexes.py              # Script manual para crear el índice único
│   ├── migrar_passwords.py          # Script de migración de contraseñas
│   ├── deploy.py                    # Script de deploy
│   │
│   ├── models/
│   │   ├── cita.py                  # Modelo de cita
│   │   ├── barbero.py               # Modelo de barbero/especialista (con bcrypt)
│   │   └── cliente.py               # Modelo de cliente (historial de citas)
│   │
│   ├── routes/
│   │   ├── autenticacion.py         # Login/registro/CRUD de barberos
│   │   ├── citas.py                 # CRUD de citas, disponibilidad, bloqueos
│   │   ├── dashboard.py             # Rutas protegidas (JWT) para el panel del barbero
│   │   └── telegram.py              # Webhook del bot de Telegram
│   │
│   ├── services/
│   │   ├── email_service.py         # Envío de emails (confirmación, cancelación, etc.)
│   │   ├── google_calendar.py       # Integración Google Calendar
│   │   └── telegram_service.py      # Envío de mensajes vía Telegram
│   │
│   ├── utils/
│   │   ├── autenticacion.py         # generar_token, verificar_token, decorador @token_requerido
│   │   └── validaciones.py          # horario_disponible y otras validaciones
│   │
│   └── static/
│       ├── index.html               # Landing page
│       ├── professionals.html       # ✨ Elegir profesional (Edy, David, Cameron, Adriana, Oscar)
│       ├── servicios.html
│       ├── sobre-nosotros.html
│       ├── galeria.html
│       ├── contacto.html
│       ├── reserva.html             # Formulario de reserva (sistema interno)
│       ├── cita.html                # Detalles de cita
│       ├── dashboard.html           # Dashboard privado del barbero
│       ├── index-temp.html          # ⚠️ Archivo temporal/obsoleto, sin usar
│       ├── reservaantigua.html      # ⚠️ Versión antigua del formulario, sin usar
│       │
│       ├── images/                  # logo, fotos del equipo (edy.jpg, david.jpg, etc.), iconos
│       │
│       ├── css/
│       │   ├── main.css
│       │   ├── index.css            # Landing + reviews + grid de servicios
│       │   ├── dashboard.css
│       │   ├── servicios.css
│       │   ├── galeria.css
│       │   ├── reserva.css
│       │   ├── index-reserva.css
│       │   ├── contacto.css
│       │   ├── cita.css
│       │   └── sobre-nosotros.css
│       │
│       └── js/
│           ├── navbar.js            # Navegación / menú hamburguesa
│           ├── app.js               # Lógica del formulario de reserva
│           ├── dashboard.js         # Dashboard interactivo
│           ├── cita.js
│           ├── contacto.js
│           └── galeria.js
│
└── .git/
```

> Nota: no existe carpeta `reviews.js` ni `reservas.js` como se documentaba antes; la lógica de reservas vive en `js/app.js`.

---

## <a name="config"></a>
# 4️⃣ CONFIGURACIÓN INICIAL

### Variables de entorno relevantes (`.env`)
```env
FLASK_ENV=development
FLASK_DEBUG=True
MONGO_URI=mongodb+srv://...
SECRET_KEY=...
EMAIL_FROM=...
EMAIL_PASSWORD=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID_ADMIN=...
SKINCARE_ENABLED=true   # feature flag, expuesto en GET /api/citas/config
```

`config.py` carga el `.env` desde la carpeta `backend/` usando `pathlib`, e imprime en consola si lo encontró (útil para debug de deploy).

---

## <a name="frontend-html"></a>
# 5️⃣ FRONTEND - PÁGINAS

| Página | Propósito |
|---|---|
| `index.html` | Landing page: hero, reviews, preview de servicios |
| `professionals.html` | Elegir profesional antes de reservar. Navbar "BOOK APPOINTMENT" apunta a sí misma **intencionalmente** (siempre se pasa primero por aquí, ya que no todos los profesionales usan `reserva.html`) |
| `servicios.html` | Catálogo de servicios y precios |
| `galeria.html` | Galería de trabajos |
| `sobre-nosotros.html` | Historia / equipo |
| `contacto.html` | Formulario de contacto |
| `reserva.html` | Formulario real de reserva: datos del cliente, tipo de servicio (`barber`/`skincare`), método de pago, día/hora según `barbero_id` |
| `cita.html` | Vista de detalles de una cita (confirmación) |
| `dashboard.html` | Panel privado del barbero/admin (requiere login JWT) |

**Flujo de reserva:** `professionals.html` → (según el profesional) → `reserva.html` (sistema interno) **o** enlace externo a Booksy/Square (profesionales que no usan el sistema propio).

---

## <a name="backend-python"></a>
# 6️⃣ BACKEND - RUTAS DE LA API

### `routes/citas.py` — prefijo `/api/citas`
- `GET /disponibles` — días disponibles (próximos 365 días, excluyendo domingos y días bloqueados) + horarios del día según la fecha (ver [Lógica de Horarios](#horarios))
- `GET /barberos` — lista barberos, filtrable por `tipo`
- `POST /crear` — crea una cita: valida duplicado (`dia`+`hora`+`barbero_id`+`estado=confirmada`), guarda en Mongo, envía email de confirmación al cliente, notifica por email al barbero asignado y al admin, notifica por Telegram, y crea evento en Google Calendar si aplica
- `GET /horarios-ocupados/<dia>` — horas ocupadas (citas confirmadas + slots bloqueados) para un barbero en un día
- `GET /<cita_id>` — detalle de una cita
- `PUT /<cita_id>/completada` — marca completada + email al cliente
- `PUT /<cita_id>/cancelar` — cancela + email al cliente
- `PUT /<cita_id>/reagendar` — cambia día/hora + email al cliente
- `GET /listar/todas` — todas las citas no canceladas
- `GET /barbero/<barbero_id>` — datos básicos de un barbero
- `GET /config` — feature flags públicos (`skincare_enabled`)
- `POST /bloquear-slot` / `DELETE /slots-bloqueados/<id>` / `GET /slots-bloqueados/<dia>` — bloqueo de horarios puntuales
- `POST /bloquear-dia` / `DELETE /dias-bloqueados/<id>` / `GET /dias-bloqueados/<dia>` — bloqueo de días completos (por barbero o para toda la barbería)

### `routes/autenticacion.py` — prefijo `/api/auth`
- `POST /registrar` — registra un barbero nuevo
- `POST /login` — login, devuelve JWT (7 días de validez)
- `GET /verificar` — valida un token
- `GET /barberos` — lista todos los barberos (solo admin)
- `PUT /barberos/<id>` — edita barbero (nombre, email, teléfono, tipo, contraseña, foto) — solo admin
- `DELETE /barberos/<id>` — elimina barbero (solo admin; no se puede eliminar al owner ni a sí mismo)
- `GET /perfil` — perfil del usuario autenticado actual

### `routes/dashboard.py` — prefijo `/api/dashboard` (todas protegidas con `@token_requerido`)
- `GET /citas` — admin ve todas, el resto solo las suyas
- `GET /citas/hoy` — citas del día actual
- `GET /citas/<id>` — detalle
- `PUT /citas/<id>/completar` — marcar completada
- `PUT /citas/<id>/reagendar` — reagendar (valida disponibilidad con `utils/validaciones.py`)
- `GET /perfil` — datos del barbero logueado

### `routes/telegram.py` — prefijo `/api/telegram`
- `POST /webhook` — único endpoint; recibe todos los updates de Telegram (ver sección Bot)

### Rutas estáticas (`app.py`)
- `GET /` → sirve `index.html`
- `GET /<path:filename>` → sirve cualquier archivo de `static/`
- `GET /favicon.ico`, `GET /uploads/<filename>` → archivos especiales
- `GET /api/test` → healthcheck

---

## <a name="modelos"></a>
# 7️⃣ MODELOS DE DATOS

- **`Cita`**: `cliente_nombre`, `cliente_email`, `cliente_telefono`, `dia`, `hora`, `servicio`, `metodoPago`, `precio`, `instrucciones`, `barbero_id`, `estado` (`confirmada`/`completada`/`cancelada`), `fecha_creacion`, `tipo_servicio` (`barber`/`skincare`, agregado al dict al crear).
- **`Barbero`**: `email`, `nombre`, `tipo` (`barber`/`skincare`), `telefono`, `foto` (ruta relativa), `contraseña_hash` (bcrypt). Puede tener `es_admin: True` y `google_token` (no están en el constructor pero se leen/usan en las rutas).
- **`Cliente`**: `nombre`, `email`, `telefono`, `historial_citas` (lista de IDs) — modelo definido pero no se usa activamente en las rutas actuales.

---

## <a name="servicios"></a>
# 8️⃣ SERVICIOS

- **`EmailService`** (Gmail/smtplib): `enviar_confirmacion`, `enviar_notificacion_barbero`, `enviar_cancelacion`, `enviar_reagendamiento`, `enviar_email` (genérico). Formatea fechas a `MM-DD-YYYY` y horas a formato 12h.
- **`GoogleCalendarService`**: autentica con el `google_token` guardado del barbero y crea un evento (`crear_evento`) con recordatorios (24h antes por email, 30 min antes por popup). Zona horaria fija: `America/Guatemala` (⚠️ revisar si debería ser la zona horaria de Seattle, dado que el negocio está en Seattle, WA según el footer).
- **`TelegramService`**: envío de mensajes al admin; comparte los helpers de formato de fecha/hora con `EmailService`.

---

## <a name="telegram-bot"></a>
# 9️⃣ BOT DE TELEGRAM

Todo pasa por un único webhook (`POST /api/telegram/webhook`). Solo el `TELEGRAM_CHAT_ID_ADMIN` puede ejecutar comandos administrativos.

**Comandos de texto:**
- `/start` — bienvenida
- `/me` — devuelve el Chat ID del usuario (para configurar notificaciones)
- `/help` — lista de comandos
- `/today` — menú para ver citas de hoy filtradas por tipo (Barbers/Skincare) y luego por barbero específico
- `/block MM/DD/YYYY` — bloquear un día (elige barbero específico o toda la barbería, vía botones)
- `/unblock MM/DD/YYYY` — desbloquear
- `/blocked` — lista de días bloqueados próximos

**Callbacks (botones inline):** `block|...`, `unblock|...`, `todaymenu|...`, `today|...` — navegación por menús para bloquear/consultar sin escribir comandos largos.

---

## <a name="horarios"></a>
# 🔟 LÓGICA DE HORARIOS

Definida en `routes/citas.py`, función `horarios_para(fecha)`:
- **Antes del 24 de agosto de 2026:** turnos de 40 min (`HORARIOS_VIEJOS`, 10:00–16:40)
- **Desde el 24 de agosto de 2026:** turnos de 45 min (`HORARIOS_45`, 09:45–16:30)
- **Sábados desde el 1 de septiembre de 2026:** jornada corta (`HORARIOS_SABADO`, 09:45–13:30)
- Domingos: cerrado (excluidos de `/disponibles`)

---

## <a name="cambios-recientes"></a>
# CAMBIOS RECIENTES

### Octubre 2026 — `professionals.html`
Nueva página de selección de profesional, entre la navegación general y la reserva. Muestra 5 tarjetas (Edy, David, Cameron, Adriana, Oscar) con foto, rol, Instagram y botón de reserva — interno (`reserva.html`) o externo (Booksy/Square), según el profesional. Todas las páginas informativas (`index`, `servicios`, `galeria`, `contacto`, `cita`, `sobre-nosotros`) actualizaron su navbar para apuntar aquí en vez de a `reserva.html` directamente.

### Julio 2026 — Ajustes visuales en `index.css`
1. **Grid de servicios centrado**: `grid-template-columns` cambiado de `repeat(auto-fit, minmax(250px, 1fr))` a `repeat(auto-fit, 280px)` + `justify-content: center`.
2. **Logo animado removido del hero**: `.hero::after { display: none; }` para quitar el logo semitransparente detrás del texto del hero.

*(Detalle histórico de la solución de double-booking y el fix de timezone: ver `SOLUCION_DOUBLE_BOOKING.md` e `INSTRUCCIONES_REPARACION.md`.)*

---

## <a name="deploy"></a>
# 1️⃣1️⃣ DEPLOY

**Producción real: VPS propio** (no Render — esa URL/referencia está desactualizada en docs viejas).

- **VPS:** `administrator@108.181.184.168`
- **Ruta del proyecto:** `/var/www/Golden-Shark-Barber` (el backend corre desde `/var/www/Golden-Shark-Barber/backend`)
- **Servicio:** `goldenshark.service` (systemd), corre como usuario `www-data`
  - `ExecStart=/usr/bin/python3 -m waitress --port=8000 app:app` (servidor WSGI **waitress**, no el dev server de Flask)
  - `Restart=always`, `RestartSec=10`
- Hay también una copia en `/root/Golden-Shark-Barber` — parece residual/sin usar, no la referencia el servicio.
- Falta confirmar la configuración de nginx/proxy inverso y HTTPS (no se encontró referencia a `8000` en `/etc/nginx/sites-enabled/` — revisar manualmente en el VPS cómo llega el tráfico público al puerto 8000).

### Deploy automático: `backend/deploy.py`
Script local (usa `paramiko`, pide la contraseña del VPS por `getpass`, no la expone en texto plano). Al ejecutarlo (`python deploy.py`) hace, en orden:
1. `git add -A`
2. `git commit -m "<mensaje que pidas>"`
3. `git push origin main`
4. Por SSH al VPS: `cd /var/www/Golden-Shark-Barber && git pull origin main`
5. `systemctl restart goldenshark`
6. `systemctl status goldenshark` (para confirmar que quedó arriba)

### Cache-busting: `update_versioning.py` (raíz del proyecto)
Actualiza el parámetro `?v=<timestamp>` en todos los `href`/`src` de CSS y JS de `backend/static/*.html`, reemplazando versiones viejas (no las concatena). Hace backup automático de cada archivo y lo borra si todo salió bien. **Se debe correr antes de cada commit/deploy** que toque CSS o JS (o HTML, para mantener consistencia), si no los navegadores pueden servir versiones cacheadas.
```bash
python update_versioning.py
```

### Deploy manual (si no se usa `deploy.py`)
```bash
# En local
git add -A
git commit -m "mensaje"
git push origin main

# En el VPS (por SSH)
cd /var/www/Golden-Shark-Barber
git pull origin main
systemctl restart goldenshark
systemctl status goldenshark
```

- **Desarrollo local:** `python app.py` (puerto 5000, `debug=True`). `ngrok` se usa para exponer el callback de Google OAuth en desarrollo.
- Scripts de mantenimiento en `backend/`: `cleanup_and_reindex.py`, `init_indexes.py`, `cleanup_citas.py`, `migrar_passwords.py`.

---

## ⚠️ PENDIENTES / A REVISAR
- `index-temp.html` y `reservaantigua.html` parecen archivos obsoletos — confirmar si se pueden eliminar.
- Zona horaria de Google Calendar está fija en `America/Guatemala`; el negocio está en Seattle, WA — verificar si es intencional.
- `Cliente.historial_citas` está modelado pero no se actualiza en ninguna ruta actual.
- `README.md` está vacío (solo el título).
- Confirmar configuración de nginx/proxy inverso y HTTPS en el VPS (no se encontró en `/etc/nginx/sites-enabled/`).
- Decidir si `/root/Golden-Shark-Barber` en el VPS se puede eliminar (copia residual sin usar).
