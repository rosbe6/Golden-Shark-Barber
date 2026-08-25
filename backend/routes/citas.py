from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb
from models.cita import Cita
from services.email_service import EmailService
from services.google_calendar import GoogleCalendarService
from pymongo.errors import DuplicateKeyError, OperationFailure
from services.telegram_service import TelegramService

# Crear el blueprint
citas_bp = Blueprint('citas', __name__, url_prefix='/api/citas')

# Servicios
email_service = EmailService()
telegram_service = TelegramService()

# ==================== RUTAS ====================

@citas_bp.route('/disponibles', methods=['GET'])
def obtener_disponibles():
    barbero_id = request.args.get('barbero_id')
    fecha_str = request.args.get('fecha')

    HORARIOS_VIEJOS = ['10:00', '10:40', '11:20', '12:00', '12:40', '13:20', '14:00',
                       '14:40', '15:20', '16:00', '16:40']
    HORARIOS_45 = ['09:45', '10:30', '11:15', '12:00', '12:45', '13:30', '14:15',
                   '15:00', '15:45', '16:30']
    HORARIOS_SABADO = ['09:45', '10:30', '11:15', '12:00', '12:45', '13:30', '14:15']

    FECHA_CORTE_45 = datetime(2026, 8, 24)        # Lunes 24 agosto: pasa a 45 min
    FECHA_CORTE_SABADO = datetime(2026, 9, 1)     # 1 septiembre: sábados hasta 2:15 PM

    def horarios_para(fecha):
        # Sábado (weekday 5) desde el 1 de septiembre: jornada corta
        if fecha >= FECHA_CORTE_SABADO and fecha.weekday() == 5:
            return HORARIOS_SABADO
        if fecha >= FECHA_CORTE_45:
            return HORARIOS_45
        return HORARIOS_VIEJOS

    dias = []
    fecha_inicio = datetime.now()

    coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')
    bloqueos = list(coleccion_bloqueos.find({
        '$or': [
            {'barbero_id': None},
            {'barbero_id': barbero_id}
        ]
    }))
    fechas_bloqueadas = set(b['fecha'] for b in bloqueos)

    for i in range(365):
        fecha = fecha_inicio + timedelta(days=i)
        fecha_str_dia = fecha.strftime('%Y-%m-%d')
        if fecha.weekday() < 6 and fecha_str_dia not in fechas_bloqueadas:
            dias.append(fecha_str_dia)

    if fecha_str:
        try:
            horarios = horarios_para(datetime.strptime(fecha_str, '%Y-%m-%d'))
        except ValueError:
            horarios = HORARIOS_VIEJOS
    else:
        horarios = horarios_para(datetime.now())

    return jsonify({
        'status': 'success',
        'dias': dias,
        'horarios': horarios,
        'barbero_id': barbero_id
    }), 200


@citas_bp.route('/barberos', methods=['GET'])
def listar_barberos():
    try:
        tipo = request.args.get('tipo')
        
        coleccion_barbero = mongodb.get_collection('barbero')
        
        query = {}
        if tipo:
            query['tipo'] = tipo
        
        barberos = list(coleccion_barbero.find(query, {'_id': 1, 'nombre': 1, 'tipo': 1}))
        
        for barbero in barberos:
            barbero['_id'] = str(barbero['_id'])
        
        return jsonify({'status': 'success', 'barberos': barberos}), 200
        
    except Exception as e:
        print(f"❌ Error en /barberos: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': 'Error en el servidor'}), 500


@citas_bp.route('/crear', methods=['POST'])
def crear_cita():
    """Crear una nueva cita y enviar emails"""
    
    try:
        data = request.get_json()
        
        campos_requeridos = ['cliente_nombre', 'cliente_email', 'cliente_telefono', 
                            'dia', 'hora', 'servicio', 'metodoPago', 'precio', 'barbero_id']
        
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'status': 'error',
                    'mensaje': f'Missing required field: {campo}'
                }), 400
        
        try:
            precio = int(data['precio'])
        except:
            return jsonify({
                'status': 'error',
                'mensaje': 'Price must be a number'
            }), 400
        
        db = mongodb.db
        
        print(f"🔍 Buscando: dia={data['dia']}, hora={data['hora']}, barbero_id={data['barbero_id']}, estado=confirmada")
        
        cita_existe = db.citas.find_one({
            'dia': data['dia'],
            'hora': data['hora'],
            'barbero_id': data['barbero_id'],
            'estado': 'confirmada'
        })
        
        if cita_existe:
            print(f"❌ BLOQUEADA - Horario {data['hora']} en {data['dia']} ya ocupado")
            return jsonify({
                'status': 'error',
                'mensaje': 'Ese horario ya está reservado. Por favor selecciona otro.',
                'tipo_error': 'horario_ocupado'
            }), 409
        
        print(f"✅ PERMITIDA - Horario disponible, creando cita...")
        
        cita = Cita(
            cliente_nombre=data['cliente_nombre'],
            cliente_email=data['cliente_email'],
            cliente_telefono=data['cliente_telefono'],
            dia=data['dia'],
            hora=data['hora'],
            servicio=data['servicio'],
            metodoPago=data['metodoPago'],
            precio=precio,
            instrucciones=data.get('instrucciones', ''),
            barbero_id=data['barbero_id']
        )
        
        cita_dict = cita.to_dict()
        cita_dict['tipo_servicio'] = data.get('tipo_servicio', 'barber')
        resultado = db.citas.insert_one(cita_dict)
        cita_id = str(resultado.inserted_id)
        print(f"✅ Cita guardada: {cita_id}")
        
        # ✅ Obtener nombre, teléfono y tipo del especialista
        barbero_info = db.barbero.find_one({'_id': ObjectId(data['barbero_id'])})
        data['barbero_nombre'] = barbero_info['nombre'] if barbero_info else 'N/A'
        data['barbero_telefono'] = barbero_info.get('telefono', '') if barbero_info else ''
        data['tipo_servicio'] = data.get('tipo_servicio', 'barber')

        # Enviar email de confirmación al cliente
        try:
            email_service.enviar_confirmacion(data, cita_id)
            print(f"✅ Email de confirmación enviado a {data['cliente_email']}")
        except Exception as e:
            print(f"⚠️ Error al enviar email de confirmación: {str(e)}")
        
        # ✅ Notificar SOLO al barbero asignado y al admin (dueño)
        try:
            barberos_a_notificar = list(db.barbero.find({
                '$or': [
                    {'_id': ObjectId(data['barbero_id'])},
                    {'es_admin': True}
                ]
            }))
            
            emails_enviados = set()
            
            for barbero in barberos_a_notificar:
                email_barbero = barbero.get('email')
                nombre_barbero = barbero.get('nombre', 'Barbero')
                
                if email_barbero and email_barbero not in emails_enviados:
                    try:
                        email_service.enviar_notificacion_barbero(data, cita_id, email_barbero)
                        print(f"✅ Notificación enviada a {nombre_barbero}: {email_barbero}")
                        emails_enviados.add(email_barbero)
                    except Exception as email_error:
                        print(f"❌ Error enviando email a {email_barbero}")
                elif not email_barbero:
                    print(f"⚠️ {nombre_barbero} no tiene email configurado")
                    
        except Exception as e:
            print(f"❌ Error en notificación de barbero: {str(e)}")

                # ✅ Notificar por Telegram al admin
        try:
            telegram_service.notificar_nueva_cita(data, cita_id)
        except Exception as e:
            print(f"❌ Error enviando Telegram: {str(e)}")
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
        print(f"❌ Error al crear cita: {str(e)}")
        return jsonify({
            'status': 'error',
            'mensaje': f'Error creating appointment: {str(e)}'
        }), 500


@citas_bp.route('/horarios-ocupados/<dia>', methods=['GET'])
def horarios_ocupados(dia):
    try:
        barbero_id = request.args.get('barbero_id')
        
        if not barbero_id:
            return jsonify({
                'status': 'error',
                'mensaje': 'barbero_id is required'
            }), 400
        
        coleccion_citas = mongodb.get_collection('citas')
        
        citas = coleccion_citas.find({
            'dia': dia,
            'barbero_id': barbero_id,
            'estado': 'confirmada'
        })
        
        horas_ocupadas = [cita['hora'] for cita in citas]

        # ✅ Agregar slots bloqueados globalmente ese día
        coleccion_slots = mongodb.get_collection('slots_bloqueados')
        slots_bloqueados = list(coleccion_slots.find({'fecha': dia}))
        horas_bloqueadas = [s['hora'] for s in slots_bloqueados]

        horas_ocupadas = list(set(horas_ocupadas + horas_bloqueadas))
        
        return jsonify({
            'status': 'success',
            'dia': dia,
            'barbero_id': barbero_id,
            'horas_ocupadas': horas_ocupadas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500

@citas_bp.route('/<cita_id>', methods=['GET'])
def obtener_cita(cita_id):
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
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {'estado': 'completada'}}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
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


@citas_bp.route('/<cita_id>/cancelar', methods=['PUT'])
def cancelar_cita(cita_id):
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Sin motivo especificado')
        
        coleccion_citas = mongodb.get_collection('citas')
        
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
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
    try:
        data = request.get_json()
        nueva_fecha = data.get('nueva_fecha')
        nueva_hora = data.get('nueva_hora')
        motivo = data.get('motivo', 'Client request')
        
        if not nueva_fecha or not nueva_hora:
            return jsonify({
                'status': 'error',
                'mensaje': 'Nueva fecha y hora son requeridas'
            }), 400
        
        coleccion_citas = mongodb.get_collection('citas')
        
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Cita no encontrada'}), 404
        
        fecha_anterior = cita.get('dia')
        hora_anterior = cita.get('hora')
        
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
    try:
        coleccion_citas = mongodb.get_collection('citas')
        citas = list(coleccion_citas.find({'estado': {'$ne': 'cancelada'}}))
        
        for cita in citas:
            cita['_id'] = str(cita['_id'])
        
        return jsonify({
            'status': 'success',
            'total': len(citas),
            'citas': citas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500
    

@citas_bp.route('/barbero/<barbero_id>', methods=['GET'])
def obtener_barbero(barbero_id):
    try:
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
        
        if not barbero:
            return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404
        
        return jsonify({
            'status': 'success',
            'barbero': {
                '_id': str(barbero['_id']),
                'nombre': barbero['nombre'],
                'email': barbero['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500



import os

@citas_bp.route('/config', methods=['GET'])
def obtener_config():
    """
    Configuración pública del sitio (feature flags)
    GET /api/citas/config
    """
    try:
        skincare_enabled = os.getenv('SKINCARE_ENABLED', 'true').lower() == 'true'
        return jsonify({
            'status': 'success',
            'skincare_enabled': skincare_enabled
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': 'Error en el servidor'}), 500



@citas_bp.route('/bloquear-slot', methods=['POST'])
def bloquear_slot():
    """
    Bloquear un horario específico en una fecha
    POST /api/citas/bloquear-slot
    { "fecha": "2026-08-26", "hora": "10:30" }
    """
    try:
        data = request.get_json()
        fecha = data.get('fecha')
        hora = data.get('hora')

        if not fecha or not hora:
            return jsonify({'status': 'error', 'mensaje': 'fecha and hora are required'}), 400

        coleccion = mongodb.get_collection('slots_bloqueados')

        # Evitar duplicados
        existe = coleccion.find_one({'fecha': fecha, 'hora': hora})
        if existe:
            return jsonify({'status': 'error', 'mensaje': 'This slot is already blocked'}), 409

        coleccion.insert_one({
            'fecha': fecha,
            'hora': hora,
            'creado_en': datetime.now().isoformat()
        })

        return jsonify({'status': 'success', 'mensaje': 'Slot blocked successfully'}), 201

    except Exception as e:
        print(f"❌ Error bloqueando slot: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': 'Error en el servidor'}), 500


@citas_bp.route('/bloquear-dia', methods=['POST'])
def bloquear_dia():
    """
    Reutiliza el sistema de dias_bloqueados existente
    POST /api/citas/bloquear-dia
    { "fecha": "2026-08-26", "barbero_id": null }
    """
    try:
        data = request.get_json()
        fecha = data.get('fecha')
        barbero_id = data.get('barbero_id', None)

        if not fecha:
            return jsonify({'status': 'error', 'mensaje': 'fecha is required'}), 400

        coleccion = mongodb.get_collection('dias_bloqueados')
        existe = coleccion.find_one({'fecha': fecha, 'barbero_id': barbero_id})
        if existe:
            return jsonify({'status': 'error', 'mensaje': 'This day is already blocked'}), 409

        coleccion.insert_one({
            'fecha': fecha,
            'barbero_id': barbero_id,
            'nombre_display': 'Whole Barbershop',
            'creado_en': datetime.now().isoformat()
        })

        return jsonify({'status': 'success', 'mensaje': 'Day blocked successfully'}), 201

    except Exception as e:
        print(f"❌ Error bloqueando día: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': 'Error en el servidor'}), 500

@citas_bp.route('/slots-bloqueados/<dia>', methods=['GET'])
def listar_slots_bloqueados(dia):
    """GET /api/citas/slots-bloqueados/2026-08-26"""
    try:
        coleccion = mongodb.get_collection('slots_bloqueados')
        slots = list(coleccion.find({'fecha': dia}))
        for s in slots:
            s['_id'] = str(s['_id'])
        return jsonify({'status': 'success', 'slots': slots}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/slots-bloqueados/<slot_id>', methods=['DELETE'])
def eliminar_slot_bloqueado(slot_id):
    """DELETE /api/citas/slots-bloqueados/<id>"""
    try:
        coleccion = mongodb.get_collection('slots_bloqueados')
        resultado = coleccion.delete_one({'_id': ObjectId(slot_id)})
        if resultado.deleted_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Slot not found'}), 404
        return jsonify({'status': 'success', 'mensaje': 'Slot unblocked'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/dias-bloqueados/<dia>', methods=['GET'])
def listar_dia_bloqueado(dia):
    """GET /api/citas/dias-bloqueados/2026-08-26"""
    try:
        coleccion = mongodb.get_collection('dias_bloqueados')
        bloqueos = list(coleccion.find({'fecha': dia}))
        for b in bloqueos:
            b['_id'] = str(b['_id'])
        return jsonify({'status': 'success', 'bloqueos': bloqueos}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@citas_bp.route('/dias-bloqueados/<bloqueo_id>', methods=['DELETE'])
def eliminar_dia_bloqueado(bloqueo_id):
    """DELETE /api/citas/dias-bloqueados/<id>"""
    try:
        coleccion = mongodb.get_collection('dias_bloqueados')
        resultado = coleccion.delete_one({'_id': ObjectId(bloqueo_id)})
        if resultado.deleted_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Block not found'}), 404
        return jsonify({'status': 'success', 'mensaje': 'Day unblocked'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500