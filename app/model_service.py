"""ML model service for phishing detection."""

import joblib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

from app.features import URLFeatureExtractor

logger = logging.getLogger(__name__)


class ModelService:
    """Singleton service for ML model operations."""
    
    _instance = None
    _model = None
    _is_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.feature_extractor = URLFeatureExtractor(fetch_html=True, timeout=5)
            self.confidence_threshold = 0.5
            self.initialized = True
    
    def load_model(self, model_path: Path) -> bool:
        """Load model from disk."""
        try:
            if not model_path.exists():
                logger.error(f"Model file not found: {model_path}")
                return False
            
            logger.info(f"Loading model from {model_path}")
            loaded = joblib.load(model_path)
            
            # Handle if the pickle is a dict containing the model
            if isinstance(loaded, dict):
                logger.info("Model is stored in a dictionary, extracting...")
                # Try common keys
                if 'model' in loaded:
                    self._model = loaded['model']
                elif 'classifier' in loaded:
                    self._model = loaded['classifier']
                elif 'estimator' in loaded:
                    self._model = loaded['estimator']
                else:
                    # Take the first value that looks like a model
                    for key, value in loaded.items():
                        if hasattr(value, 'predict'):
                            logger.info(f"Found model under key: '{key}'")
                            self._model = value
                            break
                    if self._model is None:
                        logger.error(f"Could not find model in dict. Keys: {list(loaded.keys())}")
                        return False
            else:
                self._model = loaded
            
            self._is_loaded = True
            
            logger.info(f"Model loaded successfully: {type(self._model).__name__}")
            if hasattr(self._model, 'n_features_in_'):
                logger.info(f"Features expected: {self._model.n_features_in_}")
            else:
                logger.warning("Model does not have n_features_in_ attribute")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self._is_loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded and self._model is not None
    
    def predict(self, url: str) -> Dict[str, Any]:
        """Predict if URL is phishing."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")
        
        try:
            # Extract features
            features = self.feature_extractor.extract_features(url)
            
            # Validate feature count if model has the attribute
            if hasattr(self._model, 'n_features_in_'):
                expected_features = self._model.n_features_in_
                if len(features) != expected_features:
                    # If we have more features than model expects, trim
                    if len(features) > expected_features:
                        logger.warning(f"Trimming features from {len(features)} to {expected_features}")
                        features = features[:expected_features]
                    # If we have fewer features, pad with zeros
                    else:
                        logger.warning(f"Padding features from {len(features)} to {expected_features}")
                        features.extend([0.0] * (expected_features - len(features)))
            
            # Convert to numpy array with proper shape
            features_array = np.array([features])
            
            # Get prediction
            prediction = self._model.predict(features_array)[0]
            
            # Get probability if available
            confidence = None
            if hasattr(self._model, 'predict_proba'):
                probabilities = self._model.predict_proba(features_array)[0]
                # Confidence is the probability of the predicted class
                confidence = float(probabilities[int(prediction)])
            
            # Format result
            # UCI dataset uses: -1 = phishing, 1 = legitimate
            is_phishing = bool(prediction == -1)
            prediction_label = "phishing" if is_phishing else "safe"
            
            logger.info(f"Prediction: {prediction_label} (confidence: {confidence})")
            
            return {
                "url": url,
                "prediction": prediction_label,
                "is_phishing": is_phishing,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Prediction error for URL: {e}", exc_info=True)
            raise
