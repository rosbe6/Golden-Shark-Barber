from bson import ObjectId
import bcrypt

class Barbero:
    def __init__(self, email, contraseña, nombre="Admin", tipo="barber", telefono="", foto="", _id=None):
        self._id = _id or ObjectId()
        self.email = email
        self.nombre = nombre
        self.tipo = tipo
        self.telefono = telefono
        self.foto = foto  # ✅ NUEVO - URL relativa a la foto
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
            'tipo': self.tipo,
            'telefono': self.telefono,
            'foto': self.foto,
            'contraseña_hash': self.contraseña_hash
        }
    
    @staticmethod
    def from_dict(data):
        barbero = Barbero.__new__(Barbero)
        barbero._id = data.get('_id')
        barbero.email = data.get('email')
        barbero.nombre = data.get('nombre')
        barbero.tipo = data.get('tipo', 'barber')
        barbero.telefono = data.get('telefono', '')
        barbero.foto = data.get('foto', '')
        barbero.contraseña_hash = data.get('contraseña_hash')
        return barbero