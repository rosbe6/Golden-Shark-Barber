const API_URL = 'https://goldenbarbershop.online/api';

let allCitas = [];
let selectedCita = null;
let barberoToken = null;
let barberoName = null;
let barberoFilterSeleccionado = '';  

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

    // Modal buttons
    document.getElementById('btnMarcaCompletada').addEventListener('click', () => {
        if (selectedCita && selectedCita._id) {
            markComplete(selectedCita._id);
        }
    });
    document.getElementById('btnCancelarCita').addEventListener('click', () => openCancelModal());
    document.getElementById('btnReagendar').addEventListener('click', () => openRescheduleModal());
    document.getElementById('btnConfirmCancel').addEventListener('click', confirmCancel);
    document.getElementById('btnConfirmReschedule').addEventListener('click', confirmReschedule);
    document.getElementById('inputNewDate').addEventListener('change', loadTimesForDate); // ✅ FIX: línea que faltaba
    
    document.getElementById('btnPrevWeeks').addEventListener('click', () => {
        if (currentDayPage > 0) {
            currentDayPage--;
            renderDayPage();
        }
    });


    document.getElementById('btnNextWeeks').addEventListener('click', () => {
        const totalPages = Math.ceil(diasActuales.length / DAYS_PER_PAGE);
        if (currentDayPage < totalPages - 1) {
            currentDayPage++;
            renderDayPage();
        }
    });
}

// ==================== TABS ====================

function switchTab(tab) {
    // Ocultar todo
    document.getElementById('seccionCitas').style.display = 'none';
    document.getElementById('seccionBarberos').style.display = 'none';
    
    // Desactivar botones
    document.getElementById('tabCitas').style.background = '#6c757d';
    document.getElementById('tabBarberos').style.background = '#6c757d';
    
    // Mostrar seleccionado
    if (tab === 'citas') {
        document.getElementById('seccionCitas').style.display = 'block';
        document.getElementById('tabCitas').style.background = '#007bff';
    } else {
        document.getElementById('seccionBarberos').style.display = 'block';
        document.getElementById('tabBarberos').style.background = '#007bff';
    }
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
    // ✅ Limpiar TODO el localStorage
    localStorage.removeItem('barber_token');
    localStorage.removeItem('barber_name');
    localStorage.clear();  // Limpiar TODO
    
    barberoToken = null;
    barberoName = null;
    
    // Mostrar login
    showLogin();
    
    // Limpiar formulario
    document.getElementById('inputEmail').value = '';
    document.getElementById('inputPassword').value = '';
    document.getElementById('errorLogin').classList.add('hidden');
}

function showLogin() {
    document.getElementById('screenLogin').classList.remove('hidden');
    document.getElementById('screenDashboard').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('screenLogin').classList.add('hidden');
    document.getElementById('screenDashboard').classList.remove('hidden');
    document.getElementById('textNombre').textContent = barberoName || 'Barber';
    document.getElementById('tabBarberos').style.display = 'none';

    // ✅ Tipo filter SIEMPRE visible (fuera del fetch)
    document.getElementById('tipoFilterSection').style.display = 'block';
    document.getElementById('selectTipoFilter').addEventListener('change', filterCitasByTipo);

    fetch(`${API_URL}/auth/perfil`, {
        headers: { 'Authorization': `Bearer ${barberoToken}` }
    })
    .then(r => r.json())
    .then(data => {
        if (data && data.es_admin) {
            document.getElementById('tabBarberos').style.display = 'block';
            cargarBarberosAdmin();

            fetch(`${API_URL}/auth/barberos`, {
                headers: { 'Authorization': `Bearer ${barberoToken}` }
            })
            .then(r => r.json())
            .then(bData => {
                if (bData.status === 'success') {
                    const select = document.getElementById('selectBarberoFilter');
                    document.getElementById('barberoFilterSection').style.display = 'block';

                    bData.barberos.forEach(b => {
                        const option = document.createElement('option');
                        option.value = b._id;
                        option.textContent = b.nombre;
                        select.appendChild(option);
                    });

                    select.addEventListener('change', filterCitasByBarbero);
                }
            });
        }
    })
    .catch(e => {
        console.error('Error verificando admin:', e);
        document.getElementById('tabBarberos').style.display = 'none';
    });

    loadCitas();
}

function filterCitasByBarbero() {
    const barberoFilter = document.getElementById('selectBarberoFilter').value;
    barberoFilterSeleccionado = barberoFilter; // ← Guardar selección
    
    // Aplicar el filtro activo (all, today, week, completed)
    const activeTab = document.querySelector('.filter-tab.active');
    const filterType = activeTab ? activeTab.dataset.filter : 'all';
    
    filterCitas(filterType); // ← Aplicar filtro con el barbero seleccionado
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
            updateStats();

            const activeTab = document.querySelector('.filter-tab.active');
            const filterType = activeTab ? activeTab.dataset.filter : 'all';
            filterCitas(filterType);
        } else {
            console.error('Error: ' + data.mensaje);
        }
    } catch (error) {
        console.error('Error loadCitas:', error);
    } finally {
        showLoading(false);
    }
}

function updateStats() {
    const today = new Date();
    const hoyString = today.getFullYear() + '-' + 
        String(today.getMonth() + 1).padStart(2, '0') + '-' + 
        String(today.getDate()).padStart(2, '0');

    const citasToday = allCitas.filter(c => c.dia === hoyString && c.estado === 'confirmada').length;
    const citasPending = allCitas.filter(c => c.estado === 'confirmada').length;
    const citasCompleted = allCitas.filter(c => c.estado === 'completada').length;

    document.getElementById('statToday').textContent = citasToday;
    document.getElementById('statPending').textContent = citasPending;
    document.getElementById('statCompleted').textContent = citasCompleted;
    document.getElementById('statTotal').textContent = allCitas.length;
}

function getMonday(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const dow = d.getDay();
    const diff = dow === 0 ? -6 : 1 - dow;
    d.setDate(d.getDate() + diff);
    d.setHours(0, 0, 0, 0);
    return d;
}

function dayLabel(fechaISO) {
    // 2026-08-24 -> Monday 24/2026
    const [year, month, day] = fechaISO.split('-').map(Number);
    const fecha = new Date(year, month - 1, day);
    const diasSemana = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return `${diasSemana[fecha.getDay()]} ${day}/${year}`;
}


function getSaturday(monday) {
    const sat = new Date(monday);
    sat.setDate(monday.getDate() + 5);
    return sat;
}

function formatShort(d) {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function formatearFecha(fechaISO) {
    // 2026-08-20 -> Thursday 20, August 2026
    const [year, month, day] = fechaISO.split('-').map(Number);
    const fecha = new Date(year, month - 1, day);

    const diasSemana = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const meses = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'];

    return `${diasSemana[fecha.getDay()]} ${day}, ${meses[month - 1]} ${year}`;
}

function formatearHora(horaISO) {
    // 14:00 -> 2:00 PM
    const [horas, minutos] = horaISO.split(':').map(Number);
    const periodo = horas >= 12 ? 'PM' : 'AM';
    let horas12 = horas % 12;
    if (horas12 === 0) horas12 = 12;
    return `${horas12}:${String(minutos).padStart(2, '0')} ${periodo}`;
}

let currentDayPage = 0;
const DAYS_PER_PAGE = 7;
let diasActuales = [];

function renderCitas(citas, invertirOrden = false) {
    const box = document.getElementById('citasBox');
    const empty = document.getElementById('emptyBox');
    const pagination = document.getElementById('weekPagination');

    if (citas.length === 0) {
        box.innerHTML = '';
        box.classList.add('hidden');
        pagination.classList.add('hidden');
        empty.classList.remove('hidden');
        return;
    }

    box.classList.remove('hidden');
    empty.classList.add('hidden');

    const sorted = [...citas].sort((a, b) => {
        let cmp;
        if (a.dia !== b.dia) cmp = a.dia.localeCompare(b.dia);
        else cmp = a.hora.localeCompare(b.hora);
        return invertirOrden ? -cmp : cmp;
    });

    // Agrupar por DÍA
    const grupos = {};
    sorted.forEach(c => {
        if (!grupos[c.dia]) grupos[c.dia] = { dia: c.dia, citas: [] };
        grupos[c.dia].citas.push(c);
    });

    let diasOrdenados = Object.values(grupos).sort((a, b) => a.dia.localeCompare(b.dia));
    if (invertirOrden) diasOrdenados = diasOrdenados.reverse();

    diasActuales = diasOrdenados;
    currentDayPage = 0;
    renderDayPage();
}

function renderDayPage() {
    const box = document.getElementById('citasBox');
    const pagination = document.getElementById('weekPagination');
    const label = document.getElementById('weekPageLabel');
    const btnPrev = document.getElementById('btnPrevWeeks');
    const btnNext = document.getElementById('btnNextWeeks');

    const totalPages = Math.ceil(diasActuales.length / DAYS_PER_PAGE);
    const start = currentDayPage * DAYS_PER_PAGE;
    const diasVisibles = diasActuales.slice(start, start + DAYS_PER_PAGE);

    const header = `
        <div class="tabla-header">
            <div>Name</div>
            <div>Time</div>
            <div>Service</div>
            <div style="text-align: right;">Status</div>
        </div>`;

    box.innerHTML = header + diasVisibles.map(grupo => `
        <div class="week-header">${dayLabel(grupo.dia)}</div>
        ${grupo.citas.map(c => {
            let badgeClass = 'badge-pending';
            let badgeText = 'Pending';
            if (c.estado === 'completada') { badgeClass = 'badge-completed'; badgeText = 'Completed'; }
            else if (c.estado === 'cancelada') { badgeClass = 'badge-cancelled'; badgeText = 'Cancelled'; }

            return `
                <div class="fila-cita" onclick="openDetailsModal('${c._id}')">
                    <div class="col-name">${c.cliente_nombre}</div>
                    <div class="col-time">${formatearHora(c.hora)}</div>
                    <div class="col-service">${c.servicio}</div>
                    <div class="badge ${badgeClass}">${badgeText}</div>
                </div>`;
        }).join('')}
    `).join('');

    if (totalPages <= 1) {
        pagination.classList.add('hidden');
    } else {
        pagination.classList.remove('hidden');
        label.textContent = `Page ${currentDayPage + 1} of ${totalPages}`;
        btnPrev.disabled = currentDayPage === 0;
        btnNext.disabled = currentDayPage >= totalPages - 1;
    }
}

function filterCitas(filter) {
    const today = new Date();
    const hoyString = today.getFullYear() + '-' + 
        String(today.getMonth() + 1).padStart(2, '0') + '-' + 
        String(today.getDate()).padStart(2, '0');

    let filtered = allCitas;

    if (barberoFilterSeleccionado) {
        filtered = filtered.filter(c => c.barbero_id === barberoFilterSeleccionado);
    }

    const tipoFilter = document.getElementById('selectTipoFilter');
    if (tipoFilter && tipoFilter.value) {
        filtered = filtered.filter(c => c.tipo_servicio === tipoFilter.value);
    }

    let invertir = false;

    if (filter === 'today') {
        filtered = filtered.filter(c => c.dia === hoyString && c.estado === 'confirmada');
    } else if (filter === 'past') {
        // Todo lo anterior a hoy, sin importar estado — más reciente primero
        filtered = filtered.filter(c => c.dia < hoyString);
        invertir = true;
    } else if (filter === 'completed') {
        filtered = filtered.filter(c => c.estado === 'completada');
        invertir = true;
    } else if (filter === 'cancelled') {
        filtered = filtered.filter(c => c.estado === 'cancelada');
        invertir = true;
    } else {
        // All: solo pendientes de hoy en adelante
        filtered = filtered.filter(c => c.estado === 'confirmada' && c.dia >= hoyString);
    }

    renderCitas(filtered, invertir);
}
// ==================== MODAL: DETAILS ====================

function openDetailsModal(citaId) {
    selectedCita = allCitas.find(c => c._id === citaId);

    if (!selectedCita) return;

    document.getElementById('detClient').textContent = selectedCita.cliente_nombre;
    document.getElementById('detEmail').textContent = selectedCita.cliente_email;
    document.getElementById('detPhone').textContent = selectedCita.cliente_telefono;
    document.getElementById('detDate').textContent = formatearFecha(selectedCita.dia);
    document.getElementById('detTime').textContent = formatearHora(selectedCita.hora);
    document.getElementById('detService').textContent = selectedCita.servicio;
    document.getElementById('detPrice').textContent = `$${selectedCita.precio}`;
    document.getElementById('detNotes').textContent = selectedCita.instrucciones || 'None';
    document.getElementById('detPayment').textContent = selectedCita.metodoPago === 'cash' ? 'Cash' : 'Card';
    document.getElementById('detBarber').textContent = selectedCita.barbero_nombre || '-';
    let statusText = 'Pending';
    if (selectedCita.estado === 'completada') statusText = 'Completed';
    else if (selectedCita.estado === 'cancelada') statusText = 'Cancelled';
    document.getElementById('detStatus').textContent = statusText;

    const isCompletedOrCancelled = selectedCita.estado === 'completada' || selectedCita.estado === 'cancelada';
    document.getElementById('btnMarcaCompletada').disabled = isCompletedOrCancelled;
    document.getElementById('btnCancelarCita').disabled = isCompletedOrCancelled;
    document.getElementById('btnReagendar').disabled = isCompletedOrCancelled;

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

    if (selectedCita) {
        document.getElementById('cancelCurrentInfo').innerHTML = 
            `Cancelling: <strong>${selectedCita.cliente_nombre} — ${formatearFecha(selectedCita.dia)} at ${formatearHora(selectedCita.hora)}</strong>`;
    }
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
    document.getElementById('selectNewTime').innerHTML = '<option value="">Select a date first</option>';
    document.getElementById('inputRescheduleReason').value = '';

    if (selectedCita) {
        document.getElementById('rescheduleCurrentInfo').innerHTML = 
            `Currently: <strong>${formatearFecha(selectedCita.dia)} at ${formatearHora(selectedCita.hora)}</strong>`;
    }
}

function closeRescheduleModal() {
    document.getElementById('modalReschedule').classList.add('hidden');
}

async function loadTimesForDate() {
    const date = document.getElementById('inputNewDate').value;
    if (!date || !selectedCita) return;

    try {
        const response = await fetch(`${API_URL}/citas/horarios-ocupados/${date}?barbero_id=${selectedCita.barbero_id}`);
        const data = await response.json();

        const FECHA_CORTE_45 = new Date('2026-08-24T00:00:00');
        const FECHA_CORTE_SABADO = new Date('2026-09-01T00:00:00');
        const fechaSeleccionada = new Date(date + 'T00:00:00');
        const esSabado = fechaSeleccionada.getDay() === 6;

        let allTimes;
        if (fechaSeleccionada >= FECHA_CORTE_SABADO && esSabado) {
            allTimes = ['09:45', '10:30', '11:15', '12:00', '12:45', '13:30', '14:15'];
        } else if (fechaSeleccionada >= FECHA_CORTE_45) {
            allTimes = ['09:45', '10:30', '11:15', '12:00', '12:45', '13:30', '14:15', '15:00', '15:45', '16:30'];
        } else {
            allTimes = ['10:00', '10:40', '11:20', '12:00', '12:40', '13:20', '14:00', '14:40', '15:20', '16:00', '16:40'];
        }

        const occupied = data.horas_ocupadas || [];
        const available = allTimes.filter(t => !occupied.includes(t));

        const select = document.getElementById('selectNewTime');
        if (available.length === 0) {
            select.innerHTML = '<option value="">No times available this day</option>';
            return;
        }
        select.innerHTML = '<option value="">Select time...</option>' + 
            available.map(t => `<option value="${t}">${formatearHora(t)}</option>`).join('');
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


function cargarBarberosAdmin() {
    fetch(`${API_URL}/auth/perfil`, {
        headers: { 'Authorization': `Bearer ${barberoToken}` }
    })
    .then(r => r.json())
    .then(perfilData => {
        fetch(`${API_URL}/auth/barberos`, {
            headers: { 'Authorization': `Bearer ${barberoToken}` }
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                barberosCache = data.barberos;
                renderBarberosAdmin(data.barberos, perfilData.barbero_id);
            }
        })
        .catch(e => console.error(e));
    })
    .catch(e => console.error(e));
}

function openEditBarberoModal(barberoId) {
    const barbero = barberosCache.find(b => b._id === barberoId);
    if (!barbero) return;

    document.getElementById('editBarberoId').value = barbero._id;
    document.getElementById('editNombre').value = barbero.nombre;
    document.getElementById('editEmail').value = barbero.email;
    document.getElementById('editTelefono').value = barbero.telefono || '';
    document.getElementById('editTipo').value = barbero.tipo || 'barber';
    document.getElementById('editPassword').value = '';
    document.getElementById('editPasswordConfirm').value = '';
    document.getElementById('editInputFoto').value = '';

    const fotoImg = document.getElementById('editFotoImg');
    const fotoPlaceholder = document.getElementById('editFotoPlaceholder');
    if (barbero.foto) {
        fotoImg.src = barbero.foto;
        fotoImg.style.display = 'block';
        fotoPlaceholder.style.display = 'none';
    } else {
        fotoImg.style.display = 'none';
        fotoPlaceholder.style.display = 'block';
    }

    document.getElementById('modalEditBarbero').classList.remove('hidden');
}

function closeEditBarberoModal() {
    document.getElementById('modalEditBarbero').classList.add('hidden');
}



function renderBarberosAdmin(barberos, barberoActualId) {
    const list = document.getElementById('barberosList');
    list.innerHTML = barberos.map(b => `
        <div class="barbero-card">
            ${!b.es_admin && b._id !== barberoActualId ? `<button class="barbero-edit-btn" onclick="openEditBarberoModal('${b._id}')">✏️</button>` : (b.es_admin ? `<button class="barbero-edit-btn" onclick="openEditBarberoModal('${b._id}')">✏️</button>` : '')}
            <div class="barbero-card-foto">
                ${b.foto ? `<img src="${b.foto}" alt="${b.nombre}">` : '👤'}
            </div>
            <div style="font-weight: bold; font-size: 15px;">${b.nombre}</div>
            <div style="color: #666; font-size: 12px;">${b.email}</div>
            <div style="color: #666; font-size: 12px;">📞 ${b.telefono || 'No phone'}</div>
            <div style="color: #007bff; font-size: 11px; margin-top: 4px;">
                ${b.tipo === 'skincare' ? '💆 Skincare Specialist' : '💈 Barber'}
            </div>
            ${b.es_admin ? '<div style="color: #28a745; font-weight: bold; margin-top: 6px; font-size: 12px;">👑 Owner</div>' : ''}
            ${(!b.es_admin && b._id !== barberoActualId) ? `<button onclick="confirmarEliminarBarbero('${b._id}', '${b.nombre}')" style="background: #dc3545; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; margin-top: 10px; font-size: 12px;">Delete</button>` : ''}
        </div>
    `).join('');
}



async function agregarBarberoAdmin(e) {
    e.preventDefault();
    
    const nombre = document.getElementById('inputNombreBarbero').value;
    const email = document.getElementById('inputEmailBarbero').value;
    const telefono = document.getElementById('inputTelefonoBarbero').value;
    const contraseña = document.getElementById('inputPasswordBarbero').value;
    const contraseñaConfirm = document.getElementById('inputPasswordBarberoConfirm').value;
    const tipo = document.getElementById('inputTipoBarbero').value;

    if (contraseña !== contraseñaConfirm) {
        alert('❌ Passwords do not match');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_URL}/auth/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, email, telefono, contraseña, tipo })
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


let barberosCache = [];

function previewEditFoto(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        const fotoImg = document.getElementById('editFotoImg');
        fotoImg.src = e.target.result;
        fotoImg.style.display = 'block';
        document.getElementById('editFotoPlaceholder').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

async function guardarEdicionBarbero(e) {
    e.preventDefault();

    const barberoId = document.getElementById('editBarberoId').value;
    const password = document.getElementById('editPassword').value;
    const passwordConfirm = document.getElementById('editPasswordConfirm').value;

    if (password && password !== passwordConfirm) {
        alert('❌ Passwords do not match');
        return;
    }

    const formData = new FormData();
    formData.append('nombre', document.getElementById('editNombre').value);
    formData.append('email', document.getElementById('editEmail').value);
    formData.append('telefono', document.getElementById('editTelefono').value);
    formData.append('tipo', document.getElementById('editTipo').value);
    if (password) formData.append('contraseña', password);

    const fotoFile = document.getElementById('editInputFoto').files[0];
    if (fotoFile) formData.append('foto', fotoFile);

    try {
        showLoading(true);

        const response = await fetch(`${API_URL}/auth/barberos/${barberoId}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${barberoToken}` },
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('✅ Barber updated successfully!');
            closeEditBarberoModal();
            cargarBarberosAdmin();
        } else {
            alert('❌ Error: ' + data.mensaje);
        }
    } catch (error) {
        alert('❌ Error updating barber');
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


function filterCitasByTipo() {
    const tipoFilter = document.getElementById('selectTipoFilter').value;
    const activeTab = document.querySelector('.filter-tab.active');
    const filterType = activeTab ? activeTab.dataset.filter : 'all';
    filterCitas(filterType);
}