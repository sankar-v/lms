#!/usr/bin/env pwsh

Write-Host "Setting up LMS Development Environment..." -ForegroundColor Cyan

# Check prerequisites
Write-Host ""
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "docker" = "Docker"
    "docker-compose" = "Docker Compose"
    "node" = "Node.js"
    "python" = "Python 3"
}

$missingPrereqs = @()
foreach ($cmd in $prerequisites.Keys) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $($prerequisites[$cmd]) is required but not installed." -ForegroundColor Red
        $missingPrereqs += $prerequisites[$cmd]
    }
}

if ($missingPrereqs.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing prerequisites: $($missingPrereqs -join ', ')" -ForegroundColor Red
    Write-Host "Please install them and try again." -ForegroundColor Red
    exit 1
}

Write-Host "SUCCESS: All prerequisites installed" -ForegroundColor Green

# Create environment files
Write-Host ""
Write-Host "Setting up environment files..." -ForegroundColor Yellow

$envFiles = @(
    @{Source='backend\.env.example'; Target='backend\.env'}
    @{Source='ai-services\.env.example'; Target='ai-services\.env'}
    @{Source='frontend\.env.example'; Target='frontend\.env'}
    @{Source='infrastructure\docker\.env.example'; Target='infrastructure\docker\.env'}
)

foreach ($env in $envFiles) {
    if (-not (Test-Path $env.Target)) {
        Copy-Item $env.Source $env.Target
        Write-Host "SUCCESS: Created $($env.Target)" -ForegroundColor Green

        if ($env.Target -match 'ai-services|docker') {
            Write-Host "WARNING: Please add your OpenAI API key to $($env.Target)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "INFO: $($env.Target) already exists" -ForegroundColor Gray
    }
}

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location frontend
npm install
Pop-Location
Write-Host "SUCCESS: Frontend dependencies installed" -ForegroundColor Green

# Create Python virtual environments
Write-Host ""
Write-Host "Setting up Python virtual environments..." -ForegroundColor Yellow

# Backend venv
Write-Host "Setting up backend virtual environment..." -ForegroundColor Cyan
Push-Location backend
if (-not (Test-Path 'venv')) {
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    Write-Host "SUCCESS: Backend virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "INFO: Backend virtual environment already exists" -ForegroundColor Gray
}
Pop-Location

# AI Services venv
Write-Host "Setting up AI services virtual environment..." -ForegroundColor Cyan
Push-Location ai-services
if (-not (Test-Path 'venv')) {
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    Write-Host "SUCCESS: AI Services virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "INFO: AI Services virtual environment already exists" -ForegroundColor Gray
}
Pop-Location

# Create .gitignore if not exists
if (-not (Test-Path '.gitignore')) {
    $gitignoreContent = @'
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
'@
    $gitignoreContent | Out-File -FilePath '.gitignore' -Encoding UTF8
    Write-Host "SUCCESS: Created .gitignore" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your OpenAI API key to:"
Write-Host "   - ai-services\.env"
Write-Host "   - infrastructure\docker\.env"
Write-Host ""
Write-Host "2. Start all services with Docker:" -ForegroundColor Cyan
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. Access the application:"
Write-Host "   - Frontend:    http://localhost:3000"
Write-Host "   - Backend API: http://localhost:8000/docs"
Write-Host "   - AI Services: http://localhost:8001/docs"
Write-Host ""
Write-Host "For more information, see docs\guides\development.md"
