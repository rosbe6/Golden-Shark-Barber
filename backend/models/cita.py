from bson.objectid import ObjectId
from datetime import datetime

class Cita:
    def __init__(self, cliente_nombre, cliente_email, cliente_telefono, dia, hora, servicio, 
                 metodoPago='cash', precio=45, instrucciones='', barbero_id=None):
        self.cliente_nombre = cliente_nombre
        self.cliente_email = cliente_email
        self.cliente_telefono = cliente_telefono
        self.dia = dia
        self.hora = hora
        self.servicio = servicio
        self.metodoPago = metodoPago
        self.precio = precio
        self.instrucciones = instrucciones
        self.barbero_id = barbero_id  # ← NUEVO
        self.estado = 'confirmada'
        self.fecha_creacion = datetime.now()

    def to_dict(self):
        return {
            'cliente_nombre': self.cliente_nombre,
            'cliente_email': self.cliente_email,
            'cliente_telefono': self.cliente_telefono,
            'dia': self.dia,
            'hora': self.hora,
            'servicio': self.servicio,
            'metodoPago': self.metodoPago,
            'precio': self.precio,
            'instrucciones': self.instrucciones,
            'barbero_id': self.barbero_id,  # ← NUEVO
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion
        }

    @staticmethod
    def from_dict(data):
        cita = Cita(
            cliente_nombre=data.get('cliente_nombre', ''),
            cliente_email=data.get('cliente_email', ''),
            cliente_telefono=data.get('cliente_telefono', ''),
            dia=data.get('dia', ''),
            hora=data.get('hora', ''),
            servicio=data.get('servicio', ''),
            metodoPago=data.get('metodoPago', 'cash'),
            precio=data.get('precio', 45),
            instrucciones=data.get('instrucciones', ''),
            barbero=data.get('barbero', 'Rosbin')
        )
        return cita