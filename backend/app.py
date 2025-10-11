# backend/app.py
import os
from flask import Flask, request, send_file, jsonify, after_this_request
from rembg import remove, new_session
import io
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)

# Rate limiter to prevent abuse
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

ALLOWED = {'png', 'jpg', 'jpeg', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

def allowed_file(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in ALLOWED

# Create a session with a more precise model
session = new_session('isnet-general-use')

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Security headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data: https:;"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
    return response

@app.route('/')
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
        # Use the session with the advanced model
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

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
