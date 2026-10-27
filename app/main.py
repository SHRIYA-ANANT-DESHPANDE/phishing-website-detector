from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import os

from app.routes import router, model_service, MODEL_PATH

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phishing Link Detector API",
    version="0.1.0",
    description="API for checking URLs against a phishing classification model.",
)

# Restrict this list to the frontend origin(s) when the UI is wired up.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Load ML model on application startup."""
    logger.info("Starting application...")
    
    if MODEL_PATH.is_file():
        logger.info(f"Loading model from {MODEL_PATH}")
        success = model_service.load_model(MODEL_PATH)
        if success:
            logger.info("✓ Model loaded successfully - predictions enabled")
        else:
            logger.warning("✗ Model failed to load - predictions disabled")
    else:
        logger.warning(f"✗ Model file not found at {MODEL_PATH} - predictions disabled")
