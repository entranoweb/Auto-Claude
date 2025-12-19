#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Auto Claude Enhancement Suite Installation${NC}"
echo -e "${GREEN}  Morph Fast Apply + Warp Grep + Augment Context${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in auto-claude directory
if [ ! -f "requirements.txt" ] || [ ! -d "agents" ]; then
    echo -e "${RED}❌ Error: Must run from auto-claude directory${NC}"
    echo "cd to your auto-claude directory first"
    exit 1
fi

# Check Node.js
echo -e "${YELLOW}🔍 Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Install from https://nodejs.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check Python
echo -e "${YELLOW}🔍 Checking Python...${NC}"
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}✓ Python found: $($PYTHON_CMD --version)${NC}"

# Install Morph MCP Server
echo ""
echo -e "${YELLOW}📦 Installing Morph MCP Server...${NC}"
npm install -g @morphllm/morphmcp
echo -e "${GREEN}✓ Morph MCP installed${NC}"

# Install Morph SDK (for direct integration)
echo -e "${YELLOW}📦 Installing Morph SDK...${NC}"
npm install -g @morphllm/morphsdk
echo -e "${GREEN}✓ Morph SDK installed${NC}"

# Install Augment CLI
echo -e "${YELLOW}📦 Installing Augment CLI...${NC}"
npm install -g @augmentcode/auggie-cli
echo -e "${GREEN}✓ Augment CLI installed${NC}"

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
$PYTHON_CMD -m pip install --break-system-packages aiohttp requests 2>/dev/null || \
$PYTHON_CMD -m pip install aiohttp requests
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create integrations directory structure
echo ""
echo -e "${YELLOW}📁 Creating integration directories...${NC}"
mkdir -p integrations/morph
mkdir -p integrations/augment
touch integrations/__init__.py
touch integrations/morph/__init__.py
touch integrations/augment/__init__.py
echo -e "${GREEN}✓ Directories created${NC}"

# Create Node.js package.json in integrations
echo -e "${YELLOW}📦 Setting up Node.js workspace...${NC}"
cat > integrations/package.json << 'EOF'
{
  "name": "auto-claude-integrations",
  "version": "1.0.0",
  "description": "Enhanced tools for Auto Claude",
  "private": true,
  "dependencies": {
    "@morphllm/morphsdk": "latest",
    "@augmentcode/auggie-sdk": "latest"
  }
}
EOF

cd integrations && npm install && cd ..
echo -e "${GREEN}✓ Node.js workspace configured${NC}"

# Check for API keys
echo ""
echo -e "${YELLOW}🔑 Checking API keys...${NC}"
if [ -f ".env" ]; then
    if grep -q "MORPH_API_KEY" .env && grep -q "AUGMENT_API_KEY" .env; then
        echo -e "${GREEN}✓ API keys found in .env${NC}"
    else
        echo -e "${YELLOW}⚠️  API keys not configured in .env${NC}"
        echo ""
        echo "Add these to your .env file:"
        echo "MORPH_API_KEY=your_morph_key_here"
        echo "AUGMENT_API_KEY=your_augment_key_here"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
fi

# Success message
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Get API keys:"
echo "   • Morph: https://morphllm.com/dashboard"
echo "   • Augment: https://augmentcode.com"
echo ""
echo "2. Add to .env file:"
echo "   MORPH_API_KEY=your_morph_key"
echo "   AUGMENT_API_KEY=your_augment_key"
echo ""
echo "3. Test the integration:"
echo "   python test_enhanced_tools.py"
echo ""
echo "4. Restart Auto Claude"
echo ""
echo -e "${GREEN}🚀 You're ready to go!${NC}"
