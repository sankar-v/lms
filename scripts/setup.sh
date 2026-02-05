#!/bin/bash

echo "🚀 Setting up LMS Development Environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting."; exit 1; }

echo -e "${GREEN}✓ All prerequisites installed${NC}"

# Create environment files
echo -e "\n${YELLOW}Setting up environment files...${NC}"

# Backend .env
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
else
    echo "✓ backend/.env already exists"
fi

# AI Services .env
if [ ! -f ai-services/.env ]; then
    cp ai-services/.env.example ai-services/.env
    echo -e "${GREEN}✓ Created ai-services/.env${NC}"
    echo -e "${YELLOW}⚠️  Please add your OpenAI API key to ai-services/.env${NC}"
else
    echo "✓ ai-services/.env already exists"
fi

# Frontend .env
if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
else
    echo "✓ frontend/.env already exists"
fi

# Docker Compose .env
if [ ! -f infrastructure/docker/.env ]; then
    cp infrastructure/docker/.env.example infrastructure/docker/.env
    echo -e "${GREEN}✓ Created infrastructure/docker/.env${NC}"
    echo -e "${YELLOW}⚠️  Please add your OpenAI API key to infrastructure/docker/.env${NC}"
else
    echo "✓ infrastructure/docker/.env already exists"
fi

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create Python virtual environments
echo -e "\n${YELLOW}Setting up Python virtual environments...${NC}"

# Backend venv
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo -e "${GREEN}✓ Backend virtual environment created${NC}"
else
    echo "✓ Backend virtual environment already exists"
fi
cd ..

# AI Services venv
cd ai-services
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo -e "${GREEN}✓ AI Services virtual environment created${NC}"
else
    echo "✓ AI Services virtual environment already exists"
fi
cd ..

# Create .gitignore if not exists
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Environment files
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

# Docker
docker-compose.override.yml
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Add your OpenAI API key to:"
echo "   - ai-services/.env"
echo "   - infrastructure/docker/.env"
echo ""
echo "2. Start all services with Docker:"
echo "   cd infrastructure/docker"
echo "   docker-compose up -d"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000/docs"
echo "   - AI Services: http://localhost:8001/docs"
echo ""
echo "For more information, see docs/guides/development.md"
