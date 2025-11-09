#!/bin/bash
# Watchtower Setup Script for VPS
# This script sets up automatic deployments with Watchtower

set -e

echo "🚀 Setting up Watchtower Auto-Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on VPS
if [ ! -d "/usr/share/nginx/html/nedko.info/cdn-check" ]; then
    echo -e "${YELLOW}Warning: Expected directory not found${NC}"
    echo "This script is designed for VPS deployment"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to project directory
cd /usr/share/nginx/html/nedko.info/cdn-check || exit 1
echo -e "${BLUE}📁 Working directory: $(pwd)${NC}"
echo ""

# Pull latest changes
echo -e "${BLUE}📥 Pulling latest configuration from GitHub...${NC}"
git pull origin master || git pull origin main
echo ""

# Stop existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker compose down
echo ""

# Pull latest image
echo -e "${BLUE}🐳 Pulling latest Docker image...${NC}"
docker pull ghcr.io/nedkohristov/cdn-check:latest
echo ""

# Start services with Watchtower
echo -e "${BLUE}▶️  Starting services (CDN Checker + Watchtower)...${NC}"
docker compose up -d
echo ""

# Wait for containers to start
echo -e "${BLUE}⏳ Waiting for containers to start...${NC}"
sleep 10
echo ""

# Check status
echo -e "${GREEN}✅ Services Status:${NC}"
docker compose ps
echo ""

# Show Watchtower logs
echo -e "${BLUE}📋 Watchtower Logs:${NC}"
docker logs watchtower --tail=20
echo ""

# Final instructions
echo -e "${GREEN}=========================================="
echo -e "✅ Watchtower Auto-Deployment Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo "📊 What's Running:"
echo "  • CDN Checker: http://localhost:5000"
echo "  • Watchtower: Monitoring for updates every 5 minutes"
echo ""
echo "🔄 Auto-Deployment Flow:"
echo "  1. You push code to GitHub"
echo "  2. GitHub Actions builds & pushes image"
echo "  3. Watchtower detects new image (within 5 min)"
echo "  4. Your VPS automatically updates!"
echo ""
echo "📝 Useful Commands:"
echo "  • View logs:        docker logs watchtower"
echo "  • Check status:     docker compose ps"
echo "  • Force update:     docker exec watchtower watchtower --run-once"
echo "  • Restart services: docker compose restart"
echo ""
echo "📚 Full documentation: WATCHTOWER.md"
echo ""
