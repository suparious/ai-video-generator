.PHONY: build run stop publish clean download-models help

# Default target
help:
	@echo "FramePack AI Video Generator"
	@echo ""
	@echo "Usage:"
	@echo "  make build          Build the Docker image"
	@echo "  make run            Run the container with docker-compose"
	@echo "  make stop           Stop the running container"
	@echo "  make publish        Publish image to GitHub Container Registry"
	@echo "  make clean          Remove all containers and images"
	@echo "  make download-models Download required models"
	@echo "  make help           Show this help message"

# Build the Docker image
build:
	@echo "Building Docker image..."
	cd docker && docker-compose build

# Run the container
run:
	@echo "Starting container..."
	cd docker && docker-compose up -d
	@echo "Service available at http://localhost:7860"

# Stop the container
stop:
	@echo "Stopping container..."
	cd docker && docker-compose down

# Publish image to GitHub Container Registry
publish:
	@echo "Publishing to GitHub Container Registry..."
	@if [ -z "$$GHCR_PAT" ]; then \
		echo "ERROR: GitHub Personal Access Token (GHCR_PAT) is not set."; \
		echo "Please set it with: export GHCR_PAT='your_github_token'"; \
		exit 1; \
	fi
	scripts/publish_to_ghcr.sh

# Clean up containers and images
clean:
	@echo "Cleaning up containers and images..."
	cd docker && docker-compose down --rmi all
	docker system prune -f

# Download required models
download-models:
	@echo "Downloading required models..."
	python scripts/download_models.py
