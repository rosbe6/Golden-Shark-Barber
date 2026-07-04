import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from database import mongodb
from bcrypt import hashpw, gensalt

# Crear app Flask para inicializar MongoDB
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongodb.init_app(app)

def migrar_contraseñas():
    with app.app_context():
        coleccion = mongodb.get_collection('barbero')
        barberos = list(coleccion.find({}))
        
        for barbero in barberos:
            password_actual = barbero.get('contraseña') or barbero.get('password', '')
            
            if not password_actual:
                print(f"⚠️ {barbero['nombre']} sin contraseña")
                continue
            
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
            print(f"✅ {barbero['nombre']} migrado a bcrypt")

migrar_contraseñas()
print("🎉 Migración completada")