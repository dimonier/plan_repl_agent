#!/bin/bash
set -e

# Clear agent-installed packages on startup to avoid conflicts
echo "Cleaning up lib directories..."

rm -rf /app/lib/.pydeps/*
rm -rf /app/lib/.pipcache
rm -rf /app/lib/.matplotlib

mkdir -p /app/lib/.pydeps
mkdir -p /app/lib/.matplotlib
mkdir -p /app/lib/.pipcache

echo "Starting agent server..."
exec "$@"
