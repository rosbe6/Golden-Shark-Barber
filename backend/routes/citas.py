from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb
from models.cita import Cita
from services.email_service import EmailService
from services.google_calendar import GoogleCalendarService
from pymongo.errors import DuplicateKeyError

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
        
        # ✅ VALIDAR QUE NO EXISTA CITA CONFIRMADA EN ESE HORARIO
        db = mongodb.db
        cita_existe = db.citas.find_one({
            'dia': data['dia'],
            'hora': data['hora'],
            'barbero': 'Rosbin',
            'estado': 'confirmed'  # ← SOLO las confirmadas
        })
        
        if cita_existe:
            return jsonify({
                'status': 'error',
                'mensaje': 'Ese horario ya está reservado. Por favor selecciona otro.',
                'tipo_error': 'horario_ocupado'
            }), 409
        
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
        resultado = db.citas.insert_one(cita.to_dict())
        cita_id = str(resultado.inserted_id)
        
        # Enviar email de confirmación al cliente
        try:
            email_service.enviar_confirmacion(data, cita_id)
            print(f"✅ Email de confirmación enviado a {data['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error al enviar email de confirmación: {str(e)}")
        
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
                        except Exception as email_error:
                            print(f"❌ Error enviando email a {email_barbero}")
                            print(f"   Error: {str(email_error)}")
                    else:
                        print(f"⚠️ {nombre_barbero} no tiene email configurado")
            else:
                print("⚠️ No se encontraron barberos")
                
        except Exception as e:
            print(f"❌ Error en notificación de barbero: {str(e)}")
        
        # Agregar a Google Calendar si el barbero tiene token
        try:
            barbero = db.barbero.find_one()
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


@citas_bp.route('/<cita_id>/completada', methods=['PUT'])
def marcar_completada(cita_id):
    """
    Marcar una cita como completada
    PUT /api/citas/abc123/completada
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        # Obtener la cita primero para enviar email
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # Actualizar estado
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {'estado': 'completada'}}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # Enviar email de confirmación al cliente
        try:
            asunto = "Tu cita ha sido completada - Gold Shark Barber"
            mensaje = f"""
            <h2>¡Tu cita ha sido completada!</h2>
            <p>Hola {cita.get('cliente_nombre')},</p>
            <p>Tu cita del <strong>{cita.get('dia')}</strong> a las <strong>{cita.get('hora')}</strong> ha sido completada.</p>
            <p>Servicio: <strong>{cita.get('servicio')}</strong></p>
            <p>¡Gracias por visitarnos en Gold Shark Barber!</p>
            <p>Te esperamos pronto.</p>
            """
            email_service.enviar_email(cita.get('cliente_email'), asunto, mensaje)
            print(f"✅ Email de completación enviado a {cita.get('cliente_email')}")
        except Exception as e:
            print(f"⚠️ Error al enviar email: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Cita marcada como completada'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

# REEMPLAZA ESTAS 2 FUNCIONES EN TU citas.py ACTUAL

@citas_bp.route('/<cita_id>/cancelar', methods=['PUT'])
def cancelar_cita(cita_id):
    """
    Cancelar una cita con motivo
    PUT /api/citas/abc123/cancelar
    Body: { "motivo": "Barbero enfermo" }
    """
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Sin motivo especificado')
        
        coleccion_citas = mongodb.get_collection('citas')
        
        # Obtener la cita primero para enviar email
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # Actualizar estado con motivo
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {
                'estado': 'cancelada',
                'motivo_cancelacion': motivo,
                'fecha_cancelacion': datetime.now().isoformat()
            }}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # ENVIAR EMAIL DE CANCELACIÓN AL CLIENTE
        try:
            email_service.enviar_cancelacion(cita, motivo)
            print(f"✅ Email de cancelación enviado a {cita.get('cliente_email')}")
        except Exception as e:
            print(f"⚠️ Error al enviar email de cancelación: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Cita cancelada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/<cita_id>/reagendar', methods=['PUT'])
def reagendar_cita(cita_id):
    """
    Reagendar una cita a nueva fecha y hora
    PUT /api/citas/abc123/reagendar
    Body: { "nueva_fecha": "2026-07-15", "nueva_hora": "14:00", "motivo": "Conflicto de horario" }
    """
    try:
        data = request.get_json()
        nueva_fecha = data.get('nueva_fecha')
        nueva_hora = data.get('nueva_hora')
        motivo = data.get('motivo', 'Client request')
        
        # Validar que tenemos fecha y hora
        if not nueva_fecha or not nueva_hora:
            return jsonify({
                'status': 'error',
                'mensaje': 'Nueva fecha y hora son requeridas'
            }), 400
        
        coleccion_citas = mongodb.get_collection('citas')
        
        # Obtener la cita primero
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # Guardar fecha anterior
        fecha_anterior = cita.get('dia')
        hora_anterior = cita.get('hora')
        
        # Actualizar la cita con nueva fecha/hora
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {
                'dia': nueva_fecha,
                'hora': nueva_hora,
                'fecha_anterior': fecha_anterior,
                'hora_anterior': hora_anterior,
                'motivo_reagendamiento': motivo,
                'fecha_reagendamiento': datetime.now().isoformat()
            }}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        # ENVIAR EMAIL DE REAGENDAMIENTO AL CLIENTE
        try:
            email_service.enviar_reagendamiento(cita, nueva_fecha, nueva_hora, motivo)
            print(f"✅ Email de reagendamiento enviado a {cita.get('cliente_email')}")
        except Exception as e:
            print(f"⚠️ Error al enviar email de reagendamiento: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Cita reagendada exitosamente',
            'nueva_fecha': nueva_fecha,
            'nueva_hora': nueva_hora
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
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        # Buscar citas en ese día que estén CONFIRMADAS (excluir canceladas y completadas)
        citas = coleccion_citas.find({
            'dia': dia,
            'estado': 'confirmed'  # ← SOLO las confirmadas
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
        
        # Extraer las horas ocupadas
        horas_ocupadas = [cita['hora'] for cita in citas]
        
        return jsonify({
            'status': 'success',
            'dia': dia,
            'horas_ocupadas': horas_ocupadas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500