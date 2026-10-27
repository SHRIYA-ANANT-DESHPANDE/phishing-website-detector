# Model Integration Checklist

Use this checklist to track progress on connecting the backend to the ML model.

## Pre-Implementation

- [ ] Read the full implementation plan
- [ ] Understand the current architecture
- [ ] Review model training metrics (97.38% accuracy with Random Forest)
- [ ] Ensure dependencies are installed (`pip install -e .`)

## Phase 1: Model Inspection ⚙️

- [ ] Run `python inspect_model.py` to analyze the model
- [ ] Document the number of features required: `___` features
- [ ] Document feature names (if available) or note if missing
- [ ] Verify model type: Expected Random Forest Classifier
- [ ] Check output classes: Confirm 0=Safe, 1=Phishing
- [ ] Verify `predict_proba` is available for confidence scores
- [ ] Save inspection report for reference

**Expected Output:**
```
✅ Model Type: RandomForestClassifier
✅ Features Required: X
✅ Feature Names: Available/Not Available
✅ Output Classes: [0, 1] (0=Safe, 1=Phishing)
✅ Probability Support: Yes
```

## Phase 2: Feature Engineering 🔧

- [ ] Create `app/features.py` file
- [ ] Implement `URLFeatureExtractor` class
- [ ] Implement feature extraction methods:
  - [ ] Structural features (length, special chars)
  - [ ] Domain features (subdomain count, TLD)
  - [ ] Protocol features (HTTP/HTTPS)
  - [ ] Suspicious patterns (IP address, digits)
  - [ ] Entropy calculation
- [ ] Ensure features are in **exact training order**
- [ ] Test with sample URLs:
  - [ ] `https://www.google.com`
  - [ ] `http://suspicious-site123.xyz`
  - [ ] `http://192.168.1.1/login`
- [ ] Verify feature count matches model expectation
- [ ] Add type hints and docstrings

**Test Command:**
```python
from app.features import URLFeatureExtractor
features = URLFeatureExtractor.extract_features("https://google.com")
print(f"Feature count: {len(features)}")
```

## Phase 3: Model Service 🤖

- [ ] Create `app/model_service.py` file
- [ ] Implement `ModelService` class as singleton
- [ ] Implement `load_model()` method
  - [ ] Add error handling for missing file
  - [ ] Add error handling for corrupt file
  - [ ] Add logging
- [ ] Implement `is_loaded()` method
- [ ] Implement `predict()` method
  - [ ] Extract features
  - [ ] Validate feature count
  - [ ] Get prediction
  - [ ] Get confidence score
  - [ ] Format response
- [ ] Test model loading independently
- [ ] Test prediction with known URLs

**Test Command:**
```python
from app.model_service import ModelService
service = ModelService()
service.load_model(Path("models/phish_model.pkl"))
result = service.predict("https://www.google.com")
print(result)
```

## Phase 4: Route Integration 🔌

- [ ] Update `app/routes.py`
- [ ] Add startup event handler to load model
- [ ] Update `/api/predict` endpoint:
  - [ ] Remove placeholder HTTPException
  - [ ] Add model loaded check
  - [ ] Call `model_service.predict()`
  - [ ] Handle exceptions gracefully
  - [ ] Return formatted response
- [ ] Update `/api/model-status` endpoint:
  - [ ] Add real model loaded status
  - [ ] Add feature count info
  - [ ] Add model type info
- [ ] Test endpoint with curl/Postman
- [ ] Test with frontend

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

## Phase 5: Testing 🧪

### Unit Tests
- [ ] Create `tests/` directory
- [ ] Create `tests/test_features.py`
  - [ ] Test feature extraction
  - [ ] Test with edge cases
  - [ ] Test entropy calculation
- [ ] Create `tests/test_model_service.py`
  - [ ] Test model loading
  - [ ] Test prediction
  - [ ] Test error handling
- [ ] Create `tests/test_routes.py`
  - [ ] Test predict endpoint
  - [ ] Test health endpoint
  - [ ] Test model-status endpoint
- [ ] Run tests: `pytest tests/`

### Integration Tests
- [ ] Test with frontend at http://localhost:3000
- [ ] Test known safe URLs:
  - [ ] https://www.google.com
  - [ ] https://github.com
  - [ ] https://stackoverflow.com
- [ ] Test known phishing patterns:
  - [ ] URLs with IP addresses
  - [ ] URLs with suspicious TLDs
  - [ ] URLs with many hyphens/numbers
- [ ] Test edge cases:
  - [ ] Very long URLs
  - [ ] URLs with special characters
  - [ ] Non-standard ports
- [ ] Test error scenarios:
  - [ ] Invalid URL format
  - [ ] Empty URL
  - [ ] Malformed requests

### Performance Tests
- [ ] Measure average response time (target: <200ms)
- [ ] Test concurrent requests (10+ simultaneous)
- [ ] Monitor memory usage
- [ ] Test model reload after crash

## Phase 6: Configuration & Environment 📝

- [ ] Create `app/config.py` for settings
- [ ] Update `.env.example` with new variables:
  ```
  PHISHING_MODEL_PATH=models/phish_model.pkl
  MODEL_CONFIDENCE_THRESHOLD=0.5
  ```
- [ ] Add environment variable loading
- [ ] Test with different configurations
- [ ] Document configuration options

## Phase 7: Error Handling & Logging 📊

- [ ] Add logging to feature extraction
- [ ] Add logging to model loading
- [ ] Add logging to predictions (without URLs for privacy)
- [ ] Handle specific exceptions:
  - [ ] `FileNotFoundError` - model not found
  - [ ] `ValueError` - feature mismatch
  - [ ] `RuntimeError` - model not loaded
  - [ ] Generic `Exception` - unexpected errors
- [ ] Return appropriate HTTP status codes:
  - [ ] 200 - Success
  - [ ] 422 - Validation error
  - [ ] 500 - Server error
  - [ ] 503 - Model unavailable
- [ ] Test error messages in frontend

## Phase 8: Documentation 📚

- [ ] Update main `README.md`:
  - [ ] Note that predictions are now working
  - [ ] Add example requests/responses
  - [ ] Document feature list
- [ ] Update `frontend/README.md` if needed
- [ ] Add docstrings to all new functions
- [ ] Add type hints throughout
- [ ] Create API documentation examples
- [ ] Update getting started guide

## Verification Checklist ✅

Before considering the integration complete:

- [ ] Model loads successfully on startup
- [ ] `/api/health` returns 200 OK
- [ ] `/api/model-status` shows model as loaded
- [ ] `/api/predict` returns predictions
- [ ] Frontend displays results correctly
- [ ] Safe URLs show green "Safe" result
- [ ] Suspicious URLs show red "Phishing" result
- [ ] Confidence percentage displays correctly
- [ ] Error handling works for invalid URLs
- [ ] Response time is under 200ms
- [ ] No memory leaks after 100+ requests
- [ ] Backend logs are clean (no errors)
- [ ] Frontend console is clean (no errors)

## Common Issues & Solutions 🔧

### Issue: "Feature mismatch error"
**Solution:** 
- Re-run `inspect_model.py` to verify feature count
- Check feature extraction order
- Verify no features are skipped

### Issue: "Model not loading"
**Solution:**
- Check file path is correct
- Verify file is not corrupted
- Check Python version compatibility
- Ensure scikit-learn version matches training version

### Issue: "All predictions are the same class"
**Solution:**
- Check feature extraction logic
- Verify features aren't all zeros
- Check model threshold (default 0.5)
- Test with diverse URLs

### Issue: "No confidence scores"
**Solution:**
- Verify model has `predict_proba` method
- Check model type (must support probabilities)
- Ensure using correct prediction method

### Issue: "Slow predictions (>1 second)"
**Solution:**
- Profile feature extraction
- Check if model is loaded (not reloading each time)
- Optimize expensive operations (regex, entropy)
- Consider caching for repeated URLs

### Issue: "Frontend not showing results"
**Solution:**
- Check browser console for errors
- Verify CORS is configured
- Check API response format matches frontend expectations
- Test API endpoint with curl first

## Quick Reference Commands

```bash
# Inspect model
python inspect_model.py

# Start backend
uvicorn app.main:app --reload

# Start frontend
cd frontend && python -m http.server 3000

# Test API
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Run tests
pytest tests/ -v

# Check logs
tail -f logs/app.log  # if logging to file
```

## Success Criteria

Integration is complete when:
1. ✅ Model inspection shows all required info
2. ✅ Features extract correctly (count matches model)
3. ✅ Model loads without errors
4. ✅ Predictions return within 200ms
5. ✅ Frontend displays results correctly
6. ✅ Error handling works for all cases
7. ✅ Tests pass (unit + integration)
8. ✅ Documentation is updated
9. ✅ No security vulnerabilities
10. ✅ Code is clean and well-commented

## Timeline

- **Phase 1 (Inspection):** 30 minutes
- **Phase 2 (Features):** 2-3 hours
- **Phase 3 (Model Service):** 1-2 hours
- **Phase 4 (Routes):** 1 hour
- **Phase 5 (Testing):** 2-3 hours
- **Phase 6-8 (Config, Logging, Docs):** 2 hours
- **Total:** 8-11 hours

## Next Step

🚀 **START HERE:** Run the model inspection script

```bash
python inspect_model.py
```

Review the output and document the findings before proceeding to Phase 2.

---

**Questions?** Refer to the main implementation plan document for detailed explanations of each phase.
