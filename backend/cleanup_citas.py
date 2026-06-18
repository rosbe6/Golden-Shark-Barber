from database import mongodb
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongodb.init_app(app)

db = mongodb.db

print("🔧 Arreglando índices y datos...")

# 1. Actualizar TODOS los documentos con barbero null
db.citas.update_many(
    { 'barbero': { '$in': [None, '', None] } },
    { '$set': { 'barbero': 'Rosbin' } }
)
print("✅ Documentos actualizados")

# 2. Eliminar TODOS los índices
try:
    db.citas.drop_indexes()
    print("✅ Todos los índices eliminados")
except Exception as e:
    print(f"⚠️ Error eliminando índices: {e}")

# 3. Crear índices nuevos (SIN unique)
db.citas.create_index([('dia', 1), ('hora', 1), ('barbero', 1)])
print("✅ Índice nuevo creado (sin unique)")

print("✅ COMPLETADO")