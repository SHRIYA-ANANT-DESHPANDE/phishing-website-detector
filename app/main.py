from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

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
