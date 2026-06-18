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
        
        # ✅ CREAR ÍNDICE ÚNICO para prevenir double-booking
        try:
            self.db.citas.create_index(
                [('dia', 1), ('hora', 1), ('barbero', 1)],
                unique=True
            )
            print("✅ Índice único creado para prevenir double-booking")
        except Exception as e:
            print(f"⚠️ Índice ya existe o error: {e}")
        
        print("✅ Conectado a MongoDB exitosamente")

    def get_collection(self, collection_name):
        """Obtener una colección de MongoDB"""
        return self.db[collection_name]
    
    def close(self):
        """Cerrar la conexión"""
        if self.client:
            self.client.close()

# Instancia global
mongodb = MongoDB()