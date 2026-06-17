from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self, token=None):
        self.service = None
        self.token = token
    
    def authenticate(self, token):
        """Autenticar con Google Calendar"""
        try:
            creds = Credentials.from_authorized_user_info(token, SCOPES)
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except:
            return False
    
    def crear_evento(self, cita_data):
        """Crear un evento en Google Calendar"""
        try:
            event = {
                'summary': f"Haircut - {cita_data['cliente_nombre']}",
                'description': f"Service: {cita_data['servicio']}\nPhone: {cita_data['cliente_telefono']}\nPayment: {cita_data['metodoPago']}\nPrice: ${cita_data['precio']}",
                'start': {
                    'dateTime': self._convertir_fecha_hora(cita_data['dia'], cita_data['hora']),
                    'timeZone': 'America/Guatemala',
                },
                'end': {
                    'dateTime': self._convertir_fecha_hora(cita_data['dia'], self._siguiente_hora(cita_data['hora'])),
                    'timeZone': 'America/Guatemala',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 horas antes
                        {'method': 'popup', 'minutes': 30},  # 30 minutos antes
                    ],
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return {'status': 'success', 'event_id': event['id']}
        except Exception as e:
            return {'status': 'error', 'mensaje': str(e)}
    
    def _convertir_fecha_hora(self, fecha, hora):
        """Convertir fecha y hora a formato ISO 8601"""
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        hora_obj = datetime.strptime(hora, '%H:%M')
        combined = fecha_obj.replace(hour=hora_obj.hour, minute=hora_obj.minute)
        return combined.isoformat()
    
    def _siguiente_hora(self, hora):
        """Calcular la hora siguiente (30 minutos después)"""
        hora_obj = datetime.strptime(hora, '%H:%M')
        siguiente = hora_obj + timedelta(minutes=30)
        return siguiente.strftime('%H:%M')