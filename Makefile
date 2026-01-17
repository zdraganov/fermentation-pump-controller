.PHONY: help build-simple clean vm-create vm-shell vm-build vm-clean vm-restart install uninstall start stop run-pump emergency-stop tui

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
	multipass exec $(VM_NAME) -- bash -c "cd /workspace && make build"
	@echo "📝 Creating manifest on host..."
	chmod +x scripts/create-imager-manifest.sh
	./scripts/create-imager-manifest.sh

vm-clean: ## Delete Multipass VM
	@echo "🗑️  Deleting VM..."
	multipass delete $(VM_NAME)
	multipass purge

vm-restart: ## Restart Multipass VM
	@echo "🔄 Restarting VM..."
	multipass restart $(VM_NAME)

# Build targets
build: ## Build custom Raspberry Pi image for use with Raspberry Pi Imager
	@echo "🍓 Building image..."
	mkdir -p cache
	@if [ ! -f cache/2024-03-15-raspios-bookworm-arm64-lite.img.xz ]; then \
		echo "Downloading base image..."; \
		wget -O cache/2024-03-15-raspios-bookworm-arm64-lite.img.xz https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz; \
	fi
	chmod +x scripts/build-image.sh
	sudo ./scripts/build-image.sh

create-manifest: ## Create Raspberry Pi Imager manifest for customization support
	@echo "📝 Creating manifest..."
	chmod +x scripts/create-imager-manifest.sh
	./scripts/create-imager-manifest.sh

open-imager: ## Open Raspberry Pi Imager with custom manifest
	@echo "🖥️  Opening Raspberry Pi Imager..."
	/Applications/Raspberry\ Pi\ Imager.app/Contents/MacOS/rpi-imager --repo $(shell pwd)/output/os_list_local.json

# Deployment targets
sync: ## Sync code to Raspberry Pi
	@echo "🔄 Syncing code to Raspberry Pi..."
	rsync -avz --exclude 'venv' --exclude 'cache' --exclude 'output' --exclude '.git' --exclude '__pycache__' \
		. raspberry@raspberry.lan:~/fermentation-controller/
	@echo "✅ Code synced!"

# Service management targets
install: ## Install and enable systemd services on Pi
	@echo "📦 Installing services..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	sudo ./scripts/install.sh

uninstall: ## Uninstall and remove systemd services
	@echo "🗑️  Uninstalling services..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	sudo ./scripts/uninstall.sh

start: ## Start all systemd services
	@echo "▶️  Starting services..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	sudo ./scripts/start.sh

stop: ## Stop all systemd services
	@echo "⏸️  Stopping services..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	sudo ./scripts/stop.sh

run-pump: ## Manually trigger pump cycle
	@echo "▶️  Running pump cycle..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	~/fermentation-controller/venv/bin/python ~/fermentation-controller/src/pump_control.py

emergency-stop: ## Emergency stop - turn off relay immediately
	@echo "🛑 EMERGENCY STOP - Turning off relay..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	python3 scripts/emergency-stop.py

tui: ## Open TUI dashboard
	@echo "📊 Opening TUI dashboard..."
	@if [ "$$(hostname)" != "raspberry" ]; then \
		echo "⚠️  Run this on the Raspberry Pi, not locally"; \
		exit 1; \
	fi
	~/fermentation-controller/venv/bin/python ~/fermentation-controller/src/tui_dashboard.py

clean: ## Clean output and temporary files
	rm -rf $(OUTPUT_DIR)/*
	rm -rf cache/*

clean-cache: ## Clean cached base image
	rm -f cache/2024-03-15-raspios-bookworm-arm64-lite.img.xz
