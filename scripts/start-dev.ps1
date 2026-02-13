#!/usr/bin/env pwsh

Write-Host "Starting LMS Development Environment..." -ForegroundColor Cyan

# Check if Docker Compose is available
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker Compose is required but not installed." -ForegroundColor Red
    exit 1
}

# Navigate to docker directory
Push-Location infrastructure\docker

# Check if .env file exists
if (-not (Test-Path '.env')) {
    Write-Host "WARNING: .env file not found. Creating from example..." -ForegroundColor Yellow
    Copy-Item '.env.example' '.env'
    Write-Host "WARNING: Please add your OpenAI API key to infrastructure\docker\.env and run this script again." -ForegroundColor Yellow
    Pop-Location
    exit 1
}

# Check if OPENAI_API_KEY is set
$envContent = Get-Content '.env' -Raw
if ($envContent -notmatch 'OPENAI_API_KEY=sk-') {
    Write-Host "WARNING: OPENAI_API_KEY not found or invalid in .env file." -ForegroundColor Yellow
    Write-Host "Please add your OpenAI API key and run this script again." -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Write-Host "Starting services..." -ForegroundColor Cyan
docker-compose up -d

# Wait for services to be ready
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service health
Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Cyan

$services = @('postgres', 'qdrant', 'backend', 'ai-services', 'frontend')
$dockerPs = docker-compose ps

foreach ($service in $services) {
    if ($dockerPs -match ("lms_" + $service + ".*Up")) {
        Write-Host "SUCCESS: $service is running" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: $service may not be ready yet" -ForegroundColor Yellow
    }
}

Pop-Location

Write-Host ""
Write-Host "Development environment started!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:3000"
Write-Host "  Backend API: http://localhost:8000/docs"
Write-Host "  AI Services: http://localhost:8001/docs"
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  cd infrastructure\docker"
Write-Host "  docker-compose logs -f [service-name]"
Write-Host ""
Write-Host "Stop services:" -ForegroundColor Yellow
Write-Host "  cd infrastructure\docker"
Write-Host "  docker-compose down"
