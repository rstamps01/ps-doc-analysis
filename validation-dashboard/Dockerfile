# Enhanced Information Validation Tool - Frontend Dockerfile

# Build stage
FROM node:20 AS build

# Set working directory
WORKDIR /app

# Copy package files first (for better caching)
COPY package.json ./
COPY .npmrc ./

# Install dependencies
RUN npm install

# Copy source code and config
COPY public/ ./public/
COPY src/ ./src/
COPY vite.config.js ./
COPY index.html ./
COPY jsconfig.json ./

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Install debugging tools and health check utilities
RUN apk add --no-cache curl bash vim

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

