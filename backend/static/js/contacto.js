// Manejo del formulario de contacto
document.addEventListener('DOMContentLoaded', function() {
    const formulario = document.getElementById('formularioContacto');
    const mensajeDiv = document.getElementById('formularioMensaje');

    formulario.addEventListener('submit', function(e) {
        e.preventDefault();

        // Obtener valores del formulario
        const nombre = document.getElementById('nombre').value.trim();
        const email = document.getElementById('email').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const asunto = document.getElementById('asunto').value.trim();
        const mensaje = document.getElementById('mensaje').value.trim();

        // Validar campos requeridos
        if (!nombre || !email || !asunto || !mensaje) {
            mostrarMensaje('Please fill in all required fields.', 'error');
            return;
        }

        // Validar email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            mostrarMensaje('Please enter a valid email address.', 'error');
            return;
        }

        // Si todo es válido, mostrar mensaje de éxito
        mostrarMensaje('Thank you for your message! We will contact you soon.', 'exito');

        // Limpiar formulario
        formulario.reset();

        // Opcional: aquí podrías enviar los datos a un servidor
        // enviarAlServidor(nombre, email, telefono, asunto, mensaje);
    });

    function mostrarMensaje(texto, tipo) {
        mensajeDiv.textContent = texto;
        mensajeDiv.className = `formulario-mensaje ${tipo}`;
        mensajeDiv.style.display = 'block';

        // Ocultar el mensaje después de 5 segundos
        setTimeout(() => {
            mensajeDiv.style.display = 'none';
        }, 5000);
    }

    // Función para enviar datos al servidor (si es necesario)
    // Descomentar si quieres integrar con un backend
    /*
    function enviarAlServidor(nombre, email, telefono, asunto, mensaje) {
        const datos = {
            nombre: nombre,
            email: email,
            telefono: telefono,
            asunto: asunto,
            mensaje: mensaje
        };

        fetch('/api/contacto', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
    */
});