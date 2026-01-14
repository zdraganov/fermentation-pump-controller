.PHONY: help build-simple clean vm-create vm-shell vm-build vm-clean vm-restart

OUTPUT_DIR := output
VM_NAME := pi-builder

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Multipass VM targets (for macOS)
vm-create: ## Create Multipass VM for building
	@echo "🖥️  Creating Multipass VM..."
	multipass launch --name $(VM_NAME) --cpus 4 --mem 8G --disk 30G
	multipass mount . $(VM_NAME):/workspace
	multipass exec $(VM_NAME) -- sudo apt-get update
	multipass exec $(VM_NAME) -- sudo apt-get install -y make
	@echo "✅ VM created and project mounted at /workspace"

vm-shell: ## Open shell in Multipass VM
	@echo "🐚 Opening VM shell..."
	multipass shell $(VM_NAME)

vm-build: ## Build image in Multipass VM
	@echo "🚀 Building image in VM..."
	multipass exec $(VM_NAME) -- bash -c "cd /workspace && make build-simple"

vm-clean: ## Delete Multipass VM
	@echo "🗑️  Deleting VM..."
	multipass delete $(VM_NAME)
	multipass purge

vm-restart: ## Restart Multipass VM
	@echo "🔄 Restarting VM..."
	multipass restart $(VM_NAME)

# Build targets
build-simple: ## Build custom Raspberry Pi image
	@echo "🍓 Building image..."
	mkdir -p cache
	@if [ ! -f cache/2024-03-15-raspios-bookworm-arm64-lite.img.xz ]; then \
		echo "Downloading base image..."; \
		wget -O cache/2024-03-15-raspios-bookworm-arm64-lite.img.xz https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz; \
	fi
	chmod +x scripts/build-image.sh
	sudo ./scripts/build-image.sh

clean: ## Clean output and temporary files
	rm -rf $(OUTPUT_DIR)/*
	rm -rf cache/*
