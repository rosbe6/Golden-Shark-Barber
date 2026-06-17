const API = 'https://constant-harmonize-situated.ngrok-free.dev/api';
let token = localStorage.getItem('token');
let tabActual = 'hoy';

window.addEventListener('DOMContentLoaded', iniciar);

function iniciar() {
    if (token) {
        mostrarDashboard();
        cargarCitas();
    } else {
        mostrarLogin();
        document.getElementById('form-login').addEventListener('submit', hacerLogin);
    }
}

function mostrarLogin() {
    document.getElementById('pantalla-login').classList.remove('hidden');
    document.getElementById('pantalla-dashboard').classList.add('hidden');
}

function mostrarDashboard() {
    document.getElementById('pantalla-login').classList.add('hidden');
    document.getElementById('pantalla-dashboard').classList.remove('hidden');
}

function hacerLogin(e) {
    e.preventDefault();

    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;

    fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, contraseña: password })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            token = data.token;
            localStorage.setItem('token', token);
            mostrarDashboard();
            cargarCitas();
        } else {
            mostrarError(data.mensaje);
        }
    })
    .catch(err => {
        console.error(err);
        mostrarError('Error en login');
    });
}

function mostrarError(msg) {
    const errorDiv = document.getElementById('error-login');
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
}

function cargarCitas() {
    const endpoint = tabActual === 'hoy' ? '/dashboard/citas/hoy' : '/dashboard/citas';

    fetch(`${API}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            renderizarCitas(data.citas);
        }
    })
    .catch(err => console.error(err));
}

function renderizarCitas(citas) {
    const contenedor = document.getElementById('contenido-dashboard');

    if (!citas || citas.length === 0) {
        contenedor.innerHTML = '<p class="empty-message">No appointments</p>';
        return;
    }

    let html = '';
    citas.forEach(cita => {
        const estaBloqueada = cita.estado === 'completada' || cita.estado === 'cancelada';
        
        html += `
            <div class="appointment-card">
                <h3>${cita.cliente_nombre}</h3>
                <p><strong>Service:</strong> ${cita.servicio}</p>
                <p><strong>Date:</strong> ${cita.dia}</p>
                <p><strong>Time:</strong> ${cita.hora}</p>
                <p><strong>Email:</strong> ${cita.cliente_email}</p>
                <p><strong>Phone:</strong> ${cita.cliente_telefono}</p>
                <p><strong>Payment:</strong> ${cita.metodoPago === 'cash' ? 'Cash' : 'Credit Card'}</p>
                <p><strong>Price:</strong> $${cita.precio}</p>
                <p><strong>Status:</strong> <span class="status-${cita.estado}">${cita.estado.toUpperCase()}</span></p>
                ${cita.instrucciones ? `<p><strong>Notes:</strong> ${cita.instrucciones}</p>` : ''}
                
                <div class="appointment-actions">
                    ${cita.estado !== 'completada' && cita.estado !== 'cancelada' ? `<button class="btn-complete" onclick="completar('${cita._id}')">Complete</button>` : ''}
                    ${cita.estado !== 'cancelada' && cita.estado !== 'completada' ? `<button class="btn-cancel" onclick="cancelar('${cita._id}')">Cancel</button>` : ''}
                </div>
            </div>
        `;
    });

    contenedor.innerHTML = html;
}

function verTab(tab) {
    tabActual = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    if (tab === 'hoy') {
        cargarCitasHoy();
    } else if (tab === 'todas') {
        cargarTodasCitas();
    } else if (tab === 'completadas') {
        cargarCitasCompletadas();
    } else if (tab === 'canceladas') {
        cargarCitasCanceladas();
    }
}

function cargarCitasCompletadas() {
    fetch(`${API}/dashboard/citas`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const completadas = data.citas.filter(c => c.estado === 'completada');
            renderizarCitas(completadas);
        }
    })
    .catch(err => console.error(err));
}

function cargarCitasCanceladas() {
    fetch(`${API}/dashboard/citas`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const canceladas = data.citas.filter(c => c.estado === 'cancelada');
            renderizarCitas(canceladas);
        }
    })
    .catch(err => console.error(err));
}

let accionPendiente = null;
let citaIdPendiente = null;

function completar(citaId) {
    citaIdPendiente = citaId;
    accionPendiente = 'completar';
    
    document.getElementById('modal-titulo').textContent = 'Complete Appointment?';
    document.getElementById('modal-mensaje').textContent = 'Mark this appointment as completed?';
    document.getElementById('modal').classList.remove('hidden');
}

function cancelar(citaId) {
    citaIdPendiente = citaId;
    accionPendiente = 'cancelar';
    
    document.getElementById('modal-titulo').textContent = 'Cancel Appointment?';
    document.getElementById('modal-mensaje').textContent = 'This action cannot be undone.';
    document.getElementById('modal').classList.remove('hidden');
}

function cerrarModal() {
    document.getElementById('modal').classList.add('hidden');
    accionPendiente = null;
    citaIdPendiente = null;
}

function confirmarAccion() {
    if (accionPendiente === 'completar') {
        ejecutarCompletar();
    } else if (accionPendiente === 'cancelar') {
        ejecutarCancelar();
    }
    cerrarModal();
}
function ejecutarCompletar() {
    fetch(`${API}/dashboard/citas/${citaIdPendiente}/completar`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            mostrarToast('✓ Appointment completed!', 'success');
            cargarCitas();
        }
    })
    .catch(err => console.error(err));
}

function ejecutarCancelar() {
    fetch(`${API}/citas/${citaIdPendiente}/cancelar`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            mostrarToast('✓ Appointment cancelled!', 'success');
            cargarCitas();
        }
    })
    .catch(err => console.error(err));
}

function mostrarToast(mensaje, tipo) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensaje;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}




function cerrarSesion() {
    localStorage.removeItem('token');
    token = null;
    document.getElementById('form-login').reset();
    document.getElementById('error-login').classList.add('hidden');
    mostrarLogin();
}