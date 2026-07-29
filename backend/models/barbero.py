from bson import ObjectId
import bcrypt

class Barbero:
    """Modelo para el barbero"""
    
    def __init__(self, email, contraseña, nombre="Admin", tipo="barber", _id=None):
        self._id = _id or ObjectId()
        self.email = email
        self.nombre = nombre
        self.tipo = tipo  # ✅ "barber" o "skincare"
        self.contraseña_hash = self._hashear_contraseña(contraseña)
    
    def _hashear_contraseña(self, contraseña):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contraseña.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_contraseña(self, contraseña):
        return bcrypt.checkpw(contraseña.encode('utf-8'), self.contraseña_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            '_id': self._id,
            'email': self.email,
            'nombre': self.nombre,
            'tipo': self.tipo,  # ✅ NUEVO
            'contraseña_hash': self.contraseña_hash
        }
    
    @staticmethod
    def from_dict(data):
        barbero = Barbero.__new__(Barbero)
        barbero._id = data.get('_id')
        barbero.email = data.get('email')
        barbero.nombre = data.get('nombre')
        barbero.tipo = data.get('tipo', 'barber')  # ✅ NUEVO
        barbero.contraseña_hash = data.get('contraseña_hash')
        return barbero