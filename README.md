# AI Background Remover

## Overview

This project provides an AI-powered background remover with a Flask backend and a simple frontend UI.

## Deployment

### Environment Variables

- `FLASK_DEBUG`: Set to `true` to enable debug mode (default: `false`).
- `PORT`: Port number for the backend server (default: `5000`).
- `BACKEND_URL`: URL of the backend server for the frontend (default: `http://localhost:5000`).

### Running Locally

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run the backend server:

```bash
export FLASK_DEBUG=false
export PORT=5000
python backend/app.py
```

4. Open `frontend/index.html` in a browser.

### Using Docker

Build the Docker image:

```bash
docker build -t ai-bg-remover .
```

Run the container:

```bash
docker run -p 5000:5000 ai-bg-remover
```

### Testing

Run backend tests with pytest:

```bash
pytest tests/
```

## Notes

- The backend includes rate limiting to prevent abuse.
- Security headers are set for improved security.
- Frontend backend URL is configurable via `window.BACKEND_URL` variable.
- Max upload size is 10MB.
- Supported image formats: PNG, JPG, JPEG, WEBP.
