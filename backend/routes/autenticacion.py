from flask import Blueprint, request, jsonify
from bson import ObjectId
from database import mongodb
from models.barbero import Barbero
from utils.autenticacion import generar_token, verificar_token
import bcrypt
import os
import uuid

auth_bp = Blueprint('autenticacion', __name__, url_prefix='/api/auth')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads', 'barberos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        if not data.get('email') or not data.get('contraseña'):
            return jsonify({'status': 'error', 'mensaje': 'Email and password are required'}), 400
        
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero_existente = coleccion_barbero.find_one({'email': data['email']})
        
        if barbero_existente:
            return jsonify({'status': 'error', 'mensaje': 'Barber already registered'}), 400
        
        barbero = Barbero(
            email=data['email'],
            contraseña=data['contraseña'],
            nombre=data.get('nombre', 'Admin'),
            tipo=data.get('tipo', 'barber'),
            telefono=data.get('telefono', '')
        )
        
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
        
        if not data.get('email') or not data.get('contraseña'):
            return jsonify({'status': 'error', 'mensaje': 'Email and password are required'}), 400
        
        coleccion_barbero = mongodb.get_collection('barbero')
        barbero_data = coleccion_barbero.find_one({'email': data['email']})
        
        if not barbero_data:
            return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 401
        
        barbero = Barbero.from_dict(barbero_data)
        
        if not barbero.verificar_contraseña(data['contraseña']):
            return jsonify({'status': 'error', 'mensaje': 'Incorrect password'}), 401
        
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
    
    coleccion_barbero = mongodb.get_collection('barbero')
    barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(resultado)})
    
    if not barbero_actual or not barbero_actual.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Only admin can view all barbers'}), 403
    
    barberos = list(coleccion_barbero.find({}, {'contraseña_hash': 0}))
    for b in barberos:
        b['_id'] = str(b['_id'])
    
    return jsonify({
        'status': 'success',
        'barberos': barberos
    }), 200


@auth_bp.route('/barberos/<barbero_id>', methods=['PUT'])
def editar_barbero(barbero_id):
    """
    Editar un barbero (solo admin)
    PUT /api/auth/barberos/abc123
    FormData: nombre, email, telefono, tipo, contraseña (opcional), foto (opcional, file)
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

    coleccion_barbero = mongodb.get_collection('barbero')
    barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(resultado)})

    if not barbero_actual or not barbero_actual.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Only admin can edit barbers'}), 403

    barbero_editar = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
    if not barbero_editar:
        return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404

    try:
        nombre = request.form.get('nombre', barbero_editar['nombre'])
        email = request.form.get('email', barbero_editar['email'])
        telefono = request.form.get('telefono', barbero_editar.get('telefono', ''))
        tipo = request.form.get('tipo', barbero_editar.get('tipo', 'barber'))
        contraseña = request.form.get('contraseña', '').strip()

        update_data = {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'tipo': tipo
        }

        if contraseña:
            salt = bcrypt.gensalt()
            update_data['contraseña_hash'] = bcrypt.hashpw(contraseña.encode('utf-8'), salt).decode('utf-8')

        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{barbero_id}_{uuid.uuid4().hex[:8]}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                update_data['foto'] = f"/uploads/barberos/{filename}"

        coleccion_barbero.update_one({'_id': ObjectId(barbero_id)}, {'$set': update_data})

        return jsonify({'status': 'success', 'mensaje': 'Barber updated successfully'}), 200

    except Exception as e:
        print(f"❌ Error editando barbero: {str(e)}")
        return jsonify({'status': 'error', 'mensaje': 'Error en el servidor'}), 500


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
    
    coleccion_barbero = mongodb.get_collection('barbero')
    barbero_actual = coleccion_barbero.find_one({'_id': ObjectId(resultado)})
    
    if not barbero_actual or not barbero_actual.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Only admin can delete barbers'}), 403
    
    barbero_a_eliminar = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
    if not barbero_a_eliminar:
        return jsonify({'status': 'error', 'mensaje': 'Barber not found'}), 404
    
    if barbero_a_eliminar.get('es_admin', False):
        return jsonify({'status': 'error', 'mensaje': 'Cannot delete the owner'}), 400
    
    if str(barbero_actual['_id']) == barbero_id:
        return jsonify({'status': 'error', 'mensaje': 'Cannot delete yourself'}), 400
    
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