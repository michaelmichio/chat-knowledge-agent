#!/bin/bash

set -e

echo "⚙️  Building Docker images..."
docker compose build

echo "🚀 Starting containers in background..."
docker compose up -d

echo "🐍 Running Alembic migrations inside backend container..."
docker compose run --rm backend bash -c "
    echo '🔄 Removing old migration files...';
    rm -rf infra/migrations/versions/*;

    echo '📦 Generating new Alembic revision...';
    alembic -c infra/migrations/alembic.ini revision --autogenerate -m \"init\";

    echo '⬆️ Upgrading database to head...';
    alembic -c infra/migrations/alembic.ini upgrade head;

    echo '✅ Alembic init completed successfully.';
"
