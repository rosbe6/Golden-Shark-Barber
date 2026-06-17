import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from bson import ObjectId
from database import mongodb

def generar_token(barbero_id):
    """
    Generar un JWT token para el barbero
    """
    payload = {
        'barbero_id': str(barbero_id),
        'exp': datetime.utcnow() + timedelta(days=7),  # Token válido por 7 días
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verificar_token(token):
    """
    Verificar si un token JWT es válido
    Devuelve: (es_valido, barbero_id o mensaje_error)
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        barbero_id = payload.get('barbero_id')
        return True, barbero_id
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"


def token_requerido(f):
    """
    Decorador para proteger rutas que requieren autenticación
    """
    @wraps(f)
    def decorado(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'status': 'error', 'mensaje': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'status': 'error', 'mensaje': 'Token is missing'}), 401
        
        # Verificar el token
        es_valido, resultado = verificar_token(token)
        
        if not es_valido:
            return jsonify({'status': 'error', 'mensaje': resultado}), 401
        
        # El token es válido, pasar el barbero_id a la función
        return f(resultado, *args, **kwargs)
    
    return decorado