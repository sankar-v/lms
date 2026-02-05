#!/bin/bash

echo "🌱 Seeding database with sample data..."

# Check if PostgreSQL is running
if ! docker ps | grep -q lms_postgres; then
    echo "❌ PostgreSQL container is not running. Please start it first:"
    echo "   cd infrastructure/docker && docker-compose up -d postgres"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 3

# Run seed script
docker exec -i lms_postgres psql -U lms_user -d lms_db < database/seeds/sample_data.sql

if [ $? -eq 0 ]; then
    echo "✅ Database seeded successfully!"
    echo ""
    echo "Sample data includes:"
    echo "  - 3 users (password: 'password' for all)"
    echo "  - 6 learning modules"
    echo "  - Sample progress records"
    echo "  - Sample quizzes and questions"
else
    echo "❌ Failed to seed database"
    exit 1
fi
