# TODO List for AI Background Remover - Render Deployment Fixes

## Backend Restructuring
- [x] Move app.py from backend/ to root directory
- [x] Move requirements.txt from backend/ to root directory
- [x] Update app.py paths for template_folder and static_folder (now relative to root)
- [x] Adjust logging directory for production (use /tmp/logs on Render)

## Frontend Fixes
- [x] Update logic.js to use relative URL '/remove' instead of configurable backend URL

## Testing Fixes
- [x] Fix test_backend.py: health endpoint is '/health', not '/'
- [x] Update import in test_backend.py to 'from app import app'

## Deployment Files
- [x] Update Dockerfile to copy app.py and requirements.txt from root
- [x] Add Procfile for Render (non-Docker deployment)
- [x] Update README.md with Render-specific deployment instructions

## Performance Optimizations
- [x] Pre-load rembg session at startup to avoid 502 errors
- [x] Add build.sh script to pre-download model during build
- [x] Optimize Gunicorn config with proper timeouts (120s)
- [x] Add memory monitoring with psutil

## Documentation
- [x] Update README with Render deployment steps
- [x] Update local run instructions to use root files
- [x] Add API endpoint documentation
- [x] Document security features and supported formats

## Code Quality
- [x] Add comprehensive docstrings and comments
- [x] Improve error handling and logging
- [x] Rename variables for clarity (ALLOWED -> ALLOWED_EXTENSIONS)
- [x] Add type hints and better variable naming

## Backend Fixes for 502 Errors
- [x] Move rembg session initialization from lazy loading to app startup in app.py
- [x] Add error handling and logging for session initialization
- [x] Add memory usage logging after session initialization
- [x] Test changes locally to ensure no regressions

## Deployment and Monitoring
- [x] Deploy updated code to Render
- [x] Monitor Render logs for initialization success and memory usage
- [x] Verify /remove endpoint and static file serving work without 502 errors
