from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import mongodb
from models.barbero import Barbero
from utils.autenticacion import generar_token, verificar_token

auth_bp = Blueprint('autenticacion', __name__, url_prefix='/api/auth')

# ==================== RUTAS ====================

@auth_bp.route('/registrar', methods=['POST'])
def registrar():
    """
    Registrar un nuevo barbero (solo primera vez)
    POST /api/auth/registrar
    {
        "email": "barbero@email.com",
        "contraseña": "contraseña123",
        "nombre": "Carlos"
    }
    """
    try:
        data = request.json
        
        # Validar datos
        if not data.get('email') or not data.get('contraseña'):
            return jsonify({'status': 'error', 'mensaje': 'Email and password are required'}), 400
        
        # Verificar que no exista ya un barbero
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero_existente = coleccion_barbero.find_one({'email': data['email']})
        
        if barbero_existente:
            return jsonify({'status': 'error', 'mensaje': 'Barber already registered'}), 400
        
        # Crear nuevo barbero
        barbero = Barbero(
            email=data['email'],
            contraseña=data['contraseña'],
            nombre=data.get('nombre', 'Admin')
        )
        
        # Guardar en MongoDB
        resultado = coleccion_barbero.insert_one(barbero.to_dict())
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Barber registered successfully',
            'barbero_id': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login del barbero
    POST /api/auth/login
    {
        "email": "barbero@email.com",
        "contraseña": "contraseña123"
    }
    """
    try:
        data = request.json
        
        # Validar datos
        if not data.get('email') or not data.get('contraseña'):
            return jsonify({'status': 'error', 'mensaje': 'Email and password are required'}), 400
        
        # Buscar barbero
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero_data = coleccion_barbero.find_one({'email': data['email']})
        
        if not barbero_data:
            return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 401
        
        # Verificar contraseña
        barbero = Barbero.from_dict(barbero_data)
        
        if not barbero.verificar_contraseña(data['contraseña']):
            return jsonify({'status': 'error', 'mensaje': 'Incorrect password'}), 401
        
        # Generar token
        token = generar_token(barbero._id)
        
        return jsonify({
            'status': 'success',
            'mensaje': 'Login successful',
            'token': token,
            'barbero_id': str(barbero._id),
            'nombre': barbero.nombre
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)}), 500


@auth_bp.route('/verificar', methods=['GET'])
def verificar():
    """
    Verificar si un token es válido
    GET /api/auth/verificar
    Headers: Authorization: Bearer <token>
    """
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'status': 'error', 'mensaje': 'Invalid token format'}), 401
    
    if not token:
        return jsonify({'status': 'error', 'mensaje': 'Token is missing'}), 401
    
    es_valido, resultado = verificar_token(token)
    
    if es_valido:
        return jsonify({'status': 'success', 'barbero_id': resultado}), 200
    else:
        return jsonify({'status': 'error', 'mensaje': resultado}), 401
    

@auth_bp.route('/barberos', methods=['GET'])
def listar_todos_barberos():
    """
    Listar todos los barberos (solo para admin)
    GET /api/auth/barberos
    Headers: Authorization: Bearer <token>
    """
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'status': 'error', 'mensaje': 'Invalid token format'}), 401
    
    if not token:
        return jsonify({'status': 'error', 'mensaje': 'Token is missing'}), 401
    
    es_valido, resultado = verificar_token(token)
    
    if not es_valido:
        return jsonify({'status': 'error', 'mensaje': resultado}), 401
    
    # Verificar que sea admin
    coleccion_barbero = mongodb.get_collection('barbero')
    barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(resultado)})
    
    # ✅ CAMBIAR: Usar es_admin en lugar de nombre
    if not barbero_actual or not barbero_actual.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Only admin can view all barbers'}), 403
    
    # Listar todos
    barberos = list(coleccion_barbero.find({}, {'contraseña_hash': 0}))
    for b in barberos:
        b['_id'] = str(b['_id'])
    
    return jsonify({
        'status': 'success',
        'barberos': barberos
    }), 200

@auth_bp.route('/barberos/<barbero_id>', methods=['DELETE'])
def eliminar_barbero(barbero_id):
    """
    Eliminar un barbero (solo para admin)
    DELETE /api/auth/barberos/abc123
    Headers: Authorization: Bearer <token>
    """
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'status': 'error', 'mensaje': 'Invalid token format'}), 401
    
    if not token:
        return jsonify({'status': 'error', 'mensaje': 'Token is missing'}), 401
    
    es_valido, resultado = verificar_token(token)
    
    if not es_valido:
        return jsonify({'status': 'error', 'mensaje': resultado}), 401
    
    # Verificar que sea admin
    coleccion_barbero = mongodb.get_collection('barbero')
    barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(resultado)})
    
    # ✅ CAMBIAR: Usar es_admin en lugar de nombre
    if not barbero_actual or not barbero_actual.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Only admin can delete barbers'}), 403
    
    # No permitir eliminar al admin
    barbero_a_eliminar = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
    if barbero_a_eliminar and barbero_a_eliminar.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Cannot delete admin'}), 400
    
    # Eliminar
    resultado = coleccion_barbero.delete_one({'_id': ObjectId(barbero_id)})
    
    if resultado.deleted_count == 0:
        return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404
    
    return jsonify({
        'status': 'success',
        'mensaje': 'Barber deleted successfully'
    }), 200


@auth_bp.route('/perfil', methods=['GET'])
def perfil():
    """
    Obtener datos del usuario actual
    GET /api/auth/perfil
    Headers: Authorization: Bearer <token>
    """
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'status': 'error', 'mensaje': 'Invalid token format'}), 401
    
    if not token:
        return jsonify({'status': 'error', 'mensaje': 'Token is missing'}), 401
    
    es_valido, resultado = verificar_token(token)
    
    if es_valido:
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero = coleccion_barbero.find_one({'_id': ObjectId(resultado)})
        
        if not barbero:
            return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404
        
        return jsonify({
            'status': 'success',
            'barbero_id': str(barbero['_id']),
            'nombre': barbero['nombre'],
            'email': barbero['email'],
            'es_admin': barbero.get('es_admin', False)
        }), 200
    else:
        return jsonify({'status': 'error', 'mensaje': resultado}), 401