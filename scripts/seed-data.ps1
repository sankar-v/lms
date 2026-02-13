#!/usr/bin/env pwsh

Write-Host "🌱 Seeding database with sample data..." -ForegroundColor Cyan

# Check if PostgreSQL is running
$dockerPs = docker ps
if ($dockerPs -notmatch "lms_postgres") {
    Write-Host "❌ PostgreSQL container is not running. Please start it first:" -ForegroundColor Red
    Write-Host "   cd infrastructure\docker" -ForegroundColor Yellow
    Write-Host "   docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Run seed script
Get-Content "database\seeds\sample_data.sql" | docker exec -i lms_postgres psql -U lms_user -d lms_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Database seeded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Sample data includes:"
    Write-Host "  - 3 users (password: 'password' for all)"
    Write-Host "  - 6 learning modules"
    Write-Host "  - Sample progress records"
    Write-Host "  - Sample quizzes and questions"
} else {
    Write-Host "❌ Failed to seed database" -ForegroundColor Red
    exit 1
}
