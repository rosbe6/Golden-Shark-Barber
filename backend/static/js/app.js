const API_URL = 'https://constant-harmonize-situated.ngrok-free.dev/api';
let diasDisponibles = [];
let diaSeleccionado = null;
let horaSeleccionada = null;
let mesActualMostrado = new Date();

document.addEventListener('DOMContentLoaded', function() {
    cargarDiasDisponibles();
    document.getElementById('appointmentForm').addEventListener('submit', crearCita);
});

function cargarDiasDisponibles() {
    fetch(`${API_URL}/citas/disponibles`)
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
        const fechaString = fecha.toISOString().split('T')[0];
        
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

function cargarHorarios(dia) {
    fetch(`${API_URL}/citas/disponibles`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                fetch(`${API_URL}/citas/horarios-ocupados/${dia}`)
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

function crearCita(event) {
    event.preventDefault();
    
    const citaData = {
        cliente_nombre: document.getElementById('clienteNombre').value,
        cliente_email: document.getElementById('clienteEmail').value,
        cliente_telefono: document.getElementById('clienteTelefono').value,
        dia: document.getElementById('dia').value,
        hora: document.getElementById('hora').value,
        servicio: document.getElementById('servicio').value,
        metodoPago: document.getElementById('metodoPago').value,
        precio: document.getElementById('metodoPago').value === 'cash' ? 45 : 50,
        instrucciones: document.getElementById('instrucciones').value
    };
    
    if (!citaData.cliente_nombre || !citaData.cliente_email || !citaData.cliente_telefono || 
        !citaData.dia || !citaData.hora || !citaData.servicio || !citaData.metodoPago) {
        mostrarError('Please fill in all required fields');
        return;
    }
    
    fetch(`${API_URL}/citas/crear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(citaData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = `cita.html?id=${data.cita_id}`;
        } else {
            mostrarError(data.mensaje);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarError('Error creating appointment');
    });
}

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