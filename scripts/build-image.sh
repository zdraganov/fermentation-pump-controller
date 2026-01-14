#!/bin/bash
set -e

echo "🍓 Building custom Raspberry Pi image..."

# Variables
CACHE_DIR="cache"
OUTPUT_DIR="output"
BASE_IMAGE="$CACHE_DIR/2024-03-15-raspios-bookworm-arm64-lite.img.xz"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
OUTPUT_IMAGE="$OUTPUT_DIR/fermentation-pi-$TIMESTAMP.img"

# Create directories
mkdir -p "$OUTPUT_DIR"

# Extract base image
echo "Extracting base image..."
xz -dc "$BASE_IMAGE" > "$OUTPUT_IMAGE"

# Mount the image
echo "Mounting image..."
LOOP_DEVICE=$(sudo losetup --find --partscan --show "$OUTPUT_IMAGE")
MOUNT_DIR="/tmp/rpi-mount"
sudo mkdir -p "$MOUNT_DIR"
sudo mount "${LOOP_DEVICE}p2" "$MOUNT_DIR"
sudo mount "${LOOP_DEVICE}p1" "$MOUNT_DIR/boot"

# Customize the image
echo "Customizing image..."

# Enable SSH
sudo touch "$MOUNT_DIR/boot/ssh"

# Copy project files
sudo mkdir -p "$MOUNT_DIR/home/pi/fermentation-controller"
sudo cp -r src "$MOUNT_DIR/home/pi/fermentation-controller/"
sudo cp -r systemd "$MOUNT_DIR/home/pi/fermentation-controller/"
sudo cp config.yaml "$MOUNT_DIR/home/pi/fermentation-controller/"
sudo cp requirements.txt "$MOUNT_DIR/home/pi/fermentation-controller/"
sudo cp install.sh "$MOUNT_DIR/home/pi/fermentation-controller/"

# Set ownership (pi user is UID 1000)
sudo chown -R 1000:1000 "$MOUNT_DIR/home/pi/fermentation-controller"

# Enable 1-Wire
echo "dtoverlay=w1-gpio,gpiopin=4" | sudo tee -a "$MOUNT_DIR/boot/config.txt"

# Cleanup and unmount
echo "Cleaning up..."
sync
sudo umount "$MOUNT_DIR/boot"
sudo umount "$MOUNT_DIR"
sudo rmdir "$MOUNT_DIR"
sudo losetup -d "$LOOP_DEVICE"

echo "✅ Custom Raspberry Pi image created: $OUTPUT_IMAGE"
echo "Flash it to SD card with: sudo dd if=$OUTPUT_IMAGE of=/dev/sdX bs=4M status=progress"