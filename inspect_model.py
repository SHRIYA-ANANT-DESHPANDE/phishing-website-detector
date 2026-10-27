#!/usr/bin/env python3
"""
Model Inspection Script
Analyzes the trained model to understand its requirements.
"""

import joblib
import pickle
from pathlib import Path
import sys

def inspect_model(model_path: str = "models/phish_model.pkl"):
    """Inspect the ML model to understand its structure and requirements."""
    
    print("=" * 70)
    print("PHISHING MODEL INSPECTION REPORT")
    print("=" * 70)
    print()
    
    # Check if file exists
    path = Path(model_path)
    if not path.exists():
        print(f"❌ ERROR: Model file not found at {model_path}")
        return False
    
    print(f"✅ Model file found: {model_path}")
    print(f"   File size: {path.stat().st_size:,} bytes")
    print()
    
    try:
        # Load the model
        print("Loading model...")
        model = joblib.load(model_path)
        print("✅ Model loaded successfully!")
        print()
        
        # Model type
        print("MODEL INFORMATION:")
        print("-" * 70)
        print(f"Model Type: {type(model).__module__}.{type(model).__name__}")
        print(f"Model Class: {model.__class__.__name__}")
        print()
        
        # Number of features
        if hasattr(model, 'n_features_in_'):
            print(f"Number of features expected: {model.n_features_in_}")
        else:
            print("⚠️  n_features_in_ not available (older scikit-learn version)")
        print()
        
        # Feature names (if available)
        print("FEATURE INFORMATION:")
        print("-" * 70)
        if hasattr(model, 'feature_names_in_'):
            print(f"✅ Feature names stored in model:")
            for idx, name in enumerate(model.feature_names_in_, 1):
                print(f"  {idx:2d}. {name}")
            print()
        else:
            print("⚠️  Feature names not stored in model")
            print("   You will need to extract features in the EXACT order used during training.")
            print()
        
        # Model parameters
        print("MODEL PARAMETERS:")
        print("-" * 70)
        if hasattr(model, 'get_params'):
            params = model.get_params()
            for key, value in sorted(params.items())[:10]:  # Show first 10
                print(f"  {key}: {value}")
            if len(params) > 10:
                print(f"  ... and {len(params) - 10} more parameters")
        print()
        
        # Classes (for classification)
        print("OUTPUT INFORMATION:")
        print("-" * 70)
        if hasattr(model, 'classes_'):
            print(f"Number of classes: {len(model.classes_)}")
            print(f"Class labels: {model.classes_}")
            print()
            print("Interpretation:")
            for idx, label in enumerate(model.classes_):
                interpretation = "PHISHING" if label == 1 else "SAFE"
                print(f"  {label} → {interpretation}")
        else:
            print("⚠️  Class information not available")
        print()
        
        # Prediction methods
        print("AVAILABLE METHODS:")
        print("-" * 70)
        methods = ['predict', 'predict_proba', 'predict_log_proba', 'decision_function']
        for method in methods:
            if hasattr(model, method):
                print(f"  ✅ {method}()")
            else:
                print(f"  ❌ {method}() - not available")
        print()
        
        # Tree-based model specific info
        if hasattr(model, 'n_estimators'):
            print("ENSEMBLE MODEL INFORMATION:")
            print("-" * 70)
            print(f"Number of estimators: {model.n_estimators}")
            if hasattr(model, 'feature_importances_'):
                print(f"Feature importances available: Yes")
                if hasattr(model, 'feature_names_in_'):
                    print()
                    print("Top 10 Most Important Features:")
                    importances = list(zip(model.feature_names_in_, model.feature_importances_))
                    importances.sort(key=lambda x: x[1], reverse=True)
                    for idx, (name, importance) in enumerate(importances[:10], 1):
                        bar = "█" * int(importance * 50)
                        print(f"  {idx:2d}. {name:30s} {importance:.4f} {bar}")
            print()
        
        # Test prediction (dry run)
        print("TEST PREDICTION:")
        print("-" * 70)
        if hasattr(model, 'n_features_in_'):
            # Create dummy feature vector
            import numpy as np
            test_features = np.zeros((1, model.n_features_in_))
            
            try:
                prediction = model.predict(test_features)
                print(f"✅ Test prediction successful: {prediction[0]}")
                
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(test_features)
                    print(f"✅ Test probability prediction successful")
                    print(f"   Probabilities: {probabilities[0]}")
                    print(f"   Confidence: {max(probabilities[0]):.2%}")
                
                print()
                print("✅ Model is ready for integration!")
                
            except Exception as e:
                print(f"❌ Test prediction failed: {e}")
                return False
        
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✅ Model Type: {model.__class__.__name__}")
        if hasattr(model, 'n_features_in_'):
            print(f"✅ Features Required: {model.n_features_in_}")
        if hasattr(model, 'feature_names_in_'):
            print(f"✅ Feature Names: Available ({len(model.feature_names_in_)} features)")
        else:
            print(f"⚠️  Feature Names: Not available - must use exact training order")
        if hasattr(model, 'classes_'):
            print(f"✅ Output Classes: {model.classes_} (0=Safe, 1=Phishing)")
        print(f"✅ Probability Support: {'Yes' if hasattr(model, 'predict_proba') else 'No'}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    model_path = sys.argv[1] if len(sys.argv) > 1 else "models/phish_model.pkl"
    success = inspect_model(model_path)
    sys.exit(0 if success else 1)
