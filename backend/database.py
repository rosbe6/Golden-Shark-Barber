from pymongo import MongoClient
from flask import current_app

class MongoDB:
    """Clase para manejar la conexión con MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def init_app(self, app):
        """Inicializar la conexión cuando Flask inicia"""
        mongo_uri = app.config.get('MONGO_URI')

        if not mongo_uri:
            raise ValueError("MONGO_URI no está configurada en .env")

        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database()

        print("✅ Conectado a MongoDB exitosamente")

        # Crear índice único parcial para prevenir double-booking
        self._crear_indice_unico()

    def get_collection(self, collection_name):
        """Obtener una colección de MongoDB"""
        return self.db[collection_name]

    def _crear_indice_unico(self):
        """Crear índice único parcial para prevenir double-booking"""
        try:
            citas_collection = self.db.citas
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
            print("✅ Índice único parcial para citas confirmadas verificado")
        except Exception as e:
            # Si el índice ya existe, no es error fatal
            if 'already exists' in str(e):
                print("✅ Índice único ya existe")
            else:
                print(f"⚠️ Error al crear índice: {str(e)}")

    def close(self):
        """Cerrar la conexión"""
        if self.client:
            self.client.close()

# Instancia global
mongodb = MongoDB()