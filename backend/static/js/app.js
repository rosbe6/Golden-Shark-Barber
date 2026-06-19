const API_URL = 'https://goldenbarbershop.online/api';

let diasDisponibles = [];
let diaSeleccionado = null;
let horaSeleccionada = null;
let mesActualMostrado = new Date();
let barberoSeleccionado = null;
let allBarberos = [];

document.addEventListener('DOMContentLoaded', function() {
    cargarBarberos();
    document.getElementById('appointmentForm').addEventListener('submit', crearCita);
});

// ==================== BARBEROS ====================

function cargarBarberos() {
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
    fetch(`${API_URL}/citas/disponibles?barbero_id=${barberoSeleccionado}`)
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

function renderizarHorarios(horarios, horariosOcupados) {
    const horariosDiv = document.getElementById('horariosGrid');
    horariosDiv.innerHTML = '';
    
    horarios.forEach(hora => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'horario';
        btn.textContent = hora;
        
        if (horariosOcupados.includes(hora)) {
            // Horario ocupado
            btn.classList.add('ocupado');
            btn.disabled = true;
        } else {
            // Horario disponible
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                seleccionarHora(hora, btn);
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

function crearCita(event) {
    event.preventDefault();
    
    console.log("🔍 [CREAR CITA] barberoSeleccionado:", barberoSeleccionado);
    
    const citaData = {
        cliente_nombre: document.getElementById('clienteNombre').value,
        cliente_email: document.getElementById('clienteEmail').value,
        cliente_telefono: document.getElementById('clienteTelefono').value,
        dia: document.getElementById('dia').value,
        hora: document.getElementById('hora').value,
        servicio: document.getElementById('servicio').value,
        metodoPago: document.getElementById('metodoPago').value,
        precio: document.getElementById('metodoPago').value === 'cash' ? 45 : 50,
        instrucciones: document.getElementById('instrucciones').value,
        barbero_id: barberoSeleccionado
    };
    
    console.log("📤 [CREAR CITA] citaData completo:", citaData);
    console.log("📤 [CREAR CITA] barbero_id específico:", citaData.barbero_id);
    
    if (!citaData.cliente_nombre || !citaData.cliente_email || !citaData.cliente_telefono || 
        !citaData.dia || !citaData.hora || !citaData.servicio || !citaData.metodoPago) {
        mostrarError('Please fill in all required fields');
        console.log("❌ Falta un campo requerido");
        return;
    }
    
    if (!citaData.barbero_id) {
        mostrarError('Please select a barber');
        console.log("❌ No se seleccionó barbero");
        return;
    }
    
    fetch(`${API_URL}/citas/crear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(citaData)
    })
    .then(response => {
        console.log("📥 Response status:", response.status);
        
        // ✅ Manejar error 409 (horario ocupado)
        if (response.status === 409) {
            mostrarError('❌ Ese horario ya fue reservado por otro cliente.\n\nPor favor, selecciona otro horario.');
            horaSeleccionada = null;
            document.getElementById('hora').value = '';
            document.querySelectorAll('.horario.seleccionado').forEach(el => {
                el.classList.remove('seleccionado');
            });
            if (diaSeleccionado) {
                cargarHorarios(diaSeleccionado);
            }
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        
        console.log("📥 Response data:", data);
        
        if (data.status === 'success') {
            console.log("✅ Cita creada:", data.cita_id);
            window.location.href = `cita.html?id=${data.cita_id}`;
        } else {
            console.log("❌ Error:", data.mensaje);
            mostrarError(data.mensaje);
        }
    })
    .catch(error => {
        console.error('❌ [CREAR CITA] Error:', error);
        mostrarError('Error creating appointment');
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
        precioMonto.textContent = '45';
        precioContainer.classList.remove('hidden');
    } else if (metodoPago === 'tarjeta') {
        precioMonto.textContent = '50';
        precioContainer.classList.remove('hidden');
    } else {
        precioContainer.classList.add('hidden');
    }
}