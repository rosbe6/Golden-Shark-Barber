from bson import ObjectId

class Cliente:
    """Modelo para los clientes"""
    
    def __init__(self, nombre, email, telefono, _id=None):
        self._id = _id or ObjectId()
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.historial_citas = []  # Lista de IDs de citas
    
    def to_dict(self):
        """Convertir a diccionario para guardar en MongoDB"""
        return {
            '_id': self._id,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'historial_citas': self.historial_citas
        }
    
    @staticmethod
    def from_dict(data):
        """Crear un objeto Cliente desde un diccionario"""
        cliente = Cliente(
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            _id=data.get('_id')
        )
        cliente.historial_citas = data.get('historial_citas', [])
        return cliente