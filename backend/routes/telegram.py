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
    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    requests.post(url, json={
        "callback_query_id": callback_query_id,
        "text": texto
    })

def editar_mensaje(chat_id, message_id, texto, botones=None):
    bot_token = get_bot_token()
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": texto,
        "parse_mode": "HTML"
    }
    if botones:
        payload["reply_markup"] = {"inline_keyboard": botones}
    requests.post(url, json=payload)

def es_admin(chat_id):
    admin_chat_id = os.getenv('TELEGRAM_CHAT_ID_ADMIN')
    return str(chat_id) == str(admin_chat_id)

def convertir_fecha(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%m/%d/%Y')
        return fecha.strftime('%Y-%m-%d')
    except ValueError:
        return None

def formato_display(fecha_iso):
    """YYYY-MM-DD -> MM/DD/YYYY"""
    try:
        fecha = datetime.strptime(fecha_iso, '%Y-%m-%d')
        return fecha.strftime('%m/%d/%Y')
    except ValueError:
        return fecha_iso

def emoji_barbero(barbero):
    return "💆" if barbero.get('tipo') == 'skincare' else "💈"


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
            callback_data = callback['data']

            if not es_admin(chat_id):
                responder_callback(callback_id, "⛔ Not authorized")
                return jsonify({'ok': True}), 200

            partes = callback_data.split('|')
            accion = partes[0]

            # ---------- BLOCK ----------
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
                    responder_callback(callback_id, "⚠️ Already blocked")
                    editar_mensaje(chat_id, message_id, f"⚠️ <b>{formato_display(fecha)}</b> was already blocked for <b>{nombre_display}</b>.")
                else:
                    coleccion_bloqueos.insert_one({
                        'fecha': fecha,
                        'barbero_id': barbero_id,
                        'nombre_display': nombre_display,
                        'creado_en': datetime.now().isoformat()
                    })
                    responder_callback(callback_id, "✅ Blocked!")
                    editar_mensaje(chat_id, message_id, f"✅ <b>{formato_display(fecha)}</b> blocked for <b>{nombre_display}</b>.")

            # ---------- UNBLOCK (selección de entrada específica) ----------
            elif accion == 'unblock':
                fecha = partes[1]
                bloqueo_id = partes[2]

                coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')
                bloqueo = coleccion_bloqueos.find_one({'_id': ObjectId(bloqueo_id)})

                if not bloqueo:
                    responder_callback(callback_id, "⚠️ Already removed")
                    editar_mensaje(chat_id, message_id, f"⚠️ This block was already removed.")
                    return jsonify({'ok': True}), 200

                nombre_display = bloqueo['nombre_display']
                coleccion_bloqueos.delete_one({'_id': ObjectId(bloqueo_id)})

                # Verificar si quedan más bloqueos ese día para actualizar el menú
                restantes = list(coleccion_bloqueos.find({'fecha': fecha}))

                responder_callback(callback_id, "✅ Unblocked!")

                if restantes:
                    botones = []
                    for b in restantes:
                        emoji = "🏪" if b['barbero_id'] is None else "💈"
                        botones.append([{
                            "text": f"{emoji} {b['nombre_display']}",
                            "callback_data": f"unblock|{fecha}|{str(b['_id'])}"
                        }])
                    editar_mensaje(chat_id, message_id, f"✅ <b>{nombre_display}</b> unblocked.\n\n📅 {formato_display(fecha)} is still blocked for:", botones)
                else:
                    editar_mensaje(chat_id, message_id, f"✅ <b>{formato_display(fecha)}</b> is now fully unblocked. No more blocks for that day.")

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

            coleccion_barbero = mongodb.get_collection('barbero')
            barberos = list(coleccion_barbero.find({}, {'nombre': 1, 'tipo': 1}))

            botones = [[{"text": "🏪 Whole Barbershop", "callback_data": f"block|{fecha}|ALL"}]]
            for b in barberos:
                botones.append([{
                    "text": f"{emoji_barbero(b)} {b['nombre']}",
                    "callback_data": f"block|{fecha}|{str(b['_id'])}"
                }])

            enviar_respuesta(chat_id, f"📅 Block <b>{fecha_input}</b> for:", botones)

        # ==================== /unblock MM/DD/YYYY (con menú) ====================
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
            bloqueos = list(coleccion_bloqueos.find({'fecha': fecha}))

            if not bloqueos:
                enviar_respuesta(chat_id, f"✅ {partes[1]} has no blocks.")
                return jsonify({'ok': True}), 200

            botones = []
            for b in bloqueos:
                emoji = "🏪" if b['barbero_id'] is None else "💈"
                botones.append([{
                    "text": f"{emoji} {b['nombre_display']}",
                    "callback_data": f"unblock|{fecha}|{str(b['_id'])}"
                }])

            enviar_respuesta(chat_id, f"📅 <b>{partes[1]}</b> is blocked for:", botones)

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
                lineas = [f"📅 {formato_display(b['fecha'])} — {b['nombre_display']}" for b in bloqueos]
                respuesta = "🚫 <b>Blocked Days:</b>\n\n" + "\n".join(lineas)
                enviar_respuesta(chat_id, respuesta)

        return jsonify({'ok': True}), 200
        
    except Exception as e:
        print(f"❌ Error en webhook Telegram: {str(e)}")
        return jsonify({'ok': True}), 200