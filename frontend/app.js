/**
 * Phishing Link Detector - Frontend Application
 */

// ============================================
// State Management
// ============================================
const state = {
    isBackendConnected: false,
    isChecking: false,
    healthCheckInterval: null
};

// ============================================
// DOM Elements
// ============================================
const elements = {
    backendStatus: document.getElementById('backendStatus'),
    statusText: document.getElementById('statusText'),
    checkForm: document.getElementById('checkForm'),
    urlInput: document.getElementById('urlInput'),
    urlError: document.getElementById('urlError'),
    checkButton: document.getElementById('checkButton'),
    resultsContainer: document.getElementById('resultsContainer'),
    resultCard: document.getElementById('resultCard'),
    resultUrl: document.getElementById('resultUrl'),
    resultPrediction: document.getElementById('resultPrediction'),
    resultConfidence: document.getElementById('resultConfidence'),
    confidenceContainer: document.getElementById('confidenceContainer'),
    confidenceProgress: document.getElementById('confidenceProgress'),
    resultDescription: document.getElementById('resultDescription'),
    errorContainer: document.getElementById('errorContainer'),
    errorMessage: document.getElementById('errorMessage')
};

// ============================================
// API Functions
// ============================================

/**
 * Check backend health status
 */
async function checkBackendHealth() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HEALTH}`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            updateBackendStatus(true, 'Backend connected and ready');
            return true;
        } else {
            updateBackendStatus(false, `Backend returned status ${response.status}`);
            return false;
        }
    } catch (error) {
        let message = 'Backend is not reachable';
        if (error.name === 'AbortError') {
            message = 'Connection timeout - backend is not responding';
        }
        updateBackendStatus(false, message);
        return false;
    }
}

/**
 * Send prediction request to backend
 */
async function checkUrl(url) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.PREDICT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // Parse response
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            // Handle API errors (4xx, 5xx)
            const errorMessage = data.detail?.message || data.detail || 'An error occurred';
            return { success: false, error: errorMessage, statusCode: response.status };
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            return { success: false, error: 'Request timeout - the server took too long to respond' };
        }
        return { success: false, error: `Network error: ${error.message}` };
    }
}

// ============================================
// UI Update Functions
// ============================================

/**
 * Update backend connection status banner
 */
function updateBackendStatus(isConnected, message) {
    state.isBackendConnected = isConnected;
    elements.statusText.textContent = message;
    
    // Remove all status classes
    elements.backendStatus.classList.remove('checking', 'connected', 'disconnected');
    
    // Add appropriate class
    if (isConnected) {
        elements.backendStatus.classList.add('connected');
    } else {
        elements.backendStatus.classList.add('disconnected');
    }
}

/**
 * Set loading state for the form
 */
function setLoadingState(isLoading) {
    state.isChecking = isLoading;
    elements.checkButton.disabled = isLoading;
    elements.urlInput.disabled = isLoading;
    
    if (isLoading) {
        elements.checkButton.classList.add('loading');
    } else {
        elements.checkButton.classList.remove('loading');
    }
}

/**
 * Display validation error
 */
function showValidationError(message) {
    elements.urlError.textContent = message;
    elements.urlInput.classList.add('error');
    elements.urlInput.setAttribute('aria-invalid', 'true');
}

/**
 * Clear validation error
 */
function clearValidationError() {
    elements.urlError.textContent = '';
    elements.urlInput.classList.remove('error');
    elements.urlInput.setAttribute('aria-invalid', 'false');
}

/**
 * Display prediction results
 */
function displayResults(data) {
    // Hide error container
    elements.errorContainer.style.display = 'none';
    
    // Populate result data
    elements.resultUrl.textContent = data.url;
    elements.resultPrediction.textContent = data.prediction;
    
    // Set card style based on result
    elements.resultCard.classList.remove('safe', 'phishing');
    const cardClass = data.is_phishing ? 'phishing' : 'safe';
    elements.resultCard.classList.add(cardClass);
    
    // Set icon and title
    const resultIcon = elements.resultCard.querySelector('.result-icon');
    const resultTitle = elements.resultCard.querySelector('.result-title');
    
    if (data.is_phishing) {
        resultIcon.textContent = '⚠️';
        resultTitle.textContent = 'Phishing Link Detected';
        elements.resultDescription.textContent = 
            'This URL has been identified as a potential phishing link. Do not click on it or enter any personal information.';
    } else {
        resultIcon.textContent = '✅';
        resultTitle.textContent = 'URL Appears Safe';
        elements.resultDescription.textContent = 
            'This URL appears to be safe. However, always exercise caution when clicking links from unknown sources.';
    }
    
    // Display confidence if available
    if (data.confidence !== null && data.confidence !== undefined) {
        elements.confidenceContainer.style.display = 'flex';
        const confidencePercent = (data.confidence * 100).toFixed(1);
        elements.resultConfidence.textContent = `${confidencePercent}%`;
        
        // Update progress bar
        elements.confidenceProgress.style.width = `${confidencePercent}%`;
        elements.confidenceProgress.setAttribute('aria-valuenow', confidencePercent);
    } else {
        elements.confidenceContainer.style.display = 'none';
    }
    
    // Show results
    elements.resultsContainer.style.display = 'block';
    
    // Scroll to results
    elements.resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Display error message
 */
function displayError(message) {
    // Hide results container
    elements.resultsContainer.style.display = 'none';
    
    // Show error
    elements.errorMessage.textContent = message;
    elements.errorContainer.style.display = 'block';
    
    // Scroll to error
    elements.errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================
// Validation Functions
// ============================================

/**
 * Validate URL format
 */
function validateUrl(url) {
    if (!url || url.trim() === '') {
        return { valid: false, error: 'Please enter a URL' };
    }
    
    const trimmedUrl = url.trim();
    
    // Check if it starts with http:// or https://
    if (!trimmedUrl.startsWith('http://') && !trimmedUrl.startsWith('https://')) {
        return { valid: false, error: 'URL must start with http:// or https://' };
    }
    
    // Basic URL validation
    try {
        const urlObject = new URL(trimmedUrl);
        // Check if it has a valid hostname
        if (!urlObject.hostname || urlObject.hostname.length === 0) {
            return { valid: false, error: 'Invalid URL format' };
        }
        return { valid: true, url: trimmedUrl };
    } catch (e) {
        return { valid: false, error: 'Invalid URL format' };
    }
}

// ============================================
// Event Handlers
// ============================================

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Clear previous validation errors
    clearValidationError();
    
    // Get and validate URL
    const urlValue = elements.urlInput.value;
    const validation = validateUrl(urlValue);
    
    if (!validation.valid) {
        showValidationError(validation.error);
        elements.urlInput.focus();
        return;
    }
    
    // Check backend connection
    if (!state.isBackendConnected) {
        displayError('Cannot check URL: Backend is not connected. Please ensure the API server is running at ' + CONFIG.API_BASE_URL);
        return;
    }
    
    // Set loading state
    setLoadingState(true);
    
    // Make API request
    const result = await checkUrl(validation.url);
    
    // Clear loading state
    setLoadingState(false);
    
    // Handle result
    if (result.success) {
        displayResults(result.data);
    } else {
        let errorMessage = result.error;
        
        // Add more context for specific errors
        if (result.statusCode === 503) {
            errorMessage += ' The prediction service is temporarily unavailable.';
        } else if (result.statusCode === 422) {
            errorMessage = 'Invalid URL format. Please enter a complete HTTP or HTTPS URL.';
        }
        
        displayError(errorMessage);
    }
}

/**
 * Handle URL input changes
 */
function handleUrlInput() {
    // Clear validation error when user starts typing
    if (elements.urlError.textContent) {
        clearValidationError();
    }
}

// ============================================
// Initialization
// ============================================

/**
 * Initialize the application
 */
async function initializeApp() {
    // Set up event listeners
    elements.checkForm.addEventListener('submit', handleFormSubmit);
    elements.urlInput.addEventListener('input', handleUrlInput);
    
    // Initial health check
    await checkBackendHealth();
    
    // Set up periodic health checks
    state.healthCheckInterval = setInterval(checkBackendHealth, CONFIG.HEALTH_CHECK_INTERVAL);
    
    // Focus on input field
    elements.urlInput.focus();
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (state.healthCheckInterval) {
        clearInterval(state.healthCheckInterval);
    }
});
