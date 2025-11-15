/**
 * API Communication Module
 * Handles all API calls to the FastAPI backend
 */

// API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:8000/api/v1',  // Change this for production
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
};

/**
 * Make API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseURL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...API_CONFIG.headers,
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

/**
 * API Methods
 */
const API = {
    /**
     * Get list of all companies
     */
    getCompanies: async (sector = null) => {
        const params = sector ? `?sector=${encodeURIComponent(sector)}` : '';
        return apiRequest(`/companies${params}`);
    },
    
    /**
     * Get stock data for a symbol
     */
    getStockData: async (symbol, days = 30) => {
        return apiRequest(`/data/${symbol}?days=${days}`);
    },
    
    /**
     * Get stock summary statistics
     */
    getStockSummary: async (symbol) => {
        return apiRequest(`/summary/${symbol}`);
    },
    
    /**
     * Compare two stocks
     */
    compareStocks: async (symbol1, symbol2, days = 90) => {
        return apiRequest(`/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`);
    },
    
    /**
     * Get top movers (gainers and losers)
     */
    getTopMovers: async (limit = 5) => {
        return apiRequest(`/movers?limit=${limit}`);
    },
    
    /**
     * Get technical indicators
     */
    getTechnicalIndicators: async (symbol) => {
        return apiRequest(`/technicals/${symbol}`);
    }
};

/**
 * Check if API is accessible
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_CONFIG.baseURL.replace('/api/v1', '')}/health`);
        return response.ok;
    } catch (error) {
        console.error('API health check failed:', error);
        return false;
    }
}

// Export for use in other scripts
window.API = API;
window.checkAPIHealth = checkAPIHealth;