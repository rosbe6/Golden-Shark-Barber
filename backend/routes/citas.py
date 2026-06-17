from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb
from models.cita import Cita
from services.email_service import EmailService
from services.google_calendar import GoogleCalendarService

# Crear el blueprint
citas_bp = Blueprint('citas', __name__, url_prefix='/api/citas')

# Servicios
email_service = EmailService()

# ==================== RUTAS ====================

@citas_bp.route('/disponibles', methods=['GET'])
def obtener_disponibles():
    """
    Obtener horarios disponibles (todos los días lunes-sábado del próximo año)
    """
    horarios = ['10:00', '10:40', '11:20', '12:00', '12:40', '13:20', '14:00',
                '14:40', '15:20', '16:00', '16:40']
    
    # Generar todos los días lunes-sábado del próximo año
    dias = []
    fecha_inicio = datetime.now()
    
    for i in range(365):
        fecha = fecha_inicio + timedelta(days=i)
        # Si es lunes (0) a sábado (5), agregar
        if fecha.weekday() < 6:
            dias.append(fecha.strftime('%Y-%m-%d'))
    
    return jsonify({
        'status': 'success',
        'dias': dias,
        'horarios': horarios
    }), 200


@citas_bp.route('/crear', methods=['POST'])
def crear_cita():
    """Crear una nueva cita y enviar emails"""
    
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['cliente_nombre', 'cliente_email', 'cliente_telefono', 
                            'dia', 'hora', 'servicio', 'metodoPago', 'precio']
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'status': 'error',
                    'mensaje': f'Missing required field: {campo}'
                }), 400
        
        # Validar que el precio sea un número
        try:
            precio = int(data['precio'])
        except:
            return jsonify({
                'status': 'error',
                'mensaje': 'Price must be a number'
            }), 400
        
        # Crear la cita
        cita = Cita(
            cliente_nombre=data['cliente_nombre'],
            cliente_email=data['cliente_email'],
            cliente_telefono=data['cliente_telefono'],
            dia=data['dia'],
            hora=data['hora'],
            servicio=data['servicio'],
            metodoPago=data['metodoPago'],
            precio=precio,
            instrucciones=data.get('instrucciones', '')
        )
        
        # Guardar en BD
        db = mongodb.db
        resultado = db.citas.insert_one(cita.to_dict())
        cita_id = str(resultado.inserted_id)
        
        # Enviar email de confirmación al cliente
        try:
            email_service.enviar_confirmacion(data, cita_id)
            print(f"✅ Email de confirmación enviado a {data['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error al enviar email de confirmación: {str(e)}")
        
        # Enviar notificación al barbero
        # Enviar notificación al barbero
        try:
            barberos = list(db.barbero.find({}))
            
            if barberos:
                for barbero in barberos:
                    email_barbero = barbero.get('email')
                    nombre_barbero = barbero.get('nombre', 'Barbero')
                    
                    if email_barbero:
                        try:
                            resultado = email_service.enviar_notificacion_barbero(data, cita_id, email_barbero)
                            print(f"✅ Notificación enviada a {nombre_barbero}: {email_barbero}")
                            print(f"   Resultado: {resultado}")
                        except Exception as email_error:
                            print(f"❌ Error enviando email a {email_barbero}")
                            print(f"   Error: {str(email_error)}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"⚠️ {nombre_barbero} no tiene email configurado")
            else:
                print("⚠️ No se encontraron barberos")
                
        except Exception as e:
            print(f"❌ Error en notificación de barbero: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Agregar a Google Calendar si el barbero tiene token
        try:
            barbero = db.barberos.find_one()
            if barbero and barbero.get('google_token'):
                calendar_service = GoogleCalendarService()
                calendar_service.authenticate(barbero['google_token'])
                calendar_service.crear_evento(data)
                print(f"✅ Evento agregado a Google Calendar")
        except Exception as e:
            print(f"⚠️ Error al agregar a Google Calendar: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'cita_id': cita_id,
            'mensaje': 'Cita creada exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error al crear cita: {str(e)}")
        return jsonify({
            'status': 'error',
            'mensaje': f'Error creating appointment: {str(e)}'
        }), 500
    

@citas_bp.route('/<cita_id>', methods=['GET'])
def obtener_cita(cita_id):
    """
    Obtener detalles de una cita por ID
    GET /api/citas/abc123
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Appointment not found'}), 404
        
        cita['_id'] = str(cita['_id'])
        return jsonify({'status': 'success', 'cita': cita}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/<cita_id>/cancelar', methods=['DELETE'])
def cancelar_cita(cita_id):
    """
    Cancelar una cita
    DELETE /api/citas/abc123/cancelar
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {'estado': 'cancelada'}}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Appointment not found'}), 404
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Appointment cancelled successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/listar/todas', methods=['GET'])
def listar_todas_citas():
    """
    Listar todas las citas (para el barbero)
    GET /api/citas/listar/todas
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        citas = list(coleccion_citas.find({'estado': {'$ne': 'cancelada'}}))
        
        # Convertir ObjectId a string
        for cita in citas:
            cita['_id'] = str(cita['_id'])
        
        return jsonify({
            'status': 'success',
            'total': len(citas),
            'citas': citas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500
    

@citas_bp.route('/horarios-ocupados/<dia>', methods=['GET'])
def horarios_ocupados(dia):
    """
    Obtener horarios ocupados para un día específico
    GET /api/citas/horarios-ocupados/2026-06-15
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        # Buscar citas en ese día que NO estén canceladas
        citas = coleccion_citas.find({
            'dia': dia,
            'estado': {'$ne': 'cancelada'}
        })
        
        # Extraer las horas ocupadas
        horas_ocupadas = [cita['hora'] for cita in citas]
        
        return jsonify({
            'status': 'success',
            'dia': dia,
            'horas_ocupadas': horas_ocupadas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500