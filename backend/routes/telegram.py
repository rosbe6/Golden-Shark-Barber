from flask import Blueprint, request, jsonify
import os
import requests
from datetime import datetime
from bson import ObjectId
from database import mongodb

telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')


# ==================== HELPERS ====================

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
    """MM/DD/YYYY -> YYYY-MM-DD"""
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

def formato_citas_lista(citas):
    """Formatea una lista de citas para mostrar en Telegram"""
    if not citas:
        return "📭 No appointments found."
    
    lineas = []
    for c in sorted(citas, key=lambda x: x['hora']):
        estado_emoji = "✅" if c.get('estado') == 'completada' else "⏳"
        lineas.append(
            f"{estado_emoji} <b>{c['hora']}</b> — {c['cliente_nombre']}\n"
            f"   {c['servicio']} · ${c['precio']} · {c.get('barbero_nombre', 'N/A')}\n"
            f"   🆔 <code>{str(c['_id'])[-6:].upper()}</code>"
        )
    return "\n\n".join(lineas)


# ==================== WEBHOOK ====================

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

            # ---------- UNBLOCK ----------
            elif accion == 'unblock':
                fecha = partes[1]
                bloqueo_id = partes[2]

                coleccion_bloqueos = mongodb.get_collection('dias_bloqueados')
                bloqueo = coleccion_bloqueos.find_one({'_id': ObjectId(bloqueo_id)})

                if not bloqueo:
                    responder_callback(callback_id, "⚠️ Already removed")
                    editar_mensaje(chat_id, message_id, "⚠️ This block was already removed.")
                    return jsonify({'ok': True}), 200

                nombre_display = bloqueo['nombre_display']
                coleccion_bloqueos.delete_one({'_id': ObjectId(bloqueo_id)})

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

            # ---------- TODAY MENU (nivel 1: elegir tipo) ----------
            elif accion == 'todaymenu':
                tipo = partes[1]

                if tipo == 'back':
                    botones = [
                        [{"text": "💈 Barbers", "callback_data": "todaymenu|barber"}],
                        [{"text": "💆 Skincare", "callback_data": "todaymenu|skincare"}]
                    ]
                    responder_callback(callback_id, "")
                    editar_mensaje(chat_id, message_id, "📅 Today's appointments — filter by:", botones)
                else:
                    coleccion_barbero = mongodb.get_collection('barbero')
                    barberos = list(coleccion_barbero.find({'tipo': tipo}, {'nombre': 1, 'tipo': 1}))

                    titulo = "Barbers" if tipo == 'barber' else "Skincare"
                    emoji_titulo = "💈" if tipo == 'barber' else "💆"

                    botones = [[{"text": f"🏪 All {titulo}", "callback_data": f"today|all{tipo}"}]]
                    for b in barberos:
                        botones.append([{
                            "text": f"{emoji_titulo} {b['nombre']}",
                            "callback_data": f"today|{str(b['_id'])}"
                        }])
                    botones.append([{"text": "⬅️ Back", "callback_data": "todaymenu|back"}])

                    responder_callback(callback_id, "")
                    editar_mensaje(chat_id, message_id, f"📅 Today's appointments — {titulo}:", botones)

            # ---------- TODAY FILTER (nivel 2: mostrar citas) ----------
            elif accion == 'today':
                filtro = partes[1]

                coleccion_citas = mongodb.get_collection('citas')
                coleccion_barbero = mongodb.get_collection('barbero')
                hoy = datetime.now().strftime('%Y-%m-%d')

                query = {'dia': hoy, 'estado': {'$ne': 'cancelada'}}
                titulo = "All Appointments"

                if filtro == 'allbarber':
                    barberos_tipo = list(coleccion_barbero.find({'tipo': 'barber'}, {'_id': 1}))
                    ids = [str(b['_id']) for b in barberos_tipo]
                    query['barbero_id'] = {'$in': ids}
                    titulo = "All Barbers"
                elif filtro == 'allskincare':
                    barberos_tipo = list(coleccion_barbero.find({'tipo': 'skincare'}, {'_id': 1}))
                    ids = [str(b['_id']) for b in barberos_tipo]
                    query['barbero_id'] = {'$in': ids}
                    titulo = "All Skincare"
                else:
                    query['barbero_id'] = filtro
                    barbero = coleccion_barbero.find_one({'_id': ObjectId(filtro)})
                    titulo = barbero['nombre'] if barbero else 'Unknown'

                citas = list(coleccion_citas.find(query))

                for c in citas:
                    try:
                        b = coleccion_barbero.find_one({'_id': ObjectId(c['barbero_id'])})
                        c['barbero_nombre'] = b['nombre'] if b else 'N/A'
                    except:
                        c['barbero_nombre'] = 'N/A'

                responder_callback(callback_id, "")
                respuesta = f"📅 <b>Today — {titulo}</b> ({hoy})\n\n" + formato_citas_lista(citas)
                editar_mensaje(chat_id, message_id, respuesta)

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
            respuesta = "🦈 Welcome to Golden Shark Barber Bot!\n\nSend /help to see all available commands."
            enviar_respuesta(chat_id, respuesta)

        # ==================== /me ====================
        elif text == '/me':
            respuesta = f"""👋 Hi {first_name}!

🆔 Your Chat ID: <code>{chat_id}</code>
📛 Username: @{username}

Send this Chat ID to the admin so you can start receiving appointment notifications."""
            enviar_respuesta(chat_id, respuesta)

        # ==================== /help ====================
        elif text == '/help':
            respuesta = """🦈 <b>Golden Shark Barber Bot — Commands</b>

<b>📋 General</b>
/me — Get your Chat ID
/help — Show this menu

<b>📅 Appointments</b>
/today — View today's appointments (filter by barber/type)

<b>🚫 Blocking Days</b> (admin only)
/block MM/DD/YYYY — Block a date
/unblock MM/DD/YYYY — Unblock a date
/blocked — List all upcoming blocked days

<i>Example: /block 09/25/2026</i>"""
            enviar_respuesta(chat_id, respuesta)

        # ==================== /today ====================
        elif text == '/today':
            botones = [
                [{"text": "💈 Barbers", "callback_data": "todaymenu|barber"}],
                [{"text": "💆 Skincare", "callback_data": "todaymenu|skincare"}]
            ]
            enviar_respuesta(chat_id, "📅 Today's appointments — filter by:", botones)

        # ==================== /block MM/DD/YYYY ====================
        elif text.startswith('/block '):
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