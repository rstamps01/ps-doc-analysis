#!/bin/bash
# Enhanced Information Validation Tool - Docker Entrypoint Script

set -e

echo "🚀 Starting Enhanced Information Validation Tool..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "⏳ Waiting for $service_name to be ready..."
    while ! nc -z $host $port; do
        sleep 1
    done
    echo "✅ $service_name is ready!"
}

# Function to check if backend is healthy
check_backend_health() {
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking backend health..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://backend:5000/health >/dev/null 2>&1; then
            echo "✅ Backend is healthy!"
            return 0
        fi
        echo "⏳ Attempt $attempt/$max_attempts - Backend not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Backend health check failed after $max_attempts attempts"
    return 1
}

# Function to initialize database
init_database() {
    echo "🗄️ Initializing database..."
    
    # Create data directory if it doesn't exist
    mkdir -p /app/data
    mkdir -p /app/logs
    mkdir -p /app/exports
    
    # Set permissions
    chmod 755 /app/data
    chmod 755 /app/logs
    chmod 755 /app/exports
    
    echo "✅ Database initialization complete!"
}

# Function to validate environment
validate_environment() {
    echo "🔧 Validating environment configuration..."
    
    # Check required environment variables
    local required_vars=("FLASK_ENV" "FLASK_APP")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "❌ Missing required environment variables: ${missing_vars[*]}"
        echo "Please check your .env file or environment configuration"
        exit 1
    fi
    
    echo "✅ Environment validation complete!"
}

# Function to setup Google credentials
setup_google_credentials() {
    echo "🔑 Setting up Google API credentials..."
    
    if [ -f "/app/credentials/google-service-account.json" ]; then
        export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/google-service-account.json"
        echo "✅ Google service account credentials found!"
    else
        echo "⚠️ Google service account credentials not found"
        echo "Please mount your credentials file to /app/credentials/google-service-account.json"
    fi
}

# Main execution
main() {
    echo "🎯 Enhanced Information Validation Tool Docker Entrypoint"
    echo "=================================================="
    
    # Validate environment
    validate_environment
    
    # Setup Google credentials
    setup_google_credentials
    
    # Initialize database
    init_database
    
    # Wait for dependencies if this is the frontend
    if [ "$1" = "frontend" ]; then
        wait_for_service backend 5000 "Backend API"
        check_backend_health
    fi
    
    echo "🎉 Initialization complete!"
    echo "=================================================="
    
    # Execute the main command
    exec "$@"
}

# Run main function with all arguments
main "$@"

