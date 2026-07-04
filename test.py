# Corre este script UNA VEZ para migrar contraseñas
from bcrypt import hashpw, gensalt
from database import mongodb

def migrar_contraseñas():
    coleccion = mongodb.get_collection('barbero')
    barberos = list(coleccion.find({}))
    
    for barbero in barberos:
        password_actual = barbero.get('contraseña') or barbero.get('password', '')
        
        # Si ya está hasheada con bcrypt, saltar
        if password_actual.startswith('$2b$'):
            print(f"✅ {barbero['nombre']} ya tiene bcrypt")
            continue
        
        # Encriptar
        password_hash = hashpw(password_actual.encode('utf-8'), gensalt()).decode('utf-8')
        
        coleccion.update_one(
            {'_id': barbero['_id']},
            {'$set': {'password': password_hash}}
        )
        print(f"✅ {barbero['nombre']} migrado")

migrar_contraseñas()