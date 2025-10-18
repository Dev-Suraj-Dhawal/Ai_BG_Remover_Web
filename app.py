# AI Background Remover Web App
# Flask backend for AI-powered background removal using rembg library
# Deployed on Render with optimized configuration for production

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

# Rate limiter to prevent abuse (100 requests/hour, 10/minute for image processing)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"  # Explicitly set to suppress warning
)

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Log application startup information
app.logger.info('Application startup')
app.logger.info(f'Base directory: {BASE_DIR}')
app.logger.info(f'Template folder: {app.template_folder}')
app.logger.info(f'Static folder: {app.static_folder}')

# Global session variable for rembg model
_session = None

def initialize_session():
    """
    Initialize the rembg session with u2net model at startup.
    This prevents delays on first request and catches initialization errors early.
    """
    global _session
    try:
        app.logger.info('Initializing rembg session...')
        _session = new_session('u2net')
        app.logger.info('Session initialized successfully')

        # Log memory usage if psutil is available (for monitoring)
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            app.logger.info(f'Memory usage after session init: {memory_info.rss / 1024 / 1024:.2f} MB')
        except ImportError:
            app.logger.info('psutil not available for memory logging')
    except Exception as e:
        app.logger.error(f'Failed to initialize rembg session: {e}')
        raise

# Initialize the session at startup
initialize_session()

def get_session():
    """Get the initialized rembg session"""
    if _session is None:
        raise RuntimeError("Session not initialized")
    return _session

# Security headers middleware
@app.after_request
def set_security_headers(response):
    """
    Set security headers for all responses.
    Allows connect-src for localhost and deployed domain.
    """
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "connect-src 'self' http://localhost:* http://127.0.0.1:*; "
        "img-src 'self' data: https: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline';"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
    return response

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    app.logger.info("Health check endpoint called")
    return jsonify({'status': 'ok'})

@app.route('/remove', methods=['POST'])
@limiter.limit("10/minute")
def remove_bg():
    """
    Remove background from uploaded image using rembg.
    Rate limited to 10 requests per minute per IP.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported: PNG, JPG, JPEG, WEBP'}), 400

    # Read file data
    image_data = file.read()

    try:
        # Get the initialized session and process image
        session = get_session()
        processed_bytes = remove(image_data, session=session)

        # Set cache control header to prevent caching
        @after_this_request
        def add_header(response):
            response.headers['Cache-Control'] = 'no-store'
            return response

        # Return processed image
        return send_file(
            io.BytesIO(processed_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='no_bg.png'
        )
    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({'error': 'Failed to process image'}), 500

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
