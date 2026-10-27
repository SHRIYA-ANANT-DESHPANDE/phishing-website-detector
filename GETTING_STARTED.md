# Getting Started with Phishing Link Detector

This guide will help you get the Phishing Link Detector up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- A modern web browser (Chrome, Firefox, Safari, or Edge)

## Step-by-Step Setup

### Step 1: Clone and Navigate

```powershell
cd c:\Projects\phishing-link-detector
```

### Step 2: Set Up Python Environment

```powershell
# Create virtual environment
py -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

### Step 3: Start the Backend

```powershell
# Start the FastAPI server
uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**Keep this terminal running!**

### Step 4: Verify Backend is Working

Open a new terminal and test the health endpoint:

```powershell
curl http://localhost:8000/api/health
```

You should see: `{"status":"ok"}`

Or open http://localhost:8000/docs in your browser to see the interactive API documentation.

### Step 5: Start the Frontend

Open a **new terminal** (don't close the backend):

```powershell
cd c:\Projects\phishing-link-detector\frontend
python -m http.server 3000
```

You should see:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

### Step 6: Open the Application

Open your browser and go to:

**http://localhost:3000**

You should see the Phishing Link Detector interface with a green "Backend connected and ready" banner at the top.

## Using the Application

1. **Enter a URL** - Type a complete URL including `http://` or `https://`
   - ✅ Example: `https://www.google.com`
   - ✅ Example: `http://suspicious-site.com`
   - ❌ Wrong: `google.com` (missing protocol)

2. **Click "Check URL"** - The button will show a loading spinner while checking

3. **View Results** - You'll see:
   - Whether the URL is safe or a phishing link
   - The prediction confidence (if available)
   - A clear visual indication (green for safe, red for phishing)

## Current Limitations

The model integration is not yet complete, so the `/api/predict` endpoint will return a 503 error:

```
"The model file exists, but its feature and label contract must be configured before predictions are enabled."
```

This is expected! The frontend is fully functional and will display this error message clearly.

## Testing the Frontend

Even though predictions aren't working yet, you can test the frontend features:

### ✅ Backend Health Check
- The status banner at the top should show "Backend connected and ready" in green
- Try stopping the backend (Ctrl+C) and watch it change to red
- Restart the backend and see it turn green again

### ✅ URL Validation
Try these invalid URLs to see validation in action:
- Empty input
- `google.com` (missing protocol)
- `htp://example.com` (typo)

### ✅ Error Handling
Submit a valid URL to see the error message from the backend (503 error)

### ✅ Responsive Design
- Resize your browser window to see the responsive layout
- Try it on mobile or tablet screen sizes

## Troubleshooting

### "Backend is not reachable"

1. Make sure the backend is running on port 8000
2. Check that you're using the correct URL: `http://localhost:8000`
3. Try accessing http://localhost:8000/api/health directly in your browser

### "CORS Error" in Browser Console

The backend already has CORS configured correctly. If you see CORS errors:
1. Make sure the backend is running
2. Clear your browser cache
3. Try a different browser

### Port Already in Use

If port 8000 or 3000 is already taken:

**For backend (port 8000):**
```powershell
uvicorn app.main:app --reload --port 8001
```
Then update `frontend/config.js`:
```javascript
API_BASE_URL: 'http://localhost:8001'
```

**For frontend (port 3000):**
```powershell
python -m http.server 8080
```
Then open http://localhost:8080

## Next Steps

Once the model integration is complete, the predict endpoint will work and you'll be able to:

1. Enter real URLs to check for phishing
2. See confidence scores for predictions
3. Get real-time phishing detection results

## Development Tips

### Auto-Reload

The backend automatically reloads when you edit Python files (thanks to `--reload` flag).

For frontend auto-reload, consider using:
- VS Code Live Server extension
- `npx live-server frontend`
- `npx browser-sync start --server frontend --files "frontend/**/*"`

### API Testing

Use the interactive docs at http://localhost:8000/docs to test the API directly.

### Viewing Logs

- Backend logs appear in the terminal running uvicorn
- Frontend errors appear in the browser console (F12 → Console tab)

## Configuration

### Changing the API URL

Edit `frontend/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // Change this
    REQUEST_TIMEOUT: 10000,                  // 10 seconds
    HEALTH_CHECK_INTERVAL: 30000            // 30 seconds
};
```

### Environment Variables

Create a `.env` file for backend configuration:

```
PHISHING_MODEL_PATH=models/phishing_model.pkl
```

## Questions or Issues?

- Check the main `README.md` for detailed documentation
- Check `frontend/README.md` for frontend-specific details
- Review API docs at http://localhost:8000/docs
- Check browser console for JavaScript errors
- Check terminal for backend errors

Happy phishing detection! 🔒
