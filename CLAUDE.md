# 📖 DOCUMENTACIÓN COMPLETA - Gold Shark Barber
**Última actualización:** Julio 4, 2026  
**Estado:** 100% Funcional ✅

---

## 📋 TABLA DE CONTENIDOS
1. [Resumen del Proyecto](#resumen)
2. [Stack Tecnológico](#stack)
3. [Estructura de Archivos](#estructura)
4. [Configuración Inicial](#config)
5. [Frontend - HTML](#frontend-html)
6. [Frontend - CSS](#frontend-css)
7. [Frontend - JavaScript](#frontend-js)
8. [Backend - Python](#backend-python)
9. [Base de Datos](#database)
10. [Email Service](#email)
11. [API Endpoints](#api)
12. [Cambios Recientes](#cambios-recientes)
13. [Deploy](#deploy)

---

## <a name="cambios-recientes"></a>
# CAMBIOS RECIENTES (Julio 2026)

### 1. Grid de Servicios Centrado
**Archivo:** `backend/static/css/index.css`

**Problema:** Las tarjetas de servicios no aparecían centradas en pantallas grandes

**Solución:**
```css
.servicios-grid {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, 280px);  /* ← Cambio: 280px fijo */
    gap: 30px;
    justify-content: center;  /* ← Nuevo: centra items horizontalmente */
    margin-bottom: 40px;
}
```

**Cambios:**
- De: `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`
- A: `grid-template-columns: repeat(auto-fit, 280px)` (columnas de tamaño fijo)
- Agregado: `justify-content: center` para centrar el contenido del grid

**Por qué funciona:** Con `1fr`, las columnas se expandían para llenar todo el espacio. Con `280px` fijo y `justify-content: center`, las tarjetas se centra horizontalmente.

---

### 2. Logo Animado Removido del Hero
**Archivo:** `backend/static/css/index.css`

**Problema:** El logo que se veía detrás del texto "What's Up Brother" distrae del contenido

**Solución:**
```css
.hero::after {
    content: '';
    position: absolute;
    width: 75%;
    height: 75%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-image: url('/images/logo.jpeg');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    opacity: 0.15;
    animation: carouselLogo 8s ease-in-out infinite;
    z-index: 1;
    pointer-events: none;
    display: none;  /* ← Nuevo: oculta el elemento */
}
```

**Cambio:**
- Agregado: `display: none;` para ocultar el logo animado

---

## <a name="resumen"></a>
# 1️⃣ RESUMEN DEL PROYECTO

**Nombre:** Gold Shark Barber - Sistema de Citas  
**Objetivo:** Plataforma web para barbería permitiendo reservas online, dashboard para barbero y gestión automática de emails

**Características principales:**
- Landing page con carrusel de 15 reseñas de Google
- Sistema de reservas online
- Dashboard privado para barbero
- Gestión de citas (crear, completar, cancelar, reagendar)
- Emails automáticos a clientes
- Responsive design (mobile first)
- Grid de servicios centrado
- Hero section limpia sin elementos distractores

**URL:** https://golden-shark-barber.onrender.com  
**Repo:** https://github.com/rosbe6/Golden-Shark-Barber

---

## <a name="stack"></a>
# 2️⃣ STACK TECNOLÓGICO

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (mobile first, variables CSS, CSS Grid)
- **JavaScript Vanilla** - Interactividad (sin frameworks)

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **Flask-CORS** - Cross-origin requests
- **python-dotenv** - Variables de entorno

### Base de Datos
- **MongoDB Atlas** - Base de datos NoSQL en la nube
- **PyMongo** - Driver de Python para MongoDB

### Email
- **smtplib** - Envío de emails vía Gmail
- **email.mime** - Formato HTML para emails

### Autenticación
- **JWT (JSON Web Tokens)** - Token-based auth
- **bcrypt** - Hash de contraseñas

### Deploy
- **Render** - Hosting gratuito para backend
- **GitHub** - Control de versiones

### Herramientas
- **ngrok** - Tunneling para desarrollo local
- **Git** - Control de versiones

---

## <a name="estructura"></a>
# 3️⃣ ESTRUCTURA DE ARCHIVOS

```
proyecto-barberia-gold-shark/
│
├── CLAUDE.md                        # Documentación del proyecto
├── README.md
├── requirements.txt                 # Dependencias Python
├── .gitignore
├── .env.example
│
├── backend/
│   ├── app.py                      # Aplicación Flask principal
│   ├── config.py                   # Configuración
│   ├── database.py                 # Conexión MongoDB
│   │
│   ├── models/
│   │   └── cita.py                 # Modelo de cita
│   │
│   ├── routes/
│   │   ├── autenticacion.py        # Login/Logout
│   │   └── citas.py                # CRUD de citas
│   │
│   ├── services/
│   │   ├── email_service.py        # Envío de emails
│   │   └── google_calendar.py      # Integración Google Calendar
│   │
│   └── static/
│       ├── index.html              # Landing page
│       ├── servicios.html
│       ├── sobre-nosotros.html
│       ├── galeria.html
│       ├── contacto.html
│       ├── reserva.html            # Página de reservas
│       ├── cita.html               # Detalles de cita
│       ├── dashboard.html          # Dashboard barbero
│       │
│       ├── images/
│       │   ├── logo.jpeg
│       │   ├── instagram.svg
│       │   └── [otras imágenes]
│       │
│       ├── css/
│       │   ├── main.css            # Estilos generales
│       │   ├── index.css           # Estilos landing + reviews
│       │   ├── dashboard.css       # Estilos dashboard
│       │   ├── servicios.css
│       │   ├── galeria.css
│       │   └── [otros CSS]
│       │
│       └── js/
│           ├── navbar.js           # Navegación
│           ├── dashboard.js        # Dashboard interactivo
│           ├── reviews.js          # Carrusel de reseñas
│           ├── reservas.js
│           └── [otros JS]
│
└── .git/                            # Control de versiones
```

---

## <a name="config"></a>
# 4️⃣ CONFIGURACIÓN INICIAL

### Archivo: `.env`
```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# MongoDB
MONGO_URI=mongodb+srv://Rosbin890:Rosbin890@gold-shark-barber.urfzokl.mongodb.net/barberia?appName=Gold-Shark-Barber&tlsInsecure=true&serverSelectionTimeoutMS=5000

# Seguridad
SECRET_KEY=barberia-citas-secreta-2026

# Email
EMAIL_FROM=rosbinruanop@gmail.com
EMAIL_PASSWORD=mzzqpcelwjpdswjy

# Google OAuth (para futuro)
GOOGLE_CLIENT_ID=14198537742-8clngt9b845sakdgi0tahir2464shtkd.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://constant-harmonize-situated.ngrok-free.dev/auth/google/callback

# SendGrid (alternativa a Gmail)
SENDGRID_API_KEY=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
```

### Archivo: `requirements.txt`
```
Flask==2.3.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
PyMongo==4.3.0
bcrypt==4.0.0
PyJWT==2.6.0
requests==2.31.0
google-auth==2.20.0
google-auth-oauthlib==1.0.0
google-auth-httplib2==0.1.1
google-api-python-client==2.86.0
```

### Archivo: `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    
    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Email
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Google
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
```

---

## <a name="frontend-css"></a>
# 6️⃣ FRONTEND - CSS (Actualizado)

### `backend/static/css/index.css` - Estilos Landing

**Hero Section:**
```css
.hero {
    height: 600px;
    background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5));
    display: flex;
    align-items: center;
    color: white;
}

.hero::after {
    display: none;  /* Logo animado oculto */
}

.hero-title {
    font-size: 48px;
    font-weight: 700;
    line-height: 1.2;
    font-style: italic;
}

.hero-subtitle {
    color: #d4af37;
    text-transform: uppercase;
    letter-spacing: 2px;
}
```

**Reviews Section (Google Maps Style):**
```css
.reviews-section {
    padding: 60px 20px;
    background: #fff;
    text-align: center;
}

.carousel-wrapper {
    max-width: 700px;
    margin: 0 auto;
    overflow: hidden;
    border-radius: 8px;
    height: 140px;
}

.review-card {
    position: absolute;
    width: 100%;
    height: 100%;
    padding: 16px;
    background: #fff;
    border: 1px solid #dadce0;
    opacity: 0;
    transition: opacity 0.5s ease;
}

.review-card.active {
    opacity: 1;
}

.review-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #5f6368;
    color: #fff;
    font-weight: 600;
}

.review-stars {
    color: #fcc934;
}

.dot {
    width: 8px;
    height: 8px;
    background: #dadce0;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s;
}

.dot.active {
    background: #5f6368;
    width: 24px;
}

.btn-write-review {
    display: block;
    margin: 20px auto 0;
    padding: 10px 24px;
    background: #1f2937;
    color: #fff;
    width: fit-content;
    text-decoration: none;
    border-radius: 4px;
    transition: all 0.3s;
}

.btn-write-review:hover {
    background: #d4af37;
    color: #000;
}
```

**Services Section (ACTUALIZADO):**
```css
.servicios-preview {
    padding: 80px 20px;
    text-align: center;
}

.servicios-grid {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, 280px);  /* Columnas fijas de 280px */
    gap: 30px;
    justify-content: center;  /* CENTRADO HORIZONTAL */
    margin-bottom: 40px;
}

.servicio-card {
    padding: 40px 30px;
    background: #f9f9f9;
    border-radius: 8px;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.servicio-card:hover {
    background: #fff;
    border-color: #d4af37;
    transform: translateY(-10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.servicio-icon {
    font-size: 48px;
    margin-bottom: 20px;
}

.servicio-card h3 {
    font-size: 20px;
    font-weight: 600;
    color: #000;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.servicio-card .precio {
    font-size: 16px;
    font-weight: 700;
    color: #d4af37;
    margin-bottom: 10px;
}

.servicio-card p {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}
```

**Responsive:**
```css
@media (max-width: 768px) {
    .hero { height: 400px; }
    .hero-title { font-size: 32px; }
    .carousel-wrapper { height: 150px; }
    .servicios-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .hero { height: 350px; }
    .hero-title { font-size: 24px; }
    .carousel-wrapper { height: 160px; }
    .servicios-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## NOTAS IMPORTANTES

✅ **Grid centrado en todas las resoluciones**
- Desktop: Múltiples columnas de 280px, centradas
- Tablet: 1 columna
- Mobile: 1 columna

✅ **Hero limpio sin distracciones**
- Logo animado removido
- Texto más legible

✅ **Mobile-first approach**
- Responsive desde 320px hasta 1920px
- Todas las secciones se adaptan correctamente
