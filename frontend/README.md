# Phishing Link Detector - Frontend

A responsive, accessible web interface for checking URLs against phishing detection.

## Features

- ✅ **Real-time Backend Health Check** - Monitors API connectivity
- 🔍 **URL Validation** - Client-side validation for proper HTTP/HTTPS URLs
- 🎨 **Responsive Design** - Works on desktop, tablet, and mobile devices
- ♿ **Accessible** - WCAG compliant with ARIA labels and keyboard navigation
- 🎯 **Clear Results** - Visual indicators for safe vs phishing URLs
- 📊 **Confidence Display** - Shows prediction confidence when available
- ⚡ **Loading States** - User-friendly feedback during API calls
- 🎭 **Error Handling** - Clear error messages for network and API issues

## Quick Start

### 1. Start the Backend

Ensure your FastAPI backend is running at `http://localhost:8000`:

```powershell
# From the project root
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Serve the Frontend

The simplest way to serve the frontend is using Python's built-in HTTP server:

```powershell
# From the frontend directory
cd frontend
python -m http.server 3000
```

Then open http://localhost:3000 in your browser.

### Alternative Serving Options

**Using Node.js:**
```bash
npx serve -p 3000
```

**Using PHP:**
```bash
php -S localhost:3000
```

**Using Live Server (VS Code Extension):**
Right-click on `index.html` and select "Open with Live Server"

## Configuration

Edit `config.js` to change the API endpoint:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',  // Change for production
    // ... other settings
};
```

### Production Configuration Example

```javascript
const CONFIG = {
    API_BASE_URL: 'https://api.yourdomain.com',
    REQUEST_TIMEOUT: 15000,
    HEALTH_CHECK_INTERVAL: 60000
};
```

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling with responsive design
├── app.js          # Application logic and API integration
├── config.js       # Configuration (API endpoint, timeouts)
└── README.md       # This file
```

## API Integration

The frontend expects these endpoints:

### GET `/api/health`
Returns backend health status.

**Response:**
```json
{
  "status": "ok"
}
```

### POST `/api/predict`
Checks a URL for phishing.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Success Response (200):**
```json
{
  "url": "https://example.com",
  "prediction": "safe",
  "is_phishing": false,
  "confidence": 0.95
}
```

**Error Response (503):**
```json
{
  "detail": {
    "code": "model_unavailable",
    "message": "The phishing detection model has not been installed."
  }
}
```

## Accessibility Features

- ✅ Semantic HTML structure
- ✅ ARIA labels and live regions
- ✅ Keyboard navigation support
- ✅ Focus indicators
- ✅ Screen reader compatible
- ✅ Reduced motion support
- ✅ Color contrast compliance

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Customization

### Changing Colors

Edit the CSS custom properties in `styles.css`:

```css
:root {
    --primary-color: #2563eb;
    --success-color: #16a34a;
    --danger-color: #dc2626;
    /* ... */
}
```

### Changing Timeouts

Edit `config.js`:

```javascript
REQUEST_TIMEOUT: 10000,        // API request timeout
HEALTH_CHECK_INTERVAL: 30000   // Health check frequency
```

## Troubleshooting

### Backend Not Connecting

1. Verify the backend is running: `curl http://localhost:8000/api/health`
2. Check the API_BASE_URL in `config.js`
3. Check browser console for CORS errors

### CORS Issues

If you see CORS errors, ensure your FastAPI backend has CORS middleware configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### URL Validation Errors

The frontend requires complete URLs with protocol:
- ✅ `https://example.com`
- ✅ `http://suspicious-site.com`
- ❌ `example.com`
- ❌ `www.example.com`

## Development

### Testing Locally

1. Start the backend on port 8000
2. Serve the frontend on port 3000
3. Open browser to http://localhost:3000
4. Open DevTools console to see logs

### Simulating Backend Errors

Stop the backend server to test:
- Connection status banner changes
- Error handling when submitting URLs
- Health check recovery when backend restarts

## Deployment

### Static Hosting (Netlify, Vercel, GitHub Pages)

1. Update `config.js` with production API URL
2. Upload all files in the `frontend` folder
3. Ensure your backend has CORS configured for your domain

### With Backend on Same Domain

If serving from the same domain, update `config.js`:

```javascript
API_BASE_URL: ''  // Empty string for same-origin requests
```

## License

Same as parent project.
