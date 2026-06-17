from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb

def horario_disponible(dia, hora):
    """
    Validar si un horario está disponible
    Devuelve True si está disponible, False si está ocupado
    """
    coleccion_citas = mongodb.get_collection('citas')
    
    # Buscar citas en el mismo día y hora que NO estén canceladas
    cita_existente = coleccion_citas.find_one({
        'dia': dia,
        'hora': hora,
        'estado': {'$ne': 'cancelada'}
    })
    
    if cita_existente:
        return False  # No disponible
    
    return True  # Disponible


def bloqueo_temporal_vigente(dia, hora):
    """
    Validar si hay un bloqueo temporal (cita no confirmada hace menos de 15 min)
    Devuelve True si hay bloqueo, False si no
    """
    coleccion_citas = mongodb.get_collection('citas')
    
    # Buscar citas "pendiente_confirmacion" en el mismo día y hora
    ahora = datetime.now()
    hace_15_minutos = ahora - timedelta(minutes=15)
    
    cita_bloqueada = coleccion_citas.find_one({
        'dia': dia,
        'hora': hora,
        'estado': 'pendiente_confirmacion',
        'fecha_creacion': {'$gt': hace_15_minutos}
    })
    
    if cita_bloqueada:
        return True  # Hay bloqueo vigente
    
    return False  # No hay bloqueo


def validar_cita(cliente_nombre, cliente_email, cliente_telefono, dia, hora, servicio):
    """
    Validación completa de una cita
    Devuelve: (es_valida, mensaje_error)
    """
    
    # Validar que no esté vacío
    if not cliente_nombre or not cliente_email or not cliente_telefono or not dia or not hora or not servicio:
        return False, "All fields are required"
    
    # Validar formato de email
    if '@' not in cliente_email:
        return False, "Invalid email format"
    
    # Validar que la fecha sea válida
    try:
        fecha_obj = datetime.strptime(dia, '%Y-%m-%d')
        # Validar que no sea una fecha pasada
        if fecha_obj.date() < datetime.now().date():
            return False, "Cannot book appointments in the past"
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)"
    
    # Validar que sea lunes a sábado (weekday 0-5)
    if fecha_obj.weekday() > 5:  # 6 es domingo
        return False, "Barbershop is closed on Sundays"
    
    # Validar horario válido
    horarios_validos = ['9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00',
                        '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                        '16:00', '16:30', '17:00', '17:30']
    
    if hora not in horarios_validos:
        return False, f"Invalid time. Available times: {', '.join(horarios_validos)}"
    
    # Validar que no hay bloqueo temporal
    if bloqueo_temporal_vigente(dia, hora):
        return False, "This time slot is currently being reserved by another client. Try again in a moment"
    
    # Validar que el horario esté disponible
    if not horario_disponible(dia, hora):
        return False, "This time slot is not available"
    
    return True, ""