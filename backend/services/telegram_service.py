import requests
import os
from dotenv import load_dotenv

load_dotenv()


def formatear_fecha_dd_mm_yyyy(fecha_iso):
    """2026-08-20 -> 08-20-2026"""
    try:
        year, month, day = fecha_iso.split('-')
        return f"{month}-{day}-{year}"
    except Exception:
        return fecha_iso


def formatear_hora_12h(hora_iso):
    """14:00 -> 2:00 PM"""
    try:
        horas, minutos = map(int, hora_iso.split(':'))
        periodo = 'PM' if horas >= 12 else 'AM'
        horas12 = horas % 12
        if horas12 == 0:
            horas12 = 12
        return f"{horas12}:{minutos:02d} {periodo}"
    except Exception:
        return hora_iso


class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = os.getenv('TELEGRAM_CHAT_ID_ADMIN')
        
        if not self.bot_token:
            print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        else:
            print("✅ Telegram bot configurado")
    
    def enviar_mensaje(self, chat_id, mensaje):
        """Enviar mensaje a un chat_id específico"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": mensaje,
                "parse_mode": "HTML"
            }, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram enviado a {chat_id}")
            else:
                print(f"❌ Error Telegram: {response.text}")
        except Exception as e:
            print(f"❌ Error enviando Telegram: {str(e)}")
    
    def notificar_nueva_cita(self, cita_data, cita_id):
        """Notificar al admin sobre nueva cita"""
        if not self.admin_chat_id:
            print("⚠️ TELEGRAM_CHAT_ID_ADMIN no configurado")
            return
        
        tipo_label = "💆 Specialist" if cita_data.get('tipo_servicio') == 'skincare' else "💈 Barber"
        emoji_pago = "💵" if cita_data['metodoPago'] == 'cash' else "💳"
        
        numero_cita = cita_id[-6:].upper()
        fecha_fmt = formatear_fecha_dd_mm_yyyy(cita_data['dia'])
        hora_fmt = formatear_hora_12h(cita_data['hora'])
        
        mensaje = f"""🔔 <b>NEW APPOINTMENT</b> #{numero_cita}

━━━━━━━━━━━━━━━━━━━━

👤 <b>{cita_data['cliente_nombre']}</b>
📞 {cita_data['cliente_telefono']}
✉️ {cita_data['cliente_email']}

━━━━━━━━━━━━━━━━━━━━
✂️ <b>{cita_data['servicio']}</b>
{tipo_label}: <b>{cita_data.get('barbero_nombre', 'N/A')}</b>

📅 {fecha_fmt}
⏰ {hora_fmt}
{emoji_pago} {cita_data['metodoPago'].capitalize()} — <b>${cita_data['precio']}</b>
━━━━━━━━━━━━━━━━━━━━

🔗 <a href="https://goldenbarbershop.online/dashboard.html">Open Dashboard</a>
🆔 <code>{cita_id}</code>"""
        
        self.enviar_mensaje(self.admin_chat_id, mensaje)