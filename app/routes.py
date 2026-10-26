from pathlib import Path
import os

from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

router = APIRouter()
MODEL_PATH = Path(os.getenv("PHISHING_MODEL_PATH", "models/phishing_model.pkl"))


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
    """Report artifact availability without deserializing an untrusted pickle."""
    return {
        "configured": MODEL_PATH.is_file(),
        "model_path": str(MODEL_PATH),
        "loaded": False,
        "detail": "Model loading is pending the artifact and feature contract.",
    }


@router.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(request: PredictionRequest) -> PredictionResponse:
    """Prediction is deliberately gated until the model integration is supplied."""
    if not MODEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail={"code": "model_unavailable", "message": "The phishing detection model has not been installed."},
        )
    raise HTTPException(
        status_code=503,
        detail={"code": "model_integration_pending", "message": "The model file exists, but its feature and label contract must be configured before predictions are enabled."},
    )
