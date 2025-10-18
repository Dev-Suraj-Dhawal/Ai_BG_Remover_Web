# Gunicorn configuration for AI Background Remover Web App
# Optimized for Render deployment with proper timeouts and resource management

import os

# Bind to the port Render assigns (default to 10000 for local testing)
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Worker configuration - Single worker for memory efficiency
workers = 1
worker_class = "sync"
worker_connections = 1000
threads = 2

# Timeouts - CRITICAL: Must be high enough for image processing (120s for large images)
timeout = 120  # Increased from default 30s to handle image processing
keepalive = 5  # Connection keep-alive duration

# Worker lifecycle - Restart workers periodically to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Load app before forking workers (critical for model caching and startup speed)
preload_app = True

# Logging configuration
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'

# Process naming for easier monitoring
proc_name = 'ai-bg-remover'
