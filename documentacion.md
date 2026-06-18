# 📖 DOCUMENTACIÓN COMPLETA - Gold Shark Barber
**Última actualización:** Junio 18, 2026  
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
12. [Flujos de Datos](#flujos)
13. [Deploy](#deploy)
14. [Pendiente](#pendiente)

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

**URL:** https://golden-shark-barber.onrender.com  
**Repo:** https://github.com/rosbe6/Golden-Shark-Barber

---

## <a name="stack"></a>
# 2️⃣ STACK TECNOLÓGICO

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (mobile first, variables CSS)
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
│       │   ├── ig.svg
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

## <a name="frontend-html"></a>
# 5️⃣ FRONTEND - HTML

### `backend/static/index.html` - Landing Page
**Secciones:**
1. **Navbar** - Navegación responsive con hamburger menu
2. **Hero** - Sección principal "What's Up Brother"
3. **Reviews Carousel** - 15 reseñas con iniciales en círculo
4. **Services Preview** - Preview de servicios
5. **About Us** - Información de la barbería
6. **Gallery** - Posts de Instagram embebidos
7. **CTA Section** - Call to action final
8. **Footer** - Links y contacto

**Código HTML principal:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>golden Shark Barber</title>
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/index.css">
</head>
<body>
    <!-- NAVBAR -->
    <nav class="navbar">
        <div class="navbar-container">
            <div class="logo">
                <img src="images/logo.jpeg" alt="Logo" class="logo-img">
            </div>
            <button class="hamburger" id="hamburger">☰</button>
            <ul class="nav-menu" id="navMenu">
                <li><a href="index.html" class="active">HOME</a></li>
                <li><a href="servicios.html">SERVICES</a></li>
                <li><a href="galeria.html">GALLERY</a></li>
                <li><a href="sobre-nosotros.html">ABOUT US</a></li>
                <li><a href="contacto.html">CONTACT</a></li>
            </ul>
            <div class="nav-buttons">
                <a href="reserva.html" class="btn-book">BOOK APPOINTMENT</a>
            </div>
        </div>
    </nav>

    <!-- HERO SECTION -->
    <section class="hero">
        <div class="hero-content">
            <h2 class="hero-title">What's<br>Up<br>Brother</h2>
            <p class="hero-subtitle">1432 12th Ave, Seattle, WA 98122</p>
            <p class="hero-description">Experience quality haircuts with professionalism and style.</p>
            <div class="hero-bottom">
                <a href="reserva.html" class="btn-primary">Book Now</a>
                <a href="https://www.instagram.com/golden_sharkb..." class="social-link">
                    <img src="images/ig.svg" alt="Instagram" style="width: 40px; height: 40px;">
                </a>
            </div>
        </div>
    </section>

    <!-- REVIEWS CAROUSEL -->
    <section class="reviews-section">
        <h2>Customer Reviews</h2>
        <div class="carousel-container">
            <div class="carousel-wrapper">
                <div class="carousel" id="reviewsCarousel"></div>
            </div>
            <div class="carousel-dots" id="carouselDots"></div>
        </div>
        <a href="https://www.google.com/maps/place/Golden+Shark+Barber/..." 
           target="_blank" class="btn-write-review">
            Write your review on Google Maps
        </a>
    </section>

    <!-- Resto de secciones... -->

    <script src="js/navbar.js"></script>
    <script src="js/reviews.js"></script>
</body>
</html>
```

### `backend/static/dashboard.html` - Dashboard Barbero
**Secciones:**
1. **Login Screen** - Formulario de autenticación
2. **Dashboard Screen** - Vista principal con stats y citas
3. **Modales** - Detalles, cancelación, reagendamiento

**Estructura HTML:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Gold Shark Barber</title>
    <link rel="stylesheet" href="css/dashboard.css">
</head>
<body>
    <!-- PANTALLA LOGIN -->
    <div class="screen login-screen" id="screenLogin">
        <div class="login-container">
            <h1>Barber Dashboard</h1>
            <p>Gold Shark Barber</p>
            <form id="formLogin" class="login-form">
                <input type="email" id="inputEmail" placeholder="Email" required>
                <input type="password" id="inputPassword" placeholder="Password" required>
                <button type="submit" class="btn-primary">Sign In</button>
                <div id="errorLogin" class="error-box hidden"></div>
            </form>
        </div>
    </div>

    <!-- PANTALLA DASHBOARD -->
    <div class="screen dashboard-screen hidden" id="screenDashboard">
        <div class="dashboard-top">
            <h1>Dashboard</h1>
            <div class="top-right">
                <span id="textNombre"></span>
                <button id="btnLogout" class="btn-logout">Logout</button>
            </div>
        </div>

        <!-- STATS -->
        <div class="stats-box">
            <div class="stat">
                <div class="stat-num" id="statToday">0</div>
                <div class="stat-label">Today</div>
            </div>
            <div class="stat">
                <div class="stat-num" id="statWeek">0</div>
                <div class="stat-label">This Week</div>
            </div>
            <div class="stat">
                <div class="stat-num" id="statCompleted">0</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat">
                <div class="stat-num" id="statTotal">0</div>
                <div class="stat-label">Total</div>
            </div>
        </div>

        <!-- CITAS -->
        <div class="citas-container">
            <h2>Appointments</h2>
            <div class="filter-box">
                <button class="filter-tab active" data-filter="all">All</button>
                <button class="filter-tab" data-filter="today">Today</button>
                <button class="filter-tab" data-filter="week">Week</button>
                <button class="filter-tab" data-filter="completed">Completed</button>
            </div>
            <div id="citasBox" class="citas-grid"></div>
            <div id="emptyBox" class="empty-msg hidden">No appointments</div>
        </div>
    </div>

    <!-- MODALES -->
    <div class="modal hidden" id="modalDetails">
        <!-- Detalles de cita -->
    </div>

    <div class="modal hidden" id="modalCancel">
        <!-- Cancelación -->
    </div>

    <div class="modal hidden" id="modalReschedule">
        <!-- Reagendamiento -->
    </div>

    <script src="js/dashboard.js"></script>
</body>
</html>
```

### `backend/static/reserva.html` - Página de Reservas
- Formulario con campos: nombre, email, teléfono, servicio, fecha, hora, método de pago
- Validación cliente-side
- POST a `/api/citas/crear`

### Otras páginas
- `servicios.html` - Listado de servicios
- `sobre-nosotros.html` - Información de la barbería
- `galeria.html` - Galería de trabajos (Instagram)
- `contacto.html` - Formulario de contacto
- `cita.html` - Vista de detalles de cita (para clientes)

---

## <a name="frontend-css"></a>
# 6️⃣ FRONTEND - CSS

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

**Services Section:**
```css
.servicios-preview {
    padding: 80px 20px;
    text-align: center;
}

.servicios-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

.servicio-card {
    padding: 40px 30px;
    background: #f9f9f9;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.servicio-card:hover {
    background: #fff;
    border: 2px solid #d4af37;
    transform: translateY(-10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
```

**Responsive:**
```css
@media (max-width: 768px) {
    .hero { height: 400px; }
    .hero-title { font-size: 32px; }
    .carousel-wrapper { height: 150px; }
}

@media (max-width: 480px) {
    .hero { height: 350px; }
    .hero-title { font-size: 24px; }
    .carousel-wrapper { height: 160px; }
}
```

### `backend/static/css/dashboard.css` - Estilos Dashboard

**Login Screen:**
```css
.login-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
}

.login-container {
    background: #fff;
    padding: 40px 25px;
    border-radius: 8px;
    text-align: center;
    max-width: 450px;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.login-form input {
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 4px;
}

.login-form input:focus {
    outline: none;
    border-color: #d4af37;
}
```

**Dashboard Stats:**
```css
.stats-box {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 20px;
    background: #f9f9f9;
}

.stat {
    background: #fff;
    padding: 15px;
    text-align: center;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

.stat-num {
    font-size: 24px;
    font-weight: 700;
    color: #d4af37;
}

.stat-label {
    font-size: 11px;
    color: #999;
    text-transform: uppercase;
}
```

**Citas Grid:**
```css
.citas-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
}

.cita-card {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 12px;
    cursor: pointer;
    transition: all 0.3s;
}

.cita-card:hover {
    border-color: #d4af37;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
}

.badge {
    padding: 3px 8px;
    border-radius: 10px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-pending {
    background: #fff3cd;
    color: #856404;
}

.badge-completed {
    background: #d4edda;
    color: #155724;
}
```

**Modales:**
```css
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
}

.modal:not(.hidden) {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-box {
    background: #fff;
    padding: 25px;
    border-radius: 6px;
    max-width: 500px;
    position: relative;
}

.close-modal {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
}

.details-table {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
    font-size: 12px;
}
```

---

## <a name="frontend-js"></a>
# 7️⃣ FRONTEND - JAVASCRIPT

### `backend/static/js/navbar.js` - Navegación
```javascript
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');

hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Cerrar menú al hacer click en un link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});
```

### `backend/static/js/dashboard.js` - Dashboard Completo

**Variables globales:**
```javascript
const API_URL = 'https://constant-harmonize-situated.ngrok-free.dev/api';
let allCitas = [];
let selectedCita = null;
let barberoToken = null;
let barberoName = null;
```

**Inicialización:**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    checkLogin();
    setupEvents();
});

function checkLogin() {
    const token = localStorage.getItem('barber_token');
    const name = localStorage.getItem('barber_name');

    if (token && name) {
        barberoToken = token;
        barberoName = name;
        showDashboard();
        loadCitas();
    } else {
        showLogin();
    }
}

function setupEvents() {
    // Login
    document.getElementById('formLogin').addEventListener('submit', handleLogin);
    document.getElementById('btnLogout').addEventListener('click', handleLogout);

    // Filters
    document.querySelectorAll('.filter-tab').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filterCitas(e.target.dataset.filter);
        });
    });

    // Modal buttons
    document.getElementById('btnMarcaCompletada').addEventListener('click', markComplete);
    document.getElementById('btnCancelarCita').addEventListener('click', openCancelModal);
    document.getElementById('btnReagendar').addEventListener('click', openRescheduleModal);
    document.getElementById('btnConfirmCancel').addEventListener('click', confirmCancel);
    document.getElementById('btnConfirmReschedule').addEventListener('click', confirmReschedule);
}
```

**Login:**
```javascript
async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('inputEmail').value;
    const password = document.getElementById('inputPassword').value;

    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, contraseña: password })
        });

        const data = await response.json();

        if (data.status === 'success') {
            barberoToken = data.token;
            barberoName = data.nombre;

            localStorage.setItem('barber_token', barberoToken);
            localStorage.setItem('barber_name', barberoName);

            showDashboard();
            loadCitas();
        } else {
            showLoginError(data.mensaje || 'Error logging in');
        }
    } catch (error) {
        console.error('Error:', error);
        showLoginError('Connection error');
    } finally {
        showLoading(false);
    }
}

function handleLogout() {
    localStorage.removeItem('barber_token');
    localStorage.removeItem('barber_name');
    showLogin();
}
```

**Cargar y renderizar citas:**
```javascript
async function loadCitas() {
    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/citas/listar/todas`);
        const data = await response.json();

        if (data.status === 'success') {
            allCitas = data.citas || [];
            renderCitas(allCitas);
            updateStats();
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

function renderCitas(citas) {
    const box = document.getElementById('citasBox');
    const empty = document.getElementById('emptyBox');

    if (citas.length === 0) {
        box.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');

    box.innerHTML = citas.map(c => `
        <div class="cita-card" onclick="openDetailsModal('${c._id}')">
            <div class="card-top">
                <h3>${c.cliente_nombre}</h3>
                <span class="badge ${c.estado === 'completada' ? 'badge-completed' : 'badge-pending'}">
                    ${c.estado === 'completada' ? 'Completed' : 'Pending'}
                </span>
            </div>
            
            <div class="card-info">
                <div class="info-line">
                    <span class="info-key">📅 Date</span>
                    <span class="info-val">${c.dia}</span>
                </div>
                <div class="info-line">
                    <span class="info-key">⏰ Time</span>
                    <span class="info-val">${c.hora}</span>
                </div>
                <div class="info-line">
                    <span class="info-key">💈 Service</span>
                    <span class="info-val">${c.servicio}</span>
                </div>
                <div class="info-line">
                    <span class="info-key">💰 Price</span>
                    <span class="info-val">$${c.precio}</span>
                </div>
            </div>

            <div class="card-btns">
            ${c.estado === 'completada' ? '' : `
                <button class="btn-card btn-card-main" onclick="event.stopPropagation(); markComplete('${c._id}')">
                    Complete
                </button>
                <button class="btn-card btn-card-sec" onclick="event.stopPropagation(); openDetailsModal('${c._id}')">
                    Details
                </button>
            `}
        </div>
        </div>
    `).join('');
}

function filterCitas(filter) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);

    let filtered = allCitas;

    if (filter === 'today') {
        filtered = allCitas.filter(c => {
            const d = new Date(c.dia);
            return d.toDateString() === today.toDateString() && c.estado !== 'completada';
        });
    } else if (filter === 'week') {
        filtered = allCitas.filter(c => {
            const d = new Date(c.dia);
            return d >= today && d <= nextWeek && c.estado !== 'completada';
        });
    } else if (filter === 'completed') {
        filtered = allCitas.filter(c => c.estado === 'completada');
    } else if (filter === 'all') {
        filtered = allCitas.filter(c => c.estado !== 'completada');
    }

    renderCitas(filtered);
}

function updateStats() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);

    const citasToday = allCitas.filter(c => {
        const d = new Date(c.dia);
        return d.toDateString() === today.toDateString();
    }).length;

    const citasWeek = allCitas.filter(c => {
        const d = new Date(c.dia);
        return d >= today && d <= nextWeek;
    }).length;

    const citasCompleted = allCitas.filter(c => c.estado === 'completada').length;

    document.getElementById('statToday').textContent = citasToday;
    document.getElementById('statWeek').textContent = citasWeek;
    document.getElementById('statCompleted').textContent = citasCompleted;
    document.getElementById('statTotal').textContent = allCitas.length;
}
```

**Modales:**
```javascript
function openDetailsModal(citaId) {
    selectedCita = allCitas.find(c => c._id === citaId);

    if (!selectedCita) return;

    document.getElementById('detClient').textContent = selectedCita.cliente_nombre;
    document.getElementById('detEmail').textContent = selectedCita.cliente_email;
    document.getElementById('detPhone').textContent = selectedCita.cliente_telefono;
    document.getElementById('detDate').textContent = selectedCita.dia;
    document.getElementById('detTime').textContent = selectedCita.hora;
    document.getElementById('detService').textContent = selectedCita.servicio;
    document.getElementById('detPrice').textContent = `$${selectedCita.precio}`;
    document.getElementById('detStatus').textContent = selectedCita.estado === 'completada' ? 'Completed' : 'Pending';

    const isCompleted = selectedCita.estado === 'completada';
    document.getElementById('btnMarcaCompletada').disabled = isCompleted;
    document.getElementById('btnCancelarCita').disabled = isCompleted;
    document.getElementById('btnReagendar').disabled = isCompleted;

    document.getElementById('modalDetails').classList.remove('hidden');
}

function closeDetailsModal() {
    document.getElementById('modalDetails').classList.add('hidden');
}
```

**Completar cita:**
```javascript
async function markComplete(citaId) {
    const cid = citaId || (selectedCita && selectedCita._id);
    if (!cid) return;

    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/citas/${cid}/completada`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeDetailsModal();
            loadCitas();
            alert('✅ Marked as completed!');
        } else {
            alert('Error: ' + data.mensaje);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error marking appointment');
    } finally {
        showLoading(false);
    }
}
```

**Cancelar cita:**
```javascript
function openCancelModal() {
    closeDetailsModal();
    document.getElementById('modalCancel').classList.remove('hidden');
    document.getElementById('textCancelReason').value = '';
}

function closeCancelModal() {
    document.getElementById('modalCancel').classList.add('hidden');
}

async function confirmCancel() {
    const reason = document.getElementById('textCancelReason').value.trim();

    if (!reason) {
        alert('Please enter a reason');
        return;
    }

    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/citas/${selectedCita._id}/cancelar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo: reason })
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeCancelModal();
            loadCitas();
            alert('✅ Appointment cancelled! Email sent to client.');
        } else {
            alert('Error: ' + data.mensaje);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error cancelling appointment');
    } finally {
        showLoading(false);
    }
}
```

**Reagendar cita:**
```javascript
function openRescheduleModal() {
    closeDetailsModal();
    document.getElementById('modalReschedule').classList.remove('hidden');
    document.getElementById('inputNewDate').value = '';
    document.getElementById('selectNewTime').innerHTML = '<option value="">Select time...</option>';
    document.getElementById('inputRescheduleReason').value = '';
}

function closeRescheduleModal() {
    document.getElementById('modalReschedule').classList.add('hidden');
}

async function loadTimesForDate() {
    const date = document.getElementById('inputNewDate').value;
    if (!date) return;

    try {
        const response = await fetch(`${API_URL}/citas/horarios-ocupados/${date}`);
        const data = await response.json();

        const allTimes = ['10:00', '10:40', '11:20', '12:00', '12:40', '13:20', '14:00', '14:40', '15:20', '16:00', '16:40'];
        const occupied = data.horas_ocupadas || [];
        const available = allTimes.filter(t => !occupied.includes(t));

        const select = document.getElementById('selectNewTime');
        select.innerHTML = '<option value="">Select time...</option>' + 
            available.map(t => `<option value="${t}">${t}</option>`).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function confirmReschedule() {
    const newDate = document.getElementById('inputNewDate').value;
    const newTime = document.getElementById('selectNewTime').value;
    const reason = document.getElementById('inputRescheduleReason').value || 'Client request';

    if (!newDate || !newTime) {
        alert('Please select new date and time');
        return;
    }

    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/citas/${selectedCita._id}/reagendar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nueva_fecha: newDate,
                nueva_hora: newTime,
                motivo: reason
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeRescheduleModal();
            loadCitas();
            alert('✅ Appointment rescheduled! Email sent to client.');
        } else {
            alert('Error: ' + data.mensaje);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error rescheduling appointment');
    } finally {
        showLoading(false);
    }
}
```

---

## <a name="backend-python"></a>
# 8️⃣ BACKEND - PYTHON

### `backend/app.py` - Aplicación Flask
```python
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from routes.autenticacion import autenticacion_bp
from routes.citas import citas_bp

# Cargar variables de entorno
load_dotenv()

# Crear aplicación
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Registrar blueprints
app.register_blueprint(autenticacion_bp)
app.register_blueprint(citas_bp)

# Rutas
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'status': 'error', 'mensaje': 'Not found'}, 404

@app.errorhandler(500)
def server_error(error):
    return {'status': 'error', 'mensaje': 'Server error'}, 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### `backend/database.py` - Conexión MongoDB
```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        try:
            mongo_uri = os.getenv('MONGO_URI')
            self.client = MongoClient(mongo_uri)
            self.db = self.client.barberia
            print(f"✅ Conectado a MongoDB: {self.db.name}")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {str(e)}")
    
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def close(self):
        if self.client:
            self.client.close()

# Instancia global
mongodb = MongoDB()
```

### `backend/models/cita.py` - Modelo de Cita
```python
from datetime import datetime

class Cita:
    def __init__(self, cliente_nombre, cliente_email, cliente_telefono, 
                 dia, hora, servicio, metodoPago, precio, instrucciones=''):
        self.cliente_nombre = cliente_nombre
        self.cliente_email = cliente_email
        self.cliente_telefono = cliente_telefono
        self.dia = dia
        self.hora = hora
        self.servicio = servicio
        self.metodoPago = metodoPago
        self.precio = precio
        self.instrucciones = instrucciones
        self.estado = 'pendiente'
        self.creada_en = datetime.now().isoformat()
        self.motivo_cancelacion = None
        self.motivo_reagendamiento = None
    
    def to_dict(self):
        return {
            'cliente_nombre': self.cliente_nombre,
            'cliente_email': self.cliente_email,
            'cliente_telefono': self.cliente_telefono,
            'dia': self.dia,
            'hora': self.hora,
            'servicio': self.servicio,
            'metodoPago': self.metodoPago,
            'precio': self.precio,
            'instrucciones': self.instrucciones,
            'estado': self.estado,
            'creada_en': self.creada_en,
            'motivo_cancelacion': self.motivo_cancelacion,
            'motivo_reagendamiento': self.motivo_reagendamiento
        }
```

### `backend/routes/autenticacion.py` - Login
```python
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import os
from database import mongodb

autenticacion_bp = Blueprint('autenticacion', __name__, url_prefix='/api/auth')

@autenticacion_bp.route('/login', methods=['POST'])
def login():
    """Login para barbero"""
    try:
        data = request.get_json()
        email = data.get('email')
        contrasena = data.get('contraseña')  # Nota: con tilde
        
        if not email or not contrasena:
            return jsonify({
                'status': 'error',
                'mensaje': 'Email y contraseña requeridos'
            }), 400
        
        # Buscar barbero en BD
        barbero = mongodb.db.barbero.find_one({'email': email})
        
        if not barbero:
            return jsonify({
                'status': 'error',
                'mensaje': 'Usuario no encontrado'
            }), 404
        
        # Validar contraseña (en producción usar bcrypt)
        if barbero.get('contrasena') != contrasena:
            return jsonify({
                'status': 'error',
                'mensaje': 'Contraseña incorrecta'
            }), 401
        
        # Generar token JWT
        payload = {
            'barbero_id': str(barbero['_id']),
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
        
        return jsonify({
            'status': 'success',
            'token': token,
            'barbero_id': str(barbero['_id']),
            'nombre': barbero.get('nombre', 'Barbero')
        }), 200
        
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500
```

### `backend/routes/citas.py` - CRUD de Citas
```python
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb
from models.cita import Cita
from services.email_service import EmailService

citas_bp = Blueprint('citas', __name__, url_prefix='/api/citas')
email_service = EmailService()

@citas_bp.route('/crear', methods=['POST'])
def crear_cita():
    """Crear nueva cita"""
    try:
        data = request.get_json()
        
        # Validar datos
        campos_requeridos = ['cliente_nombre', 'cliente_email', 'cliente_telefono', 
                            'dia', 'hora', 'servicio', 'metodoPago', 'precio']
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'status': 'error',
                    'mensaje': f'Falta: {campo}'
                }), 400
        
        # Crear cita
        cita = Cita(
            cliente_nombre=data['cliente_nombre'],
            cliente_email=data['cliente_email'],
            cliente_telefono=data['cliente_telefono'],
            dia=data['dia'],
            hora=data['hora'],
            servicio=data['servicio'],
            metodoPago=data['metodoPago'],
            precio=int(data['precio']),
            instrucciones=data.get('instrucciones', '')
        )
        
        # Guardar en BD
        resultado = mongodb.db.citas.insert_one(cita.to_dict())
        cita_id = str(resultado.inserted_id)
        
        # Enviar email de confirmación
        try:
            email_service.enviar_confirmacion(data, cita_id)
            print(f"✅ Email de confirmación enviado a {data['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error email: {str(e)}")
        
        # Notificar barbero
        try:
            barbero = mongodb.db.barbero.find_one()
            if barbero and barbero.get('email'):
                email_service.enviar_notificacion_barbero(data, cita_id, barbero['email'])
        except Exception as e:
            print(f"⚠️ Error notificación barbero: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'cita_id': cita_id,
            'mensaje': 'Cita creada'
        }), 201
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/listar/todas', methods=['GET'])
def listar_citas():
    """Listar todas las citas"""
    try:
        citas = list(mongodb.db.citas.find({'estado': {'$ne': 'cancelada'}}))
        
        for cita in citas:
            cita['_id'] = str(cita['_id'])
        
        return jsonify({
            'status': 'success',
            'citas': citas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/<cita_id>', methods=['GET'])
def obtener_cita(cita_id):
    """Obtener detalles de una cita"""
    try:
        cita = mongodb.db.citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        cita['_id'] = str(cita['_id'])
        
        return jsonify({'status': 'success', 'cita': cita}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/horarios-ocupados/<dia>', methods=['GET'])
def horarios_ocupados(dia):
    """Obtener horas ocupadas para un día"""
    try:
        citas = mongodb.db.citas.find({
            'dia': dia,
            'estado': {'$ne': 'cancelada'}
        })
        
        horas_ocupadas = [c['hora'] for c in citas]
        
        return jsonify({
            'status': 'success',
            'dia': dia,
            'horas_ocupadas': horas_ocupadas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/<cita_id>/completada', methods=['PUT'])
def marcar_completada(cita_id):
    """Marcar cita como completada"""
    try:
        cita = mongodb.db.citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        mongodb.db.citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {'estado': 'completada'}}
        )
        
        return jsonify({'status': 'success', 'mensaje': 'Completada'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/<cita_id>/cancelar', methods=['PUT'])
def cancelar_cita(cita_id):
    """Cancelar cita con motivo"""
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Sin especificar')
        
        cita = mongodb.db.citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        mongodb.db.citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {
                'estado': 'cancelada',
                'motivo_cancelacion': motivo
            }}
        )
        
        # ENVIAR EMAIL DE CANCELACIÓN
        try:
            email_service.enviar_cancelacion(cita, motivo)
            print(f"✅ Email de cancelación enviado a {cita['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error email: {str(e)}")
        
        return jsonify({'status': 'success', 'mensaje': 'Cancelada'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/<cita_id>/reagendar', methods=['PUT'])
def reagendar_cita(cita_id):
    """Reagendar cita a nueva fecha y hora"""
    try:
        data = request.get_json()
        nueva_fecha = data.get('nueva_fecha')
        nueva_hora = data.get('nueva_hora')
        motivo = data.get('motivo', 'Client request')
        
        if not nueva_fecha or not nueva_hora:
            return jsonify({'status': 'error', 'mensaje': 'Faltan fecha u hora'}), 400
        
        cita = mongodb.db.citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        mongodb.db.citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {
                'dia': nueva_fecha,
                'hora': nueva_hora,
                'motivo_reagendamiento': motivo,
                'estado': 'pendiente'
            }}
        )
        
        # ENVIAR EMAIL DE REAGENDAMIENTO
        try:
            email_service.enviar_reagendamiento(cita, nueva_fecha, nueva_hora, motivo)
            print(f"✅ Email de reagendamiento enviado a {cita['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error email: {str(e)}")
        
        return jsonify({'status': 'success', 'mensaje': 'Reagendada'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500
```

---

## <a name="email"></a>
# 9️⃣ EMAIL SERVICE

### `backend/services/email_service.py` - Servicio Completo
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        if not self.email_from or not self.email_password:
            print("❌ ERROR: EMAIL_FROM o EMAIL_PASSWORD no configurados")
        else:
            print(f"✅ Email configurado: {self.email_from}")
    
    def enviar_email(self, to, subject, html):
        """Método público para enviar email"""
        return self._enviar_email(to, subject, html)
    
    def enviar_confirmacion(self, cita_data, cita_id):
        """Enviar email de confirmación"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 30px; background: white;">
                    <h2 style="color: #007bff;">✓ Your appointment is confirmed!</h2>
                    <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                    <p>Thank you for booking with <strong>Gold Shark Barber</strong>.</p>
                    
                    <div style="background: #f9f9f9; padding: 20px; margin: 30px 0;">
                        <h3 style="color: #007bff;">Appointment Details:</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Service:</strong></td>
                                <td>{cita_data['servicio']}</td>
                            </tr>
                            <tr>
                                <td><strong>Date:</strong></td>
                                <td>{cita_data['dia']}</td>
                            </tr>
                            <tr>
                                <td><strong>Time:</strong></td>
                                <td>{cita_data['hora']}</td>
                            </tr>
                            <tr>
                                <td><strong>Price:</strong></td>
                                <td>${cita_data['precio']}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>If you need to cancel or reschedule, please contact us.</p>
                    <p style="text-align: center; margin-top: 30px;">
                        <strong>Gold Shark Barber</strong><br>
                        We look forward to seeing you!
                    </p>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Confirmed - {cita_data['dia']} at {cita_data['hora']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_cancelacion(self, cita_data, motivo):
        """Enviar email de cancelación"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 30px; background: white;">
                    <h2 style="color: #dc3545;">✗ Appointment Cancelled</h2>
                    <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                    <p>Your appointment has been cancelled.</p>
                    
                    <div style="background: #ffe8e8; padding: 20px; margin: 30px 0;">
                        <h3 style="color: #dc3545;">Cancelled Appointment:</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Date:</strong></td>
                                <td>{cita_data['dia']}</td>
                            </tr>
                            <tr>
                                <td><strong>Time:</strong></td>
                                <td>{cita_data['hora']}</td>
                            </tr>
                            <tr>
                                <td><strong>Service:</strong></td>
                                <td>{cita_data['servicio']}</td>
                            </tr>
                            <tr>
                                <td><strong>Reason:</strong></td>
                                <td>{motivo}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>You can book a new appointment at any time.</p>
                    <p style="text-align: center; margin-top: 30px;">
                        <strong>Gold Shark Barber</strong>
                    </p>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Cancelled - {cita_data['dia']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_reagendamiento(self, cita_data, nueva_fecha, nueva_hora, motivo):
        """Enviar email de reagendamiento"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 30px; background: white;">
                    <h2 style="color: #ffc107;">📅 Appointment Rescheduled</h2>
                    <p>Hi <strong>{cita_data['cliente_nombre']}</strong>,</p>
                    <p>Your appointment has been rescheduled.</p>
                    
                    <div style="background: #fff8f0; padding: 20px; margin: 30px 0;">
                        <h3 style="color: #ffc107;">New Appointment:</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Previous Date:</strong></td>
                                <td><s>{cita_data['dia']}</s></td>
                            </tr>
                            <tr>
                                <td><strong>New Date:</strong></td>
                                <td style="color: #28a745;"><strong>{nueva_fecha}</strong></td>
                            </tr>
                            <tr>
                                <td><strong>New Time:</strong></td>
                                <td style="color: #28a745;"><strong>{nueva_hora}</strong></td>
                            </tr>
                            <tr>
                                <td><strong>Service:</strong></td>
                                <td>{cita_data['servicio']}</td>
                            </tr>
                            <tr>
                                <td><strong>Reason:</strong></td>
                                <td>{motivo}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>Please confirm you can attend at the new time.</p>
                    <p style="text-align: center; margin-top: 30px;">
                        <strong>Gold Shark Barber</strong>
                    </p>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=cita_data['cliente_email'],
                subject=f"Appointment Rescheduled - New Date: {nueva_fecha}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def enviar_notificacion_barbero(self, cita_data, cita_id, email_barbero):
        """Enviar notificación al barbero"""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 30px; background: white;">
                    <h2 style="color: #28a745;">📅 New Appointment!</h2>
                    <p>A new appointment has been booked.</p>
                    
                    <div style="background: #f0f8f0; padding: 20px; margin: 30px 0;">
                        <h3>Appointment Details:</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Client:</strong></td>
                                <td>{cita_data['cliente_nombre']}</td>
                            </tr>
                            <tr>
                                <td><strong>Email:</strong></td>
                                <td>{cita_data['cliente_email']}</td>
                            </tr>
                            <tr>
                                <td><strong>Phone:</strong></td>
                                <td>{cita_data['cliente_telefono']}</td>
                            </tr>
                            <tr>
                                <td><strong>Date:</strong></td>
                                <td>{cita_data['dia']}</td>
                            </tr>
                            <tr>
                                <td><strong>Time:</strong></td>
                                <td>{cita_data['hora']}</td>
                            </tr>
                            <tr>
                                <td><strong>Service:</strong></td>
                                <td>{cita_data['servicio']}</td>
                            </tr>
                            <tr>
                                <td><strong>Price:</strong></td>
                                <td>${cita_data['precio']}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>Check your dashboard for more details.</p>
                </div>
            </body>
            </html>
            """
            
            self._enviar_email(
                to=email_barbero,
                subject=f"New Appointment - {cita_data['cliente_nombre']}",
                html=html
            )
            
            return {'status': 'success'}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'status': 'error', 'mensaje': str(e)}
    
    def _enviar_email(self, to, subject, html):
        """Enviar email genérico"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = to
            msg['Reply-To'] = self.email_from
            
            text_part = MIMEText('Please view in HTML', 'plain', 'utf-8')
            html_part = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Conectar a Gmail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email_from, self.email_password)
            server.sendmail(self.email_from, to, msg.as_string())
            server.quit()
            
            print(f"✅ Email enviado a {to}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
```

---

## <a name="api"></a>
# 🔟 API ENDPOINTS

### Authentication
```
POST /api/auth/login
├─ Body: { "email": "...", "contraseña": "..." }
└─ Response: { "status": "success", "token": "...", "barbero_id": "...", "nombre": "..." }
```

### Citas
```
POST /api/citas/crear
├─ Body: { "cliente_nombre", "cliente_email", "cliente_telefono", "dia", "hora", "servicio", "metodoPago", "precio" }
└─ Response: { "status": "success", "cita_id": "..." }

GET /api/citas/listar/todas
├─ Params: (none)
└─ Response: { "status": "success", "citas": [...] }

GET /api/citas/{cita_id}
├─ Params: cita_id
└─ Response: { "status": "success", "cita": {...} }

GET /api/citas/horarios-ocupados/{dia}
├─ Params: dia (YYYY-MM-DD)
└─ Response: { "status": "success", "horas_ocupadas": [...] }

PUT /api/citas/{cita_id}/completada
├─ Body: (empty)
└─ Response: { "status": "success", "mensaje": "..." }

PUT /api/citas/{cita_id}/cancelar
├─ Body: { "motivo": "..." }
└─ Response: { "status": "success", "mensaje": "..." }

PUT /api/citas/{cita_id}/reagendar
├─ Body: { "nueva_fecha": "YYYY-MM-DD", "nueva_hora": "HH:MM", "motivo": "..." }
└─ Response: { "status": "success", "mensaje": "..." }
```

---

## <a name="flujos"></a>
# 1️⃣1️⃣ FLUJOS DE DATOS

### Flujo 1: Crear Cita (Cliente)
```
1. Cliente llena formulario en reserva.html
2. JS valida datos
3. POST /api/citas/crear
4. Backend crea documento en MongoDB
5. EmailService envía confirmación al cliente
6. EmailService notifica al barbero
7. Response con cita_id
8. Redirigir a cita.html?id=...
```

### Flujo 2: Login Barbero
```
1. Barbero ingresa email/password en dashboard.html
2. JS valida
3. POST /api/auth/login
4. Backend valida contra MongoDB
5. Genera JWT token
6. Response con token
7. JS guarda token en localStorage
8. JS llama a GET /api/citas/listar/todas
9. Renderizar citas en dashboard
```

### Flujo 3: Cancelar Cita
```
1. Barbero abre modal cancelación
2. Ingresa motivo
3. JS valida
4. PUT /api/citas/{id}/cancelar { motivo: "..." }
5. Backend actualiza estado = 'cancelada'
6. EmailService.enviar_cancelacion()
7. Email llega al cliente con motivo
8. Response success
9. JS recarga citas
```

### Flujo 4: Reagendar Cita
```
1. Barbero abre modal reagendamiento
2. Selecciona nueva fecha
3. JS consulta GET /api/citas/horarios-ocupados/{fecha}
4. Renderiza horas disponibles
5. Selecciona nueva hora + motivo
6. PUT /api/citas/{id}/reagendar { nueva_fecha, nueva_hora, motivo }
7. Backend actualiza cita
8. EmailService.enviar_reagendamiento()
9. Email al cliente con ambas fechas
10. Response success
11. JS recarga citas
```

---

## <a name="deploy"></a>
# 1️⃣2️⃣ DEPLOY

### Deploy en Render (Actual)
```
1. GitHub: rosbe6/Golden-Shark-Barber
2. Render conectado a GitHub
3. URL: https://golden-shark-barber.onrender.com
4. Auto-deploy en cada push a main
5. Build: pip install -r requirements.txt
6. Start: python backend/app.py
7. Nota: Render FREE duerme tras 15 min
```

### Variables de Entorno en Render
```
FLASK_ENV=production
MONGO_URI=...
SECRET_KEY=...
EMAIL_FROM=...
EMAIL_PASSWORD=...
```

### Deploy Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear .env
cp .env.example .env

# Ejecutar
python backend/app.py

# O con ngrok para compartir
ngrok http 5000
```

---

## <a name="pendiente"></a>
# 1️⃣3️⃣ PENDIENTE

🔴 **No implementado:**
1. Windows Server RDP + IIS
2. Google Calendar integration (código existe, no testeado)
3. Recordatorio automático 24h antes
4. SMS notifications
5. Admin panel
6. Analytics

✅ **Completado:**
- [x] Landing page con carrusel
- [x] Dashboard barbero
- [x] CRUD citas
- [x] Emails (confirmación, cancelación, reagendamiento)
- [x] Filtros y stats
- [x] Responsive design
- [x] Login/Logout
- [x] API completa

---

**FIN DE DOCUMENTACIÓN** 📚

Esta doc contiene ABSOLUTAMENTE TODO el trabajo desde cero hasta hoy.