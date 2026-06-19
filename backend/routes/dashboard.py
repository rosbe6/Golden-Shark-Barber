from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from database import mongodb
from models.cita import Cita
from utils.autenticacion import token_requerido

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# ==================== RUTAS PROTEGIDAS ====================

@dashboard_bp.route('/citas', methods=['GET'])
@token_requerido
def listar_citas(barbero_id):
    """
    Listar citas: Rosbin ve todas, otros barberos ven solo las suyas
    GET /api/dashboard/citas
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        coleccion_barbero = mongodb.get_collection('barbero')
        
        # Obtener nombre del barbero para saber si es Rosbin (admin)
        barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
        es_admin = barbero_actual and barbero_actual['nombre'] == 'Rosbin'
        
        # Si es Rosbin, ve todas; si no, solo las suyas
        if es_admin:
            citas = list(coleccion_citas.find({'estado': {'$ne': 'cancelada'}}))
        else:
            citas = list(coleccion_citas.find({
                'barbero_id': barbero_id,
                'estado': {'$ne': 'cancelada'}
            }))
        
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


@dashboard_bp.route('/citas/hoy', methods=['GET'])
@token_requerido
def citas_hoy(barbero_id):
    """
    Listar citas de hoy
    GET /api/dashboard/citas/hoy
    """
    try:
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        coleccion_citas = mongodb.get_collection('citas')
        citas = list(coleccion_citas.find({
            'dia': hoy,
            'estado': {'$ne': 'cancelada'}
        }).sort('hora', 1))
        
        # Convertir ObjectId a string
        for cita in citas:
            cita['_id'] = str(cita['_id'])
        
        return jsonify({
            'status': 'success',
            'fecha': hoy,
            'total': len(citas),
            'citas': citas
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@dashboard_bp.route('/citas/<cita_id>', methods=['GET'])
@token_requerido
def detalles_cita(barbero_id, cita_id):
    """
    Obtener detalles de una cita específica
    GET /api/dashboard/citas/abc123
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        cita = coleccion_citas.find_one({'_id': ObjectId(cita_id)})
        
        if not cita:
            return jsonify({'status': 'error', 'mensaje': 'Appointment not found'}), 404
        
        cita['_id'] = str(cita['_id'])
        
        return jsonify({
            'status': 'success',
            'cita': cita
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@dashboard_bp.route('/citas/<cita_id>/completar', methods=['PUT'])
@token_requerido
def completar_cita(barbero_id, cita_id):
    """
    Marcar una cita como completada
    PUT /api/dashboard/citas/abc123/completar
    """
    try:
        coleccion_citas = mongodb.get_collection('citas')
        
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {'estado': 'completada'}}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Appointment not found'}), 404
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Appointment marked as completed'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@dashboard_bp.route('/citas/<cita_id>/reagendar', methods=['PUT'])
@token_requerido
def reagendar_cita(barbero_id, cita_id):
    """
    Reagendar una cita a otro día/hora
    PUT /api/dashboard/citas/abc123/reagendar
    Body: {
        "nuevo_dia": "2026-06-22",
        "nueva_hora": "14:00"
    }
    """
    try:
        from utils.validaciones import horario_disponible
        
        data = request.json
        nuevo_dia = data.get('nuevo_dia')
        nueva_hora = data.get('nueva_hora')
        
        # Validar datos
        if not nuevo_dia or not nueva_hora:
            return jsonify({'status': 'error', 'mensaje': 'nuevo_dia and nueva_hora are required'}), 400
        
        # Validar que el horario esté disponible
        if not horario_disponible(nuevo_dia, nueva_hora):
            return jsonify({'status': 'error', 'mensaje': 'This time slot is not available'}), 400
        
        # Actualizar cita
        coleccion_citas = mongodb.get_collection('citas')
        
        resultado = coleccion_citas.update_one(
            {'_id': ObjectId(cita_id)},
            {'$set': {
                'dia': nuevo_dia,
                'hora': nueva_hora
            }}
        )
        
        if resultado.matched_count == 0:
            return jsonify({'status': 'error', 'mensaje': 'Appointment not found'}), 404
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Appointment rescheduled successfully',
            'nuevo_dia': nuevo_dia,
            'nueva_hora': nueva_hora
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@dashboard_bp.route('/perfil', methods=['GET'])
@token_requerido
def perfil_barbero(barbero_id):
    """
    Obtener datos del perfil del barbero
    GET /api/dashboard/perfil
    """
    try:
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
        
        if not barbero:
            return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404
        
        return jsonify({
            'status': 'success',
            'barbero': {
                'id': str(barbero['_id']),
                'nombre': barbero['nombre'],
                'email': barbero['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500