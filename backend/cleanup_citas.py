from database import mongodb
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mongodb.init_app(app)

print("🔧 Eliminando duplicados...")

db = mongodb.db

# Encontrar duplicados
duplicados = db.citas.aggregate([
    {
        '$group': {
            '_id': { 'dia': '$dia', 'hora': '$hora', 'barbero': '$barbero' },
            'count': { '$sum': 1 },
            'ids': { '$push': '$_id' }
        }
    },
    { '$match': { 'count': { '$gt': 1 } } }
])

for dup in duplicados:
    print(f"⚠️ Duplicado encontrado: {dup['_id']}")
    # Eliminar el SEGUNDO (dejar el primero)
    ids_a_eliminar = dup['ids'][1:]  # Todos menos el primero
    for id_eliminar in ids_a_eliminar:
        db.citas.delete_one({'_id': id_eliminar})
        print(f"   ✅ Eliminada cita: {id_eliminar}")

# Ahora crear el índice
db.citas.create_index(
    [('dia', 1), ('hora', 1), ('barbero', 1)],
    unique=True,
    sparse=True
)
print("\n✅ Índice único creado exitosamente")