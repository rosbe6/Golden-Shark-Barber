// Variables globales
let slideActual = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    mostrarSlide(slideActual);
});

// Cambiar slide con botones prev/next
function cambiarSlide(n) {
    mostrarSlide(slideActual += n);
}

// Ir a un slide específico
function irAlSlide(n) {
    mostrarSlide(slideActual = n);
}

// Mostrar el slide activo
function mostrarSlide(n) {
    // Si n es mayor que el número de slides, volver al primero
    if (n >= slides.length) {
        slideActual = 0;
    }
    // Si n es menor a 0, ir al último slide
    if (n < 0) {
        slideActual = slides.length - 1;
    }
    
    // Ocultar todos los slides
    slides.forEach(slide => {
        slide.classList.remove('active');
    });
    
    // Desactivar todos los dots
    dots.forEach(dot => {
        dot.classList.remove('active');
    });
    
    // Mostrar el slide activo
    slides[slideActual].classList.add('active');
    dots[slideActual].classList.add('active');
}

// Navegación con teclado (izquierda/derecha)
document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowLeft') {
        cambiarSlide(-1);
    } else if (event.key === 'ArrowRight') {
        cambiarSlide(1);
    }
});