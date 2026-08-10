from flask import Blueprint, request, jsonify
import os
import requests
from datetime import datetime
from bson import ObjectId
from database import mongodb

telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')

def get_bot_token():
    return os.getenv('TELEGRAM_BOT_TOKEN')

def enviar_respuesta(chat_id, texto, botones=None):
    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML"
    }
    if botones:
        payload["reply_markup"] = {"inline_keyboard": botones}
    requests.post(url, json=payload)

def responder_callback(callback_query_id, texto=""):
    """Confirma que se recibió el click del botón (evita el 'loading' infinito)"""
    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    requests.post(url, json={
        "callback_query_id": callback_query_id,
        "text": texto
    })

def editar_mensaje(chat_id, message_id, texto):
    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    requests.post(url, json={
        "chat_id": chat_id,
        "message_id": message_id,
        "text": texto,
        "parse_mode": "HTML"
    })

def es_admin(chat_id):
    admin_chat_id = os.getenv('TELEGRAM_CHAT_ID_ADMIN')
    return str(chat_id) == str(admin_chat_id)

def convertir_fecha(fecha_str):
    """Convierte MM/DD/YYYY a YYYY-MM-DD. Retorna None si es inválida."""
    try:
        fecha = datetime.strptime(fecha_str, '%m/%d/%Y')
        return fecha.strftime('%Y-%m-%d')
    except ValueError:
        return None


@telegram_bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Recibe updates de Telegram (comandos y clicks de botones)"""
    try:
        data = request.get_json()

        # ==================== CLICK EN BOTÓN ====================
        if 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            callback_id = callback['id']
            callback_data = callback['data']  # formato: "block|FECHA|BARBERO_ID_o_ALL"

            if not es_admin(chat_id):
                responder_callback(callback_id, "⛔ Not authorized")
                return jsonify({'ok': True}), 200

            partes = callback_data.split('|')
            accion = partes[0]

            if accion == 'block':
                fecha = partes[1]
                barbero_id = partes[2] if partes[2] != 'ALL' else None

                coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')

                if barbero_id is None:
                    nombre_display = "Whole Barbershop"
                else:
                    coleccion_barbero = mongodb.get_collection('barbero')
                    barbero = coleccion_barbero.find_one({'_id': ObjectId(barbero_id)})
                    nombre_display = barbero['nombre'] if barbero else 'Unknown'

                existe = coleccion_bloqueos.find_one({'fecha': fecha, 'barbero_id': barbero_id})
                if existe:
                    responder_callback(callback_id, f"⚠️ Already blocked")
                    editar_mensaje(chat_id, message_id, f"⚠️ <b>{fecha}</b> was already blocked for <b>{nombre_display}</b>.")
                else:
                    coleccion_bloqueos.insert_one({
                        'fecha': fecha,
                        'barbero_id': barbero_id,
                        'nombre_display': nombre_display,
                        'creado_en': datetime.now().isoformat()
                    })
                    responder_callback(callback_id, "✅ Blocked!")
                    editar_mensaje(chat_id, message_id, f"✅ <b>{fecha}</b> blocked for <b>{nombre_display}</b>.")

            return jsonify({'ok': True}), 200

        # ==================== MENSAJE DE TEXTO ====================
        if 'message' not in data:
            return jsonify({'ok': True}), 200

        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        username = message['chat'].get('username', 'No username')
        first_name = message['chat'].get('first_name', '')

        # ==================== /start ====================
        if text == '/start':
            respuesta = "🦈 Welcome to Golden Shark Barber Bot!\n\nSend /me to get your Chat ID and start receiving appointment notifications."
            enviar_respuesta(chat_id, respuesta)

        # ==================== /me ====================
        elif text == '/me':
            respuesta = f"""👋 Hi {first_name}!

🆔 Your Chat ID: <code>{chat_id}</code>
📛 Username: @{username}

Send this Chat ID to the admin so you can start receiving appointment notifications."""
            enviar_respuesta(chat_id, respuesta)

        # ==================== /block MM/DD/YYYY ====================
        elif text.startswith('/block'):
            if not es_admin(chat_id):
                enviar_respuesta(chat_id, "⛔ Only the admin can use this command.")
                return jsonify({'ok': True}), 200

            partes = text.split()
            if len(partes) != 2:
                enviar_respuesta(chat_id, "❌ Usage: /block MM/DD/YYYY\n\nExample:\n/block 09/25/2026")
                return jsonify({'ok': True}), 200

            fecha_input = partes[1]
            fecha = convertir_fecha(fecha_input)

            if not fecha:
                enviar_respuesta(chat_id, "❌ Invalid date format. Use MM/DD/YYYY\n\nExample: /block 09/25/2026")
                return jsonify({'ok': True}), 200

            # Construir botones dinámicos con los barberos actuales
            coleccion_barbero = mongodb.get_collection('barbero')
            barberos = list(coleccion_barbero.find({}, {'nombre': 1, 'tipo': 1}))

            botones = [[{"text": "🏪 Whole Barbershop", "callback_data": f"block|{fecha}|ALL"}]]
            for b in barberos:
                emoji = "💆" if b.get('tipo') == 'skincare' else "💈"
                botones.append([{
                    "text": f"{emoji} {b['nombre']}",
                    "callback_data": f"block|{fecha}|{str(b['_id'])}"
                }])

            enviar_respuesta(chat_id, f"📅 Block <b>{fecha_input}</b> for:", botones)

        # ==================== /unblock MM/DD/YYYY ====================
        elif text.startswith('/unblock'):
            if not es_admin(chat_id):
                enviar_respuesta(chat_id, "⛔ Only the admin can use this command.")
                return jsonify({'ok': True}), 200

            partes = text.split()
            if len(partes) != 2:
                enviar_respuesta(chat_id, "❌ Usage: /unblock MM/DD/YYYY")
                return jsonify({'ok': True}), 200

            fecha = convertir_fecha(partes[1])
            if not fecha:
                enviar_respuesta(chat_id, "❌ Invalid date format. Use MM/DD/YYYY")
                return jsonify({'ok': True}), 200

            coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')
            resultado = coleccion_bloqueos.delete_many({'fecha': fecha})

            if resultado.deleted_count > 0:
                enviar_respuesta(chat_id, f"✅ All blocks removed for <b>{partes[1]}</b> ({resultado.deleted_count} removed).")
            else:
                enviar_respuesta(chat_id, f"⚠️ No blocks found for {partes[1]}.")

        # ==================== /blocked ====================
        elif text == '/blocked':
            if not es_admin(chat_id):
                enviar_respuesta(chat_id, "⛔ Only the admin can use this command.")
                return jsonify({'ok': True}), 200

            coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')
            hoy = datetime.now().strftime('%Y-%m-%d')
            bloqueos = list(coleccion_bloqueos.find({'fecha': {'$gte': hoy}}).sort('fecha', 1))

            if not bloqueos:
                enviar_respuesta(chat_id, "✅ No upcoming blocked days.")
            else:
                lineas = [f"📅 {b['fecha']} — {b['nombre_display']}" for b in bloqueos]
                respuesta = "🚫 <b>Blocked Days:</b>\n\n" + "\n".join(lineas)
                enviar_respuesta(chat_id, respuesta)

        return jsonify({'ok': True}), 200
        
    except Exception as e:
        print(f"❌ Error en webhook Telegram: {str(e)}")
        return jsonify({'ok': True}), 200