# Phishing Link Detector

A full-stack web application for detecting phishing URLs using machine learning. Includes a FastAPI backend and a responsive, accessible frontend interface.

## Project Structure

```
phishing-link-detector/
├── app/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── routes.py          # API endpoints
│   └── __init__.py
├── frontend/              # Web interface
│   ├── index.html         # Main page
│   ├── styles.css         # Styling
│   ├── app.js            # Application logic
│   ├── config.js         # Configuration
│   └── README.md         # Frontend documentation
├── models/               # ML models
│   └── phish_model.pkl
└── README.md            # This file
```

## Quick Start

### 1. Start the Backend

From this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. Interactive API documentation is at http://localhost:8000/docs.

### 2. Start the Frontend

From a new terminal:

```powershell
cd frontend
python -m http.server 3000
```

Open your browser to http://localhost:3000.

## API Endpoints

- `GET /api/health` — Backend health check
- `GET /api/model-status` — Model availability status
- `POST /api/predict` — URL phishing detection
  - Request: `{"url": "https://example.com"}`
  - Response: `{"url": "...", "prediction": "...", "is_phishing": bool, "confidence": float}`

## Frontend Features

- ✅ Real-time backend connectivity monitoring
- 🔍 URL validation (requires complete HTTP/HTTPS URLs)
- 🎨 Responsive design (mobile, tablet, desktop)
- ♿ WCAG accessible with ARIA labels
- 📊 Visual confidence display
- ⚡ Loading states and error handling

## Configuration

### Backend

Set `PHISHING_MODEL_PATH` environment variable to specify model location:

```powershell
$env:PHISHING_MODEL_PATH = "models/phishing_model.pkl"
```

**Security:** Pickle/joblib files can execute code when loaded. Only use model files from trusted sources.

### Frontend

Edit `frontend/config.js` to change the API endpoint:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // Change for production
    REQUEST_TIMEOUT: 10000,
    HEALTH_CHECK_INTERVAL: 30000
};
```

## Model Status

The classifier is intentionally not loaded until the model artifact and its expected input features are configured. The `/api/predict` endpoint returns `503` until the model integration is complete.

## Development

### Backend Development

```powershell
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

Use any static server. For live reload during development:

```powershell
# Using Python
cd frontend
python -m http.server 3000

# Or using Node.js
npx serve -p 3000

# Or VS Code Live Server extension
```

## Production Deployment

### Backend

1. Set production environment variables
2. Use a production ASGI server (gunicorn with uvicorn workers)
3. Update CORS origins in `app/main.py` to restrict to your frontend domain

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

### Frontend

1. Update `frontend/config.js` with production API URL
2. Deploy to static hosting (Netlify, Vercel, GitHub Pages, etc.)
3. All files in the `frontend/` directory are required

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### CORS Errors

Ensure the backend's CORS middleware includes your frontend origin. The default configuration allows all origins (`*`) for development.

### Backend Not Reachable

1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check firewall settings
3. Verify the API_BASE_URL in `frontend/config.js`

### Model Not Available

The `/api/predict` endpoint returns 503 until model integration is complete. Check `/api/model-status` for model file availability.

## Documentation

- Frontend documentation: `frontend/README.md`
- API documentation: http://localhost:8000/docs (when backend is running)

## License

[Your License Here]
