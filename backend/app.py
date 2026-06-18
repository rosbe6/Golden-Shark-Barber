from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from database import mongodb
from routes.autenticacion import auth_bp
from routes.citas import citas_bp
from routes.dashboard import dashboard_bp
import os

# Crear la aplicación Flask
app = Flask(__name__, static_folder='static', static_url_path='')

# Cargar configuración
app.config.from_object(Config)

# Habilitar CORS
CORS(app)

# Inicializar MongoDB
mongodb.init_app(app)

# Registrar blueprints
app.register_blueprint(citas_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

# ==================== RUTAS ESTÁTICAS ====================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/images'),
        'favicon.ico',
        mimetype='image/x-icon'
    )

@app.route('/')
def home():
    """Servir index.html por defecto"""
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos (HTML, CSS, JS)"""
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

# ==================== API TEST ====================

@app.route('/api/test', methods=['GET'])
def test():
    """Ruta de prueba"""
    return jsonify({
        'mensaje': 'Backend is working!',
        'status': 'success'
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)