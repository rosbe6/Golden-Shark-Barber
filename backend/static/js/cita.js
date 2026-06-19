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
    
    document.getElementById('cargando').classList.add('hidden');
    document.getElementById('cita-encontrada').classList.remove('hidden');
    
    document.getElementById('det-servicio').textContent = cita.servicio || '-';
    
    // ✅ NUEVO (sin interpretación de zona horaria)
    const partes = cita.dia.split('-');
    const fecha = new Date(parseInt(partes[0]), parseInt(partes[1]) - 1, parseInt(partes[2]));
    const fechaFormato = fecha.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    document.getElementById('det-fecha').textContent = fechaFormato;
    
    document.getElementById('det-hora').textContent = cita.hora || '-';
    
    let estado = cita.estado || 'confirmed';
    if (estado === 'cancelada' || estado === 'cancelled') {
        estado = 'Cancelled';
    } else if (estado === 'completada' || estado === 'completed') {
        estado = 'Completed';
    } else {
        estado = 'Confirmed';
    }
    document.getElementById('det-estado').textContent = estado;
    
    const metodoPago = cita.metodoPago === 'cash' ? 'Cash' : 'Credit Card';
    document.getElementById('det-metodoPago').textContent = metodoPago;
    
    document.getElementById('det-precio-monto').textContent = cita.precio || '0';
    
    document.getElementById('det-nombre').textContent = cita.cliente_nombre || '-';
    document.getElementById('det-email').textContent = cita.cliente_email || '-';
    document.getElementById('det-telefono').textContent = cita.cliente_telefono || '-';
    
    if (cita.instrucciones && cita.instrucciones.trim() !== '') {
        document.getElementById('det-instrucciones-container').classList.remove('hidden');
        document.getElementById('det-instrucciones').textContent = cita.instrucciones;
    }
    
    if (estado === 'Cancelled') {
        const btnCancelar = document.getElementById('btn-cancelar');
        btnCancelar.disabled = true;
        btnCancelar.style.opacity = '0.5';
        btnCancelar.style.cursor = 'not-allowed';
    }
    
    window.citaIdActual = cita._id || cita.id;
}

function mostrarNoEncontrada() {
    console.log('Cita no encontrada');
    document.getElementById('cargando').classList.add('hidden');
    document.getElementById('cita-no-encontrada').classList.remove('hidden');
}

function cancelarDesdeEnlace() {
    console.log('Abriendo modal...');
    document.getElementById('modal').classList.remove('hidden');
}

function cerrarModal() {
    console.log('Cerrando modal...');
    document.getElementById('modal').classList.add('hidden');
}

function confirmarCancelacion() {
    if (!window.citaIdActual) {
        alert('Error: Appointment ID not found');
        return;
    }
    
    const motivo = prompt('Reason for cancellation:') || 'No reason specified';
    
    console.log('Cancelando cita:', window.citaIdActual);
    console.log('Motivo:', motivo);
    
    fetch(`${API_URL}/citas/${window.citaIdActual}/cancelar`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            motivo: motivo
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta cancelación:', data);
        
        if (data.status === 'success') {
            cerrarModal();
            
            document.getElementById('det-estado').textContent = 'Cancelled';
            
            const btnCancelar = document.getElementById('btn-cancelar');
            btnCancelar.disabled = true;
            btnCancelar.style.opacity = '0.5';
            btnCancelar.style.cursor = 'not-allowed';
            
            alert('✓ Appointment cancelled successfully');
        } else {
            alert('Error: ' + (data.mensaje || 'Could not cancel appointment'));
        }
    })
    .catch(error => {
        console.error('Error al cancelar:', error);
        alert('Error cancelling appointment');
    });
}

window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        cerrarModal();
    }
}