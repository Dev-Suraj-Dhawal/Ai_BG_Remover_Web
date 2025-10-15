# AI Background Remover

## Overview

This project provides an AI-powered background remover with a Flask backend and a simple frontend UI.

## Deployment

### Environment Variables

- `FLASK_DEBUG`: Set to `true` to enable debug mode (default: `false`).
- `PORT`: Port number for the backend server (default: `5000`).
- `RENDER`: Set to any value to enable production logging to `/tmp/logs` (automatically set by Render).

### Running Locally

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the backend server:

```bash
export FLASK_DEBUG=false
export PORT=5000
python app.py
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

### Deploying to Render

1. Connect your GitHub repository to Render.
2. Create a new Web Service.
3. Set the following:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python download_model.py`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Add environment variables if needed (e.g., `FLASK_DEBUG=false`).
5. Deploy!

## Notes

- The backend includes rate limiting to prevent abuse.
- Security headers are set for improved security.
- Frontend uses relative URLs for same-origin requests.
- Max upload size is 10MB.
- Supported image formats: PNG, JPG, JPEG, WEBP.
