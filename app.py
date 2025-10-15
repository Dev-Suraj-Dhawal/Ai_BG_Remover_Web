# backend/app.py
import os
from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from rembg import remove, new_session
import io
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler

# Get the current directory (root of the project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure Flask with correct paths pointing to frontend
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'frontend'),
            static_folder=os.path.join(BASE_DIR, 'frontend'),
            static_url_path='')
CORS(app)

# Rate limiter to prevent abuse
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"  # Explicitly set to suppress warning
)

ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

def allowed_file(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in ALLOWED

# Configure logging - use /tmp/logs for production (Render), or logs in root for local
if os.environ.get('RENDER'):
    log_dir = '/tmp/logs'
else:
    log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'), 
    maxBytes=10240, 
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')
app.logger.info(f'Base directory: {BASE_DIR}')
app.logger.info(f'Template folder: {app.template_folder}')
app.logger.info(f'Static folder: {app.static_folder}')

# Initialize model session at startup to ensure app is ready for health checks
app.logger.info('Initializing rembg session...')
_session = new_session('isnet-general-use')
app.logger.info('Session initialized successfully')

def get_session():
    return _session

# Security headers
@app.after_request
def set_security_headers(response):
    # Allow connect-src for localhost and deployed domain
    response.headers['Content-Security-Policy'] = "default-src 'self'; connect-src 'self' http://localhost:* http://127.0.0.1:*; img-src 'self' data: https: blob:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
    return response

@app.route('/health')
def health():
    app.logger.info("Health check endpoint called")
    return jsonify({'status': 'ok'})

@app.route('/remove', methods=['POST'])
@limiter.limit("10/minute")
def remove_bg():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['image']
    if f.filename == '' or not allowed_file(f.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    data = f.read()
    try:
        session = get_session()
        out_bytes = remove(data, session=session)
        
        @after_this_request
        def add_header(response):
            response.headers['Cache-Control'] = 'no-store'
            return response
        
        return send_file(
            io.BytesIO(out_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='no_bg.png'
        )
    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({'error': 'Failed to process image'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)