/**
 * Configuration file for the Phishing Link Detector frontend
 * 
 * Update API_BASE_URL for different environments:
 * - Development: http://localhost:8000
 * - Production: https://your-domain.com
 */

const CONFIG = {
    // API base URL - change this for deployment
    API_BASE_URL: 'http://localhost:8000',
    
    // API endpoints
    ENDPOINTS: {
        HEALTH: '/api/health',
        PREDICT: '/api/predict'
    },
    
    // Request timeout in milliseconds
    REQUEST_TIMEOUT: 10000,
    
    // Health check interval in milliseconds
    HEALTH_CHECK_INTERVAL: 30000
};

// Freeze the config to prevent accidental modifications
Object.freeze(CONFIG);
Object.freeze(CONFIG.ENDPOINTS);
