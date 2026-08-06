from flask import Blueprint, request, jsonify
import os
import requests

telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')

@telegram_bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Recibe updates de Telegram (comandos como /me)"""
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'ok': True}), 200
        
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        username = message['chat'].get('username', 'No username')
        first_name = message['chat'].get('first_name', '')
        
        if text == '/me':
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            respuesta = f"""👋 Hi {first_name}!

🆔 Your Chat ID: <code>{chat_id}</code>
📛 Username: @{username}

Send this Chat ID to the admin so you can start receiving appointment notifications."""
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": respuesta,
                "parse_mode": "HTML"
            })
        
        elif text == '/start':
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            respuesta = f"""🦈 Welcome to Golden Shark Barber Bot!

Send /me to get your Chat ID and start receiving appointment notifications."""
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": respuesta,
                "parse_mode": "HTML"
            })
        
        return jsonify({'ok': True}), 200
        
    except Exception as e:
        print(f"❌ Error en webhook Telegram: {str(e)}")
        return jsonify({'ok': True}), 200