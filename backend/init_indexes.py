"""
Script para inicializar los índices necesarios en MongoDB
Ejecutar esto una sola vez al setup inicial de la BD
"""
from pymongo import MongoClient
from config import Config
import os

def crear_indice_unico():
    """Crear índice único parcial para prevenir double-booking"""

    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise ValueError("MONGO_URI no está configurada en .env")

    client = MongoClient(mongo_uri)
    db = client.get_database()
    citas_collection = db.citas

    # Crear índice único PARCIAL solo para citas confirmadas
    # Esto previene que dos citas confirmadas tengan el mismo (día, hora, barbero)
    try:
        citas_collection.create_index(
            [
                ('dia', 1),
                ('hora', 1),
                ('barbero', 1)
            ],
            unique=True,
            partialFilterExpression={'estado': 'confirmada'},
            name='unique_confirmed_appointment'
        )
        print("✅ Índice único parcial creado exitosamente")
        print("   Campo: (dia, hora, barbero)")
        print("   Condición: estado = 'confirmada'")
    except Exception as e:
        print(f"❌ Error al crear índice: {str(e)}")
        # Si el índice ya existe, no es un error fatal
        if 'already exists with a different name' in str(e):
            print("   (El índice probablemente ya existe)")
    finally:
        client.close()

if __name__ == '__main__':
    crear_indice_unico()
