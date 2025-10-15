# TODO List for Render Deployment Fixes

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

## Documentation
- [x] Update README with Render deployment steps
- [x] Update local run instructions to use root files
