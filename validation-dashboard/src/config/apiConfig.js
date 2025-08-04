/**
 * Centralized API Configuration for Enhanced Information Validation Tool
 * 
 * This configuration automatically detects the environment and sets the appropriate
 * API base URL without requiring manual editing for different deployment scenarios.
 * 
 * Supported Scenarios:
 * 1. Manus workspace deployment (production/staging)
 * 2. Local containerized environment (development)
 * 3. Environment variable override (flexible configuration)
 */

/**
 * Detects the current environment and returns appropriate configuration
 * @returns {Object} Configuration object with API settings
 */
function detectEnvironment() {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return { environment: 'server', isLocal: false };
  }

  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const port = window.location.port;

  // Local development indicators
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
  const isLocalIP = hostname.match(/^192\.168\.|^10\.|^172\.(1[6-9]|2[0-9]|3[0-1])\./);
  const isLocal = isLocalhost || isLocalIP;

  // Manus workspace indicators
  const isManusWorkspace = hostname.includes('.manus.space');
  
  // Docker container indicators (when running in containerized local environment)
  const isContainerized = port === '3000' || port === '5173'; // Common Vite/React dev ports

  return {
    hostname,
    protocol,
    port,
    isLocal,
    isLocalhost,
    isLocalIP,
    isManusWorkspace,
    isContainerized,
    environment: isManusWorkspace ? 'manus' : isLocal ? 'local' : 'unknown'
  };
}

/**
 * Generates the appropriate API base URL based on environment detection
 * @param {Object} envInfo - Environment information from detectEnvironment()
 * @returns {string} API base URL
 */
function generateApiBaseUrl(envInfo) {
  // Priority 1: Environment variable override (highest priority)
  if (import.meta.env.VITE_API_BASE) {
    console.log('🔧 Using environment variable API base:', import.meta.env.VITE_API_BASE);
    return import.meta.env.VITE_API_BASE;
  }

  // Priority 2: Manus workspace deployment
  if (envInfo.isManusWorkspace) {
    // Extract the frontend deployment ID and construct backend URL
    const frontendId = envInfo.hostname.split('.')[0];
    
    // For Manus workspace, we need to determine the backend URL
    // This could be done in several ways:
    
    // Option 1: Use a known backend deployment ID (if static)
    // const backendUrl = 'https://3dhkilcejd17.manus.space';
    
    // Option 2: Use a pattern-based approach (if backend follows naming convention)
    // const backendUrl = `https://api-${frontendId}.manus.space`;
    
    // Option 3: Use environment-specific backend URLs
    const manusBackendUrl = 'https://3dhkilcejd17.manus.space'; // Current working backend
    
    console.log('🌐 Detected Manus workspace environment, using backend:', manusBackendUrl);
    return manusBackendUrl;
  }

  // Priority 3: Local development environment
  if (envInfo.isLocal) {
    const localApiUrl = 'http://localhost:5001';
    console.log('🏠 Detected local environment, using backend:', localApiUrl);
    return localApiUrl;
  }

  // Priority 4: Fallback (should rarely be used)
  const fallbackUrl = 'http://localhost:5001';
  console.warn('⚠️ Unknown environment, using fallback:', fallbackUrl);
  return fallbackUrl;
}

/**
 * Main configuration object
 */
const envInfo = detectEnvironment();
const API_BASE = generateApiBaseUrl(envInfo);

// Log configuration for debugging
console.log('🔧 API Configuration:', {
  environment: envInfo.environment,
  hostname: envInfo.hostname,
  isLocal: envInfo.isLocal,
  isManusWorkspace: envInfo.isManusWorkspace,
  apiBase: API_BASE,
  hasEnvOverride: !!import.meta.env.VITE_API_BASE
});

/**
 * Configuration object with all API settings
 */
export const apiConfig = {
  // Primary API base URL
  baseUrl: API_BASE,
  
  // Environment information
  environment: envInfo,
  
  // API endpoints (can be extended as needed)
  endpoints: {
    health: '/api/health',
    validation: '/api/validation',
    analytics: '/api/analytics',
    export: '/api/export',
    google: '/api/google',
    realData: '/api/real-data'
  },
  
  // Request configuration
  defaultHeaders: {
    'Content-Type': 'application/json'
  },
  
  // Timeout settings
  timeout: 30000, // 30 seconds
  
  // Retry configuration
  retryAttempts: 3,
  retryDelay: 1000 // 1 second
};

/**
 * Helper function to build full API URLs
 * @param {string} endpoint - The endpoint path (with or without leading slash)
 * @returns {string} Full API URL
 */
export function buildApiUrl(endpoint) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${apiConfig.baseUrl}${cleanEndpoint}`;
}

/**
 * Helper function for making API requests with consistent configuration
 * @param {string} endpoint - The API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
export async function apiRequest(endpoint, options = {}) {
  const url = buildApiUrl(endpoint);
  const config = {
    headers: {
      ...apiConfig.defaultHeaders,
      ...options.headers
    },
    ...options
  };
  
  try {
    const response = await fetch(url, config);
    return response;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Export the main API base URL for backward compatibility
export default API_BASE;

// Named exports for specific use cases
export { API_BASE };
export const API_BASE_URL = API_BASE; // Alternative naming convention

