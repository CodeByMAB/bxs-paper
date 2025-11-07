#!/bin/bash
# Build script for creating Start9 package
# Usage: ./start9/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION="0.1.0"

echo "════════════════════════════════════════════════════════════════"
echo " Bitcoin Seconds (BXS) - Start9 Package Builder"
echo " Version: $VERSION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "→ Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "✗ Error: Docker is not installed"
    echo "  Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "⚠ Warning: npm not found"
    echo "  You'll need npm to install embassy-sdk for final packaging"
fi

echo "✓ Prerequisites checked"
echo ""

# Build Docker image
echo "→ Building BXS Docker image..."
cd "$REPO_ROOT"

# Clean old build artifacts
rm -f "$SCRIPT_DIR/image.tar"
rm -f "$SCRIPT_DIR/docker_images.tar"
rm -f "$SCRIPT_DIR/docker_images.tgz"
rm -f "$SCRIPT_DIR"/*.s9pk

# Build Docker image with buildx and output directly to tar
# CRITICAL: Tag must be start9/$(PKG_ID)/main:$(VERSION) to match manifest.yaml "image: main"
# This is how Start9 resolves the image reference
echo "→ Building Docker image with buildx (tagged with /main)..."
docker buildx build \
    --tag start9/bitcoin-seconds/main:$VERSION \
    --platform linux/amd64 \
    -o type=docker,dest="$SCRIPT_DIR/image.tar" \
    -f Dockerfile \
    "$REPO_ROOT"

if [ $? -ne 0 ]; then
    echo "✗ Docker build failed"
    exit 1
fi

echo "✓ Docker image built and saved: start9/bitcoin-seconds/main:$VERSION"
echo ""

# Load image into Docker to verify it works and get image ID
echo "→ Loading image into Docker to verify..."
docker load -i "$SCRIPT_DIR/image.tar" > /dev/null 2>&1

# Verify image exists and get its ID
IMAGE_ID=$(docker inspect --format='{{.Id}}' start9/bitcoin-seconds/main:$VERSION 2>/dev/null)
if [ -z "$IMAGE_ID" ]; then
    echo "⚠ Warning: Could not get image ID after load"
else
    echo "→ Image ID: $IMAGE_ID"
fi

SIZE=$(du -h "$SCRIPT_DIR/image.tar" | cut -f1)
echo "✓ Docker image saved: image.tar ($SIZE)"
echo ""

# Ensure all scripts are executable
echo "→ Setting script permissions..."
chmod +x "$SCRIPT_DIR"/*.sh
echo "✓ Scripts are executable"
echo ""

# Create .env template if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "→ Creating .env template..."
    cat > "$SCRIPT_DIR/.env" <<EOF
# Bitcoin Seconds Configuration
# This file is automatically populated by Start9

MOCK_MODE=true
ALERT_DROP_PCT=0.2
ALERT_WINDOW_DAYS=14
T_MIN_SECS=1000
MU_MIN_SATS_PER_S=0.000001
PIPELINE_INTERVAL_SECONDS=600
API_PORT=8080
DB_PATH=/app/data/bxs.sqlite
EOF
    echo "✓ Created .env template"
else
    echo "✓ .env already exists"
fi
echo ""

# Verify required files
echo "→ Verifying package files..."
REQUIRED_FILES=(
    "manifest.yaml"
    "instructions.md"
    "icon.png"
    "image.tar"
    "properties.sh"
    "set-config.sh"
    "check-web.sh"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo ""
    echo "✗ Some required files are missing"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo " ✓ Build Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Package contents in: $SCRIPT_DIR"
echo ""
echo "Next steps:"
echo ""
echo "1. Install start-sdk (if not already installed):"
echo "   npm install -g @start9labs/start-sdk"
echo ""
echo "2. Pack the service:"
echo "   cd $REPO_ROOT"
echo "   start-sdk pack"
echo ""
echo "   This will create: bitcoin-seconds.s9pk"
echo ""
echo "3. Install on Start9:"
echo "   - Open Start9 web interface"
echo "   - Go to System > Sideload Service"
echo "   - Upload the .s9pk file"
echo "   - Configure and start the service"
echo ""
echo "4. Access the API:"
echo "   - Via LAN: https://bitcoin-seconds.local"
echo "   - Via Tor: (address shown in Start9 interface)"
echo "   - API docs: https://bitcoin-seconds.local/docs"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "For development/testing without Start9:"
echo ""
echo "  docker-compose -f start9/docker-compose.yml up"
echo "  curl http://localhost:8080/healthz"
echo "  curl http://localhost:8080/metrics/latest"
echo ""
echo "════════════════════════════════════════════════════════════════"
