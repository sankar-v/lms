#!/bin/bash

echo "🚀 Starting LMS Development Environment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

# Navigate to docker directory
cd infrastructure/docker

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please add your OpenAI API key to infrastructure/docker/.env and run this script again.${NC}"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "^OPENAI_API_KEY=sk-" .env; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not found or invalid in .env file.${NC}"
    echo -e "${YELLOW}   Please add your OpenAI API key and run this script again.${NC}"
    exit 1
fi

echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "\n${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check service health
echo -e "\n${BLUE}Checking service status...${NC}"

services=("postgres" "qdrant" "backend" "ai-services" "frontend")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "lms_$service.*Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${YELLOW}⚠️  $service may not be ready yet${NC}"
    fi
done

echo -e "\n${GREEN}✅ Development environment started!${NC}"
echo -e "\n${BLUE}Access the application:${NC}"
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000/docs"
echo "  AI Services: http://localhost:8001/docs"
echo "  Qdrant UI:   http://localhost:6333/dashboard"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  docker-compose logs -f [service-name]"
echo ""
echo -e "${YELLOW}Stop services:${NC}"
echo "  docker-compose down"
