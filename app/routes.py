from pathlib import Path
import os
import logging

from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.model_service import ModelService

logger = logging.getLogger(__name__)
router = APIRouter()
MODEL_PATH = Path(os.getenv("PHISHING_MODEL_PATH", "models/phish_model.pkl"))

# Initialize model service
model_service = ModelService()


class PredictionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    url: AnyHttpUrl = Field(..., description="Absolute HTTP or HTTPS URL to inspect")


class PredictionResponse(BaseModel):
    url: str
    prediction: str
    is_phishing: bool
    confidence: float | None = None


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/model-status", tags=["system"])
def model_status() -> dict[str, object]:
    """Report model availability and status."""
    return {
        "configured": MODEL_PATH.is_file(),
        "model_path": str(MODEL_PATH),
        "loaded": model_service.is_loaded(),
        "detail": "Model is loaded and ready" if model_service.is_loaded() else "Model not loaded",
    }


@router.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(request: PredictionRequest) -> PredictionResponse:
    """Predict if a URL is a phishing link."""
    if not MODEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail={"code": "model_unavailable", "message": "The phishing detection model has not been installed."},
        )
    
    if not model_service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail={"code": "model_not_loaded", "message": "The model file exists but failed to load."},
        )
    
    try:
        result = model_service.predict(str(request.url))
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "prediction_error", "message": "An error occurred during prediction."},
        )
