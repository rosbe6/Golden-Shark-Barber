const API_URL = 'https://goldenbarbershop.online/api';
let allCitas = [];
let selectedCita = null;
let barberoToken = null;
let barberoName = null;

// ==================== INIT ====================

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

    // Modal buttons - ✅ ARREGLADO
    document.getElementById('btnMarcaCompletada').addEventListener('click', () => {
        if (selectedCita && selectedCita._id) {
            markComplete(selectedCita._id);
        }
    });
    document.getElementById('btnCancelarCita').addEventListener('click', () => openCancelModal());
    document.getElementById('btnReagendar').addEventListener('click', () => openRescheduleModal());
    document.getElementById('btnConfirmCancel').addEventListener('click', confirmCancel);
    document.getElementById('btnConfirmReschedule').addEventListener('click', confirmReschedule);
    document.getElementById('inputNewDate').addEventListener('change', loadTimesForDate);
}
// ==================== LOGIN ====================

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
    barberoToken = null;
    barberoName = null;
    showLogin();
}

function showLogin() {
    document.getElementById('screenLogin').classList.remove('hidden');
    document.getElementById('screenDashboard').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('screenLogin').classList.add('hidden');
    document.getElementById('screenDashboard').classList.remove('hidden');
    document.getElementById('textNombre').textContent = barberoName || 'Barber';
    
    checkIfAdmin();
}

function showLoginError(msg) {
    const errorDiv = document.getElementById('errorLogin');
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
}

// ==================== CITAS ====================

async function loadCitas() {
    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/dashboard/citas`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${barberoToken}`
            }
        });
        const data = await response.json();

        if (data.status === 'success') {
            allCitas = data.citas || [];
            renderCitas(allCitas);
            updateStats();
        } else {
            alert('Error: ' + data.mensaje);
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

// ==================== MODAL: DETAILS ====================

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

// ==================== MARK COMPLETE ====================

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

// ==================== CANCEL ====================

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
            alert('✅ Appointment cancelled!');
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

// ==================== RESCHEDULE ====================

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
            alert('✅ Appointment rescheduled!');
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

// ==================== UTILITIES ====================

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}


// ==================== ADMIN: GESTIÓN DE BARBEROS ====================

function checkIfAdmin() {
    // Verificar si es Rosbin (admin)
    if (barberoName === 'Rosbin') {
        document.getElementById('adminSection').classList.remove('hidden');
        cargarBarberosAdmin();
    }
}

function cargarBarberosAdmin() {
    fetch(`${API_URL}/auth/barberos`, {
        headers: { 'Authorization': `Bearer ${barberoToken}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            renderBarberosAdmin(data.barberos);
        }
    })
    .catch(e => console.error(e));
}

function renderBarberosAdmin(barberos) {
    const list = document.getElementById('barberosList');
    list.innerHTML = barberos.map(b => `
        <div style="background: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: bold; font-size: 16px;">${b.nombre}</div>
                <div style="color: #666; font-size: 13px;">${b.email}</div>
            </div>
            ${b.nombre !== 'Rosbin' ? `
                <button onclick="confirmarEliminarBarbero('${b._id}', '${b.nombre}')" style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Delete
                </button>
            ` : '<span style="color: #28a745; font-weight: bold;">👑 Owner</span>'}
        </div>
    `).join('');
}

async function agregarBarberoAdmin(e) {
    e.preventDefault();
    
    const nombre = document.getElementById('inputNombreBarbero').value;
    const email = document.getElementById('inputEmailBarbero').value;
    const contraseña = document.getElementById('inputPasswordBarbero').value;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_URL}/auth/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, email, contraseña })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('✅ Barber added successfully!');
            document.getElementById('formAddBarbero').reset();
            cargarBarberosAdmin();
        } else {
            alert('❌ Error: ' + data.mensaje);
        }
    } catch (error) {
        alert('❌ Error adding barber');
    } finally {
        showLoading(false);
    }
}

function confirmarEliminarBarbero(barberoId, nombre) {
    if (confirm(`Are you sure you want to delete ${nombre}?`)) {
        eliminarBarberoAdmin(barberoId);
    }
}

async function eliminarBarberoAdmin(barberoId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_URL}/auth/barberos/${barberoId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${barberoToken}` }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('✅ Barber deleted!');
            cargarBarberosAdmin();
        } else {
            alert('❌ Error: ' + data.mensaje);
        }
    } catch (error) {
        alert('❌ Error deleting barber');
    } finally {
        showLoading(false);
    }
}