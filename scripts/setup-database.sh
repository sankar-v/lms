#!/bin/bash

# Database Setup Script for LMS Project
# This script starts the PostgreSQL database with pgvector using Docker Compose

set -e

echo "=========================================="
echo "LMS Database Setup"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Stop existing container if running
echo "🛑 Stopping existing database container (if any)..."
docker-compose -f docker-compose.db.yml down 2>/dev/null || true
echo ""

# Start the database
echo "🚀 Starting PostgreSQL with pgvector..."
docker-compose -f docker-compose.db.yml up -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to be ready..."
timeout=30
counter=0

while [ $counter -lt $timeout ]; do
    if docker exec lms-postgres pg_isready -U lms_user -d lms_db > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    
    if [ $counter -eq $((timeout - 1)) ]; then
        echo "❌ Timeout waiting for database"
        exit 1
    fi
    
    echo -n "."
    sleep 1
    counter=$((counter + 1))
done

echo ""
echo ""

# Verify pgvector extension
echo "🔍 Verifying pgvector extension..."
if docker exec lms-postgres psql -U lms_user -d lms_db -c "SELECT extname, extversion FROM pg_extension WHERE extname='vector';" | grep -q vector; then
    echo "✅ pgvector extension is installed"
else
    echo "❌ pgvector extension not found"
    exit 1
fi

echo ""

# Show table counts
echo "📊 Database Statistics:"
echo "----------------------------------------"
docker exec lms-postgres psql -U lms_user -d lms_db -c "
SELECT 
    schemaname,
    tablename,
    (SELECT count(*) FROM pg_catalog.pg_class c WHERE c.relname = tablename) as row_count
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
" 2>/dev/null || echo "Could not fetch table stats"

echo ""
echo "=========================================="
echo "✅ Database Setup Complete!"
echo "=========================================="
echo ""
echo "Database connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: lms_db"
echo "  Username: lms_user"
echo "  Password: lms_password"
echo ""
echo "Connection string:"
echo "  postgresql://lms_user:lms_password@localhost:5432/lms_db"
echo ""
echo "To stop the database:"
echo "  docker-compose -f docker-compose.db.yml down"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.db.yml logs -f"
echo ""
