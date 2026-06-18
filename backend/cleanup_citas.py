from database import mongodb
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongodb.init_app(app)

db = mongodb.db

print("🔧 Eliminando índice único...")

# Eliminar el índice problemático
try:
    db.citas.drop_index("dia_1_hora_1_barbero_1")
    print("✅ Índice eliminado")
except Exception as e:
    print(f"⚠️ Error: {e}")

print("✅ Completado")