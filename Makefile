# Enhanced Information Validation Tool - Makefile
# Provides convenient commands for Docker operations

.PHONY: help build up down restart logs clean test health status

# Default target
help:
	@echo "Enhanced Information Validation Tool - Docker Commands"
	@echo "====================================================="
	@echo ""
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Remove all containers, images, and volumes"
	@echo "  test      - Run health checks on all services"
	@echo "  health    - Check service health status"
	@echo "  status    - Show status of all services"
	@echo "  backend   - Show backend logs"
	@echo "  frontend  - Show frontend logs"
	@echo ""
	@echo "Usage examples:"
	@echo "  make build    # Build all images"
	@echo "  make up       # Start the application"
	@echo "  make logs     # View all logs"
	@echo "  make down     # Stop the application"

# Build all Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache

# Start all services
up:
	@echo "🚀 Starting Enhanced Information Validation Tool..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:5001"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

# Restart all services
restart: down up

# Show logs from all services
logs:
	@echo "📋 Showing logs from all services..."
	docker-compose logs -f

# Show backend logs only
backend:
	@echo "📋 Showing backend logs..."
	docker-compose logs -f backend

# Show frontend logs only
frontend:
	@echo "📋 Showing frontend logs..."
	docker-compose logs -f frontend

# Clean up everything
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup complete!"

# Run health checks
test:
	@echo "🔍 Running health checks..."
	@echo "Testing backend health..."
	curl -f http://localhost:5001/health || echo "❌ Backend health check failed"
	@echo "Testing frontend health..."
	curl -f http://localhost/health || echo "❌ Frontend health check failed"
	@echo "✅ Health checks complete!"

# Check service health status
health:
	@echo "🏥 Checking service health..."
	docker-compose ps

# Show status of all services
status:
	@echo "📊 Service status:"
	docker-compose ps
	@echo ""
	@echo "📈 Resource usage:"
	docker stats --no-stream

# Development commands
dev-build:
	@echo "🔨 Building for development..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

dev-up:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production commands
prod-build:
	@echo "🔨 Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Backup and restore
backup:
	@echo "💾 Creating backup..."
	mkdir -p backups
	docker run --rm -v validation-tool_validation_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/validation-data-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✅ Backup created in backups/ directory"

# Update images
update:
	@echo "🔄 Updating Docker images..."
	docker-compose pull
	docker-compose build --pull
	@echo "✅ Images updated!"

# Show application URLs
urls:
	@echo "🌐 Application URLs:"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:5001"
	@echo "Health Check: http://localhost:5001/health"
	@echo "API Documentation: http://localhost:5001/docs (if available)"

