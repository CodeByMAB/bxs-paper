.PHONY: all build pack verify clean

# Package identifier
PKG_ID := bitcoin-seconds

# Default target
all: build pack

# Build the Docker image and prepare package files
build:
	@echo "Building Bitcoin Seconds package..."
	@cd .. && bash start9/build.sh

# Pack the service into .s9pk file
pack:
	@echo "Packing service..."
	@start-sdk pack

# Verify the package
verify:
	@echo "Verifying package..."
	@start-sdk verify s9pk $(PKG_ID).s9pk

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -f $(PKG_ID).s9pk
	@rm -f docker_images.tar
	@rm -f docker_images.tgz

