const API_URL = 'https://goldenbarbershop.online/api';

document.addEventListener('DOMContentLoaded', function() {
    const params = new URLSearchParams(window.location.search);
    const citaId = params.get('id');
    
    console.log('Cita ID:', citaId);
    
    if (!citaId) {
        mostrarNoEncontrada();
        return;
    }
    
    cargarCita(citaId);
});

function cargarCita(citaId) {
    console.log('Cargando cita:', citaId);
    
    fetch(`${API_URL}/citas/${citaId}`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Data recibida:', data);
            
            if (data.status === 'success' && data.cita) {
                mostrarCita(data.cita);
            } else {
                mostrarNoEncontrada();
            }
        })
        .catch(error => {
            console.error('Error al cargar cita:', error);
            mostrarNoEncontrada();
        });
}

function mostrarCita(cita) {
    console.log('Mostrando cita:', cita);
    
    // Ocultar loading
    document.getElementById('cargando').classList.add('hidden');
    
    // Mostrar contenido
    document.getElementById('cita-encontrada').classList.remove('hidden');
    
    // Llenar datos
    document.getElementById('det-servicio').textContent = cita.servicio || '-';
    
    // Formato de fecha
    const fecha = new Date(cita.dia);
    const fechaFormato = fecha.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    document.getElementById('det-fecha').textContent = fechaFormato;
    
    document.getElementById('det-hora').textContent = cita.hora || '-';
    
    // Estado
    let estado = cita.estado || 'confirmed';
    if (estado === 'cancelada' || estado === 'cancelled') {
        estado = 'Cancelled';
    } else if (estado === 'completada' || estado === 'completed') {
        estado = 'Completed';
    } else {
        estado = 'Confirmed';
    }
    document.getElementById('det-estado').textContent = estado;
    
    // Método de pago
    const metodoPago = cita.metodoPago === 'cash' ? 'Cash' : 'Credit Card';
    document.getElementById('det-metodoPago').textContent = metodoPago;
    
    // Precio
    document.getElementById('det-precio-monto').textContent = cita.precio || '0';
    
    // Datos personales
    document.getElementById('det-nombre').textContent = cita.cliente_nombre || '-';
    document.getElementById('det-email').textContent = cita.cliente_email || '-';
    document.getElementById('det-telefono').textContent = cita.cliente_telefono || '-';
    
    // Instrucciones (si existen)
    if (cita.instrucciones && cita.instrucciones.trim() !== '') {
        document.getElementById('det-instrucciones-container').classList.remove('hidden');
        document.getElementById('det-instrucciones').textContent = cita.instrucciones;
    }
    
    // Si está cancelada, desactivar botón de cancelar
    if (estado === 'Cancelled') {
        const btnCancelar = document.getElementById('btn-cancelar');
        btnCancelar.disabled = true;
        btnCancelar.style.opacity = '0.5';
        btnCancelar.style.cursor = 'not-allowed';
    }
    
    // Guardar ID para cancelación
    window.citaIdActual = cita._id || cita.id;
}

function mostrarNoEncontrada() {
    console.log('Cita no encontrada');
    document.getElementById('cargando').classList.add('hidden');
    document.getElementById('cita-no-encontrada').classList.remove('hidden');
}

function cancelarDesdeEnlace() {
    document.getElementById('modal').classList.remove('hidden');
}

function cerrarModal() {
    document.getElementById('modal').classList.add('hidden');
}

function cancelarDesdeEnlace() {
    console.log('cancelarDesdeEnlace() LLAMADA');
    const modal = document.getElementById('modal');
    console.log('Modal encontrado:', modal);
    
    if (modal) {
        modal.classList.remove('hidden');
        console.log('Modal abierto');
    } else {
        console.log('ERROR: Modal NO encontrado');
    }
}
function irAlicio() {
    window.location.href = 'index.html';
}

// Cerrar modal al hacer click afuera
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        cerrarModal();
    }
}