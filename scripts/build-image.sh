#!/bin/bash
set -e

echo "🍓 Building custom Raspberry Pi image for use with Raspberry Pi Imager..."

# Variables
CACHE_DIR="cache"
OUTPUT_DIR="output"
BASE_IMAGE="$CACHE_DIR/2024-03-15-raspios-bookworm-arm64-lite.img.xz"
TIMESTAMP=$(date +%Y-%m-%d)
OUTPUT_IMAGE="$OUTPUT_DIR/fermentation-pi-$TIMESTAMP.img"

# Create directories
mkdir -p "$OUTPUT_DIR"

# Clean up old images
echo "Cleaning up old images..."
rm -f "$OUTPUT_DIR"/fermentation-pi-*.img

# Extract base image
echo "Extracting base image..."
xz -dc "$BASE_IMAGE" > "$OUTPUT_IMAGE"

# Expand image to have more space
echo "Expanding image by 4GB..."
dd if=/dev/zero bs=1M count=4096 >> "$OUTPUT_IMAGE"

# Resize partition
echo "Resizing partition..."
sudo parted "$OUTPUT_IMAGE" ---pretend-input-tty << EOF
resizepart
2
100%
Yes
EOF

# Mount the image
echo "Mounting image..."
LOOP_DEVICE=$(sudo losetup --find --partscan --show "$OUTPUT_IMAGE")
MOUNT_DIR="/tmp/rpi-mount"
sudo mkdir -p "$MOUNT_DIR"

# Resize filesystem to use all available space
echo "Resizing filesystem..."
sudo e2fsck -f -y "${LOOP_DEVICE}p2" || true
sudo resize2fs "${LOOP_DEVICE}p2"

sudo mount "${LOOP_DEVICE}p2" "$MOUNT_DIR"
sudo mount "${LOOP_DEVICE}p1" "$MOUNT_DIR/boot"

# Customize the image
echo "Customizing image..."

# Create empty project directory structure
sudo mkdir -p "$MOUNT_DIR/home/raspberry/fermentation-controller/src"
sudo mkdir -p "$MOUNT_DIR/home/raspberry/fermentation-controller/systemd"
sudo mkdir -p "$MOUNT_DIR/home/raspberry/fermentation-controller/logs"

# Create a README for the user
cat << 'README' | sudo tee "$MOUNT_DIR/home/raspberry/fermentation-controller/README.txt"
Fermentation Pump Controller

To deploy your code:
1. From your Mac: scp -r * pi@fermentation-pi.local:~/fermentation-controller/
2. On the Pi: cd ~/fermentation-controller && sudo ./install.sh

Or use git:
1. git clone https://github.com/zdraganov/fermentation-pump-controller.git
2. cd fermentation-pump-controller && sudo ./install.sh
README

# Set ownership (pi user is UID 1000)
sudo chown -R 1000:1000 "$MOUNT_DIR/home/raspberry/fermentation-controller"

# Enable 1-Wire
echo "dtoverlay=w1-gpio,gpiopin=4" | sudo tee -a "$MOUNT_DIR/boot/config.txt"

# Enable UART
echo "enable_uart=1" | sudo tee -a "$MOUNT_DIR/boot/config.txt"

# Install rpi-connect (chroot into the image)
echo "Installing rpi-connect..."
sudo mount --bind /dev "$MOUNT_DIR/dev"
sudo mount --bind /sys "$MOUNT_DIR/sys"
sudo mount --bind /proc "$MOUNT_DIR/proc"

sudo chroot "$MOUNT_DIR" /bin/bash << 'CHROOT'
apt-get clean
apt-get update
apt-get install -y rpi-connect
CHROOT

sudo umount "$MOUNT_DIR/proc"
sudo umount "$MOUNT_DIR/sys"
sudo umount "$MOUNT_DIR/dev"

echo "✅ rpi-connect installation attempted"

# Cleanup and unmount
echo "Cleaning up..."
sync
sleep 2
sudo umount "$MOUNT_DIR/boot" || true
sudo umount "$MOUNT_DIR" || true
sudo losetup -d "$LOOP_DEVICE" || true
sleep 1
sudo rmdir "$MOUNT_DIR" || true

echo "✅ Custom Raspberry Pi image created: $OUTPUT_IMAGE"
echo ""
echo "Next steps:"
echo "1. Open Raspberry Pi Imager"
echo "2. Choose OS → Use custom → Select: $OUTPUT_IMAGE"
echo "3. Click the settings gear (⚙️) to configure:"
echo "   - WiFi credentials"
echo "   - Hostname (e.g., fermentation-pi)"
echo "   - Enable SSH"
echo "   - Enable Raspberry Pi Connect"
echo "4. Flash to SD card"
echo "5. After boot, copy your code:"
echo "   scp -r * raspberry@raspberry.lan:~/fermentation-controller/"
echo "6. SSH in and run: cd ~/fermentation-controller && sudo ./install.sh"
echo "7. Sign in to rpi-connect: rpi-connect signin"
echo "8. Visit https://connect.raspberrypi.com to access remotely"
