# Frontend Docker Health Check Fix

## Issue
The frontend container was showing as "unhealthy" in Docker despite responding correctly to manual health checks.

## Root Cause
The nginx:alpine base image does not include `curl` by default, causing the HEALTHCHECK command to fail:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
```

## Symptoms
- `docker ps` shows container as "unhealthy"
- Manual `curl -f http://localhost/health` returns "healthy" correctly
- Nginx serves the `/health` endpoint properly via nginx.conf

## Solution
Added curl installation to the Dockerfile:
```dockerfile
# Install curl for health checks
RUN apk add --no-cache curl
```

## Technical Details

### nginx.conf Health Endpoint
The nginx configuration already includes a proper health endpoint:
```nginx
# Health check endpoint
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

### Fixed Dockerfile
```dockerfile
# Production stage with Nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Alternative Solutions Considered

1. **Use wget instead of curl** (usually available in alpine)
2. **Use nginx status module** (more complex setup)
3. **Remove health check entirely** (not recommended)

## Testing
After rebuilding the container:
1. `docker ps` should show container as "healthy"
2. Manual health check should continue working
3. Docker health check logs should show successful checks

## Impact
- Minimal: Only adds curl package (~2MB) to container
- Fixes Docker orchestration health monitoring
- Enables proper container lifecycle management

