import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener la ruta del archivo .env
backend_path = Path(__file__).parent
env_file = backend_path / '.env'

# Cargar el archivo .env
load_dotenv(env_file)

print(f"Buscando .env en: {env_file}")
print(f"¿Existe .env?: {env_file.exists()}")

class Config:
    """Configuración base de la aplicación"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    MONGO_URI = os.getenv('MONGO_URI')
    
    print(f"MONGO_URI cargado: {MONGO_URI}")