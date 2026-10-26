# Phishing Link Detector API

FastAPI backend scaffold. The classifier is intentionally not loaded until the supplied model artifact and its expected input features are known.

## Run locally

From this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
```

Interactive API documentation is available at `/docs`.

## Endpoints

- `GET /api/health` — liveness check.
- `GET /api/model-status` — whether the configured model file exists and is loadable.
- `POST /api/predict` — accepts `{"url":"https://example.com"}` and returns the prediction once a model is configured. Until then it returns `503 model_unavailable`.

Set `PHISHING_MODEL_PATH` to the trusted model file path. Pickle/joblib files can execute code when loaded; only use an artifact from a trusted source. The model's feature contract (feature names/order and output labels) must be confirmed before predictions can be enabled.
