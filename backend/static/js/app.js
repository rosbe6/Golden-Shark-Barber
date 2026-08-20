const API_URL = 'https://goldenbarbershop.online/api';

let diasDisponibles = [];
let diaSeleccionado = null;
let horaSeleccionada = null;
let mesActualMostrado = new Date();
let barberoSeleccionado = null;
let allBarberos = [];

document.addEventListener('DOMContentLoaded', function() {
    cargarBarberos();
    verificarSkincareHabilitado();
    document.getElementById('appointmentForm').addEventListener('submit', crearCita);
});

function verificarSkincareHabilitado() {
    fetch(`${API_URL}/citas/config`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && !data.skincare_enabled) {
                const opcionSkincare = document.querySelector('#tipoServicio option[value="skincare"]');
                if (opcionSkincare) {
                    opcionSkincare.remove();
                }
            }
        })
        .catch(error => console.error('Error checking skincare status:', error));
}
// ==================== BARBEROS ====================

function cargarBarberos() {
    // ✅ NO cargar barberos al inicio, esperar que seleccionen tipo
    const selectBarbero = document.getElementById('selectBarbero');
    selectBarbero.innerHTML = '<option value="">Select service type first</option>';
    fetch(`${API_URL}/citas/barberos`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                allBarberos = data.barberos;
                renderBarberos();
                // Seleccionar primer barbero por defecto
                if (allBarberos.length > 0) {
                    seleccionarBarbero(allBarberos[0]._id);
                }
            }
        })
        .catch(error => console.error('Error:', error));
}

function renderBarberos() {
    const selectBarbero = document.getElementById('selectBarbero');
    selectBarbero.innerHTML = allBarberos.map(b => 
        `<option value="${b._id}">${b.nombre}</option>`
    ).join('');
    
    selectBarbero.addEventListener('change', (e) => {
        seleccionarBarbero(e.target.value);
    });
}

function seleccionarBarbero(barberoId) {
    barberoSeleccionado = barberoId;
    document.getElementById('selectBarbero').value = barberoId;
    
    // Recargar días disponibles para este barbero
    cargarDiasDisponibles();
    
    // Limpiar selecciones
    diaSeleccionado = null;
    horaSeleccionada = null;
    document.getElementById('dia').value = '';
    document.getElementById('hora').value = '';
    document.getElementById('horariosGrid').innerHTML = '';
}

// ==================== DÍAS ====================

function cargarDiasDisponibles() {
    fetch(`${API_URL}/citas/disponibles?barbero_id=${barberoSeleccionado}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                diasDisponibles = data.dias;
                mostrarMes(new Date());
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarError('Error loading available dates');
        });
}

function mostrarMes(fecha) {
    mesActualMostrado = new Date(fecha);
    renderizarCalendario();
}

function renderizarCalendario() {
    const año = mesActualMostrado.getFullYear();
    const mes = mesActualMostrado.getMonth();
    
    const meses = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'];
    
    document.getElementById('mesActualLabel').textContent = `${meses[mes]} ${año}`;
    
    const calendarioDiv = document.getElementById('calendario');
    calendarioDiv.innerHTML = '';
    
    // Agregar headers de días de la semana
    const diasSemana = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    diasSemana.forEach(dia => {
        const header = document.createElement('div');
        header.style.fontSize = '11px';
        header.style.fontWeight = '700';
        header.style.color = '#999';
        header.style.textAlign = 'center';
        header.style.padding = '8px 0';
        header.textContent = dia;
        calendarioDiv.appendChild(header);
    });
    
    const primerDia = new Date(año, mes, 1).getDay();
    const ultimoDia = new Date(año, mes + 1, 0).getDate();
    
    // Agregar espacios en blanco para el primer día
    for (let i = 0; i < primerDia; i++) {
        const espacioVacio = document.createElement('div');
        calendarioDiv.appendChild(espacioVacio);
    }
    
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    
    // Agregar días del mes
    for (let dia = 1; dia <= ultimoDia; dia++) {
        const fecha = new Date(año, mes, dia);
        const fechaString = fecha.getFullYear() + '-' +
                           String(fecha.getMonth() + 1).padStart(2, '0') + '-' +
                           String(fecha.getDate()).padStart(2, '0');
        
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'dia';
        btn.textContent = dia;
        
        if (fecha < hoy) {
            // Día pasado - deshabilitado
            btn.classList.add('deshabilitado');
            btn.disabled = true;
        } else if (diasDisponibles.includes(fechaString)) {
            // Día disponible
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                seleccionarDia(fechaString, btn);
            });
        } else {
            // Día no disponible
            btn.classList.add('deshabilitado');
            btn.disabled = true;
        }
        
        calendarioDiv.appendChild(btn);
    }
}

function seleccionarDia(dia, elemento) {
    // Remover selección anterior
    document.querySelectorAll('.dia.seleccionado').forEach(el => {
        el.classList.remove('seleccionado');
    });
    
    // Marcar como seleccionado
    elemento.classList.add('seleccionado');
    diaSeleccionado = dia;
    document.getElementById('dia').value = dia;
    horaSeleccionada = null;
    
    // Cargar horarios para el día seleccionado
    cargarHorarios(dia);
}

// ==================== HORARIOS ====================

function cargarHorarios(dia) {
    fetch(`${API_URL}/citas/disponibles?barbero_id=${barberoSeleccionado}&fecha=${dia}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                fetch(`${API_URL}/citas/horarios-ocupados/${dia}?barbero_id=${barberoSeleccionado}`)
                    .then(response => response.json())
                    .then(dataDia => {
                        const horariosOcupados = dataDia.horas_ocupadas || [];
                        renderizarHorarios(data.horarios, horariosOcupados);
                    });
            }
        })
        .catch(error => console.error('Error:', error));
}


function formatearHora12h(horaISO) {
    const [horas, minutos] = horaISO.split(':').map(Number);
    const periodo = horas >= 12 ? 'PM' : 'AM';
    let horas12 = horas % 12;
    if (horas12 === 0) horas12 = 12;
    return `${horas12}:${String(minutos).padStart(2, '0')} ${periodo}`;
}



function renderizarHorarios(horarios, horariosOcupados) {
    const horariosDiv = document.getElementById('horariosGrid');
    horariosDiv.innerHTML = '';
    
    horarios.forEach(hora => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'horario';
        btn.textContent = formatearHora12h(hora); // ✅ Solo el texto visible cambia
        
        if (horariosOcupados.includes(hora)) {
            btn.classList.add('ocupado');
            btn.disabled = true;
        } else {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                seleccionarHora(hora, btn); // ✅ el valor real (24h) se sigue guardando igual
            });
        }
        
        horariosDiv.appendChild(btn);
    });
}

function seleccionarHora(hora, elemento) {
    // Remover selección anterior
    document.querySelectorAll('.horario.seleccionado').forEach(el => {
        el.classList.remove('seleccionado');
    });
    
    // Marcar como seleccionado
    elemento.classList.add('seleccionado');
    horaSeleccionada = hora;
    document.getElementById('hora').value = hora;
}

function mesAnterior() {
    mesActualMostrado.setMonth(mesActualMostrado.getMonth() - 1);
    renderizarCalendario();
}

function mesSiguiente() {
    mesActualMostrado.setMonth(mesActualMostrado.getMonth() + 1);
    renderizarCalendario();
}

// ==================== CREAR CITA ====================

// ==================== CREAR CITA ====================

function crearCita(event) {
    event.preventDefault();
    
    const submitBtn = document.querySelector('.btn-submit');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-spinner"></span> Booking...';
    
    const tipo = document.getElementById('tipoServicio').value;
    
    let servicio, metodoPago, precio;
    
    if (tipo === 'barber') {
        servicio = document.getElementById('servicio').value;
        metodoPago = document.getElementById('metodoPago').value;
        precio = 50;
    } else if (tipo === 'skincare') {
        const servicioVal = document.getElementById('servicioSkincare').value;
        servicio = servicioVal.split('|')[0];
        precio = parseInt(servicioVal.split('|')[1]);
        metodoPago = document.getElementById('metodoPagoSkincare').value;
    }
    
    const citaData = {
        cliente_nombre: document.getElementById('clienteNombre').value,
        cliente_email: document.getElementById('clienteEmail').value,
        cliente_telefono: document.getElementById('clienteTelefono').value,
        dia: document.getElementById('dia').value,
        hora: document.getElementById('hora').value,
        servicio: servicio,
        metodoPago: metodoPago,
        precio: precio,
        instrucciones: document.getElementById('instrucciones').value,
        barbero_id: barberoSeleccionado,
        tipo_servicio: tipo
    };
    
    // Validaciones
    if (!citaData.cliente_nombre || !citaData.cliente_email || !citaData.cliente_telefono || 
        !citaData.dia || !citaData.hora || !citaData.servicio || !citaData.metodoPago || !tipo) {
        mostrarError('Please fill in all required fields');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Confirm Appointment';
        return;
    }
    
    if (!citaData.barbero_id) {
        mostrarError('Please select a barber');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Confirm Appointment';
        return;
    }
    
    fetch(`${API_URL}/citas/crear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(citaData)
    })
    .then(response => {
        if (response.status === 409) {
            mostrarError('❌ That time slot is already booked. Please select another time.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Confirm Appointment';
            horaSeleccionada = null;
            document.getElementById('hora').value = '';
            document.querySelectorAll('.horario.seleccionado').forEach(el => el.classList.remove('seleccionado'));
            if (diaSeleccionado) cargarHorarios(diaSeleccionado);
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.status === 'success') {
            window.location.href = `cita.html?id=${data.cita_id}`;
        } else {
            mostrarError(data.mensaje);
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Confirm Appointment';
        }
    })
    .catch(error => {
        mostrarError('Error creating appointment');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Confirm Appointment';
    });
}

// ==================== UTILIDADES ====================

function mostrarError(mensaje) {
    document.getElementById('errorMessage').classList.remove('hidden');
    document.getElementById('errorText').textContent = mensaje;
}

function actualizarPrecio() {
    const metodoPago = document.getElementById('metodoPago').value;
    const precioContainer = document.getElementById('precio-container');
    const precioMonto = document.getElementById('precio-monto');

    if (metodoPago === 'cash') {
        precioMonto.textContent = '50';
        precioContainer.classList.remove('hidden');
    } else if (metodoPago === 'tarjeta') {
        precioMonto.textContent = '50';
        precioContainer.classList.remove('hidden');
    } else {
        precioContainer.classList.add('hidden');
    }
}



// ==================== TIPO SERVICIO ====================

function cambiarTipoServicio() {
    const tipo = document.getElementById('tipoServicio').value;
    
    // Ocultar todo
    document.getElementById('servicios-barber').classList.add('hidden');
    document.getElementById('servicios-skincare').classList.add('hidden');
    document.getElementById('precio-container').classList.add('hidden');
    
    // Resetear
    diaSeleccionado = null;
    horaSeleccionada = null;
    document.getElementById('dia').value = '';
    document.getElementById('hora').value = '';
    document.getElementById('horariosGrid').innerHTML = '';
    
    if (tipo === 'barber') {
        document.getElementById('servicios-barber').classList.remove('hidden');
        // ✅ Cambiar titulo
        document.getElementById('titulo-especialista').textContent = 'Select Your Barber';
        document.getElementById('label-especialista').textContent = 'Barber *';
        cargarBarberosPorTipo('barber');
        
    } else if (tipo === 'skincare') {
        document.getElementById('servicios-skincare').classList.remove('hidden');
        // ✅ Cambiar titulo
        document.getElementById('titulo-especialista').textContent = 'Your Skincare Specialist';
        document.getElementById('label-especialista').textContent = 'Specialist *';
        cargarBarberosPorTipo('skincare');
    }
}

function cargarBarberosPorTipo(tipo) {
    fetch(`${API_URL}/citas/barberos?tipo=${tipo}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                allBarberos = data.barberos;
                renderBarberos();
                if (allBarberos.length > 0) {
                    seleccionarBarbero(allBarberos[0]._id);
                }
            }
        })
        .catch(error => console.error('Error:', error));
}

function actualizarPrecioSkincare() {
    const servicioVal = document.getElementById('servicioSkincare').value;
    const metodoPago = document.getElementById('metodoPagoSkincare').value;
    
    if (!servicioVal || !metodoPago) {
        document.getElementById('precio-container').classList.add('hidden');
        return;
    }
    
    // Formato: "nombre|precio"
    const precio = servicioVal.split('|')[1];
    document.getElementById('precio-monto').textContent = `$${precio}`;
    document.getElementById('precio-container').classList.remove('hidden');
}