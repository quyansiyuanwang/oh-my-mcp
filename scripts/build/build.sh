#!/bin/bash
# MCP Server Build Script for Linux/macOS
# This is a convenience wrapper around build.py

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment${NC}"
    echo -e "${BLUE}   Checking for .venv...${NC}"
    
    if [[ -d ".venv" ]]; then
        echo -e "${GREEN}   Found .venv, activating...${NC}"
        source .venv/bin/activate
    else
        echo -e "${YELLOW}   No .venv found. Install dependencies with: pip install -e .${NC}"
    fi
fi

# Run the Python build script
echo -e "${BLUE}🚀 Starting build process...${NC}\n"
python3 build.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "\n${GREEN}✨ Build completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Build failed with exit code $exit_code${NC}"
fi

exit $exit_code
