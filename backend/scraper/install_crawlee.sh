#!/bin/bash
# Script de instalación y configuración de Crawlee para el scraper

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  Instalación de Crawlee para Bolivia KPIs Scraper"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found${NC}"
    echo "Please run this script from the backend/scraper directory"
    exit 1
fi

# 1. Create/activate virtual environment (optional)
echo -e "${YELLOW}[1/5]${NC} Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "💡 To activate virtual environment, run:"
echo "   source venv/bin/activate"
echo ""

# Detect if venv is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Exiting. Please activate venv and run again."
        exit 0
    fi
fi

# 2. Install Python dependencies
echo -e "${YELLOW}[2/5]${NC} Installing Python dependencies..."
pip install -r requirements.txt

# 3. Install Playwright browsers
echo -e "${YELLOW}[3/5]${NC} Installing Playwright browsers..."
echo "This will download Chromium (~300MB). Continue? (y/n)"
read -r response
if [ "$response" = "y" ]; then
    playwright install chromium
    echo -e "${GREEN}✓${NC} Chromium installed"
else
    echo -e "${YELLOW}⚠️  Skipped browser installation${NC}"
    echo "   Run manually: playwright install chromium"
fi

# 4. Create data directories
echo -e "${YELLOW}[4/5]${NC} Creating data directories..."
mkdir -p ../../../data/raw
mkdir -p ../../../data/storage
echo -e "${GREEN}✓${NC} Directories created:"
echo "   - data/raw (for JSONL exports)"
echo "   - data/storage (for Crawlee storage)"

# 5. Verify installation
echo -e "${YELLOW}[5/5]${NC} Verifying installation..."

# Check Crawlee
python3 -c "import crawlee; print(f'✓ Crawlee {crawlee.__version__} installed')" 2>/dev/null && CRAWLEE_OK=1 || CRAWLEE_OK=0

# Check Playwright
python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright installed')" 2>/dev/null && PLAYWRIGHT_OK=1 || PLAYWRIGHT_OK=0

# Check BeautifulSoup
python3 -c "import bs4; print('✓ BeautifulSoup4 installed')" 2>/dev/null && BS4_OK=1 || BS4_OK=0

# Check Redis
python3 -c "import redis; print('✓ Redis client installed')" 2>/dev/null && REDIS_OK=1 || REDIS_OK=0

# Check psycopg2
python3 -c "import psycopg2; print('✓ psycopg2 installed')" 2>/dev/null && PSYCOPG2_OK=1 || PSYCOPG2_OK=0

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Installation Summary:${NC}"
echo "════════════════════════════════════════════════════════════════"

if [ $CRAWLEE_OK -eq 1 ]; then
    python3 -c "import crawlee; print(f'  ✓ Crawlee {crawlee.__version__}')"
else
    echo -e "  ${RED}✗ Crawlee (failed)${NC}"
fi

[ $PLAYWRIGHT_OK -eq 1 ] && echo "  ✓ Playwright" || echo -e "  ${RED}✗ Playwright (failed)${NC}"
[ $BS4_OK -eq 1 ] && echo "  ✓ BeautifulSoup4" || echo -e "  ${RED}✗ BeautifulSoup4 (failed)${NC}"
[ $REDIS_OK -eq 1 ] && echo "  ✓ Redis client" || echo -e "  ${RED}✗ Redis client (failed)${NC}"
[ $PSYCOPG2_OK -eq 1 ] && echo "  ✓ psycopg2" || echo -e "  ${RED}✗ psycopg2 (failed)${NC}"

echo ""

# Check if all OK
if [ $CRAWLEE_OK -eq 1 ] && [ $PLAYWRIGHT_OK -eq 1 ] && [ $BS4_OK -eq 1 ] && [ $REDIS_OK -eq 1 ] && [ $PSYCOPG2_OK -eq 1 ]; then
    echo -e "${GREEN}✓ All dependencies installed successfully!${NC}"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Next Steps:"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "1. Configure environment variables (optional):"
    echo "   cp ../../../.env.example ../../../.env"
    echo "   # Edit .env with your configuration"
    echo ""
    echo "2. Test the scraper:"
    echo "   python -m bolivia_scraper oep_elections"
    echo ""
    echo "3. Read the migration guide:"
    echo "   cat CRAWLEE_MIGRATION.md"
    echo ""
else
    echo -e "${RED}✗ Some dependencies failed to install${NC}"
    echo "Please check the error messages above and try again."
    exit 1
fi
