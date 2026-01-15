#!/bin/bash
set -e

echo "📝 Creating Raspberry Pi Imager manifest for custom image..."

# Find the latest image
LATEST_IMAGE=$(ls -t output/fermentation-pi-*.img 2>/dev/null | head -1)

if [ -z "$LATEST_IMAGE" ]; then
    echo "❌ No image found in output/ directory"
    echo "Run 'make build' first"
    exit 1
fi

FULL_PATH=$(realpath "$LATEST_IMAGE")
IMAGE_SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH")

echo "Found image: $FULL_PATH"

# Create os_list_local.json matching official format
cat > output/os_list_local.json << EOF
{
  "imager": {
    "latest_version": "2.0.3",
    "url": "https://www.raspberrypi.com/software/",
    "devices": [
      {
        "name": "Raspberry Pi 5",
        "tags": [
          "pi5-64bit",
          "pi5-32bit"
        ],
        "icon": "https://downloads.raspberrypi.com/imager/icons/RPi_5.png",
        "description": "Raspberry Pi 5, 500 / 500+, and Compute Module 5",
        "matching_type": "exclusive",
        "capabilities": []
      },
      {
        "name": "Raspberry Pi 4",
        "tags": [
          "pi4-64bit",
          "pi4-32bit"
        ],
        "default": false,
        "icon": "https://downloads.raspberrypi.com/imager/icons/RPi_4.png",
        "description": "Raspberry Pi 4 Model B, 400, and Compute Module 4 / 4S",
        "matching_type": "inclusive",
        "capabilities": []
      },
      {
        "name": "Raspberry Pi 3",
        "tags": [
          "pi3-64bit",
          "pi3-32bit"
        ],
        "default": false,
        "icon": "https://downloads.raspberrypi.com/imager/icons/RPi_3.png",
        "description": "Raspberry Pi 3 Model A+ / B / B+ and Compute Module 3 / 3+",
        "matching_type": "inclusive",
        "capabilities": []
      }
    ]
  },
  "os_list": [
    {
      "name": "Fermentation Pi Controller",
      "description": "Custom Raspberry Pi OS Lite (32-bit) with fermentation controller pre-installed. Use Raspberry Pi Imager customization to configure WiFi, SSH, and hostname.",
      "icon": "https://downloads.raspberrypi.com/raspios_armhf/Raspberry_Pi_OS_(32-bit).png",
      "url": "file://$FULL_PATH",
      "website": "https://github.com/zdraganov/fermentation-pump-controller",
      "release_date": "$(date +%Y-%m-%d)",
      "extract_size": $IMAGE_SIZE,
      "extract_sha256": "",
      "image_download_size": $IMAGE_SIZE,
      "image_download_sha256": "",
      "devices": [
        "pi3-32bit",
        "pi3-64bit",
        "pi4-32bit",
        "pi4-64bit",
        "pi5-64bit"
      ],
      "init_format": "systemd",
      "architecture": "armv8",
      "capabilities": [
        "rpi_connect",
        "i2c",
        "spi",
        "onewire",
        "serial"
      ]
    }
  ]
}
EOF

echo "✅ Created output/os_list_local.json"
echo ""
echo "To use with Raspberry Pi Imager:"
echo ""
echo "Option 1 - Launch with manifest:"
echo "  rpi-imager --repo $(pwd)/output/os_list_local.json"
echo ""
echo "Option 2 - Configure in settings:"
echo "  1. Open Raspberry Pi Imager"
echo "  2. Raspberry Pi Imager → Settings (Cmd+,)"
echo "  3. Content Repository → EDIT → Use custom file"
echo "  4. Select: $(pwd)/output/os_list_local.json"
echo "  5. APPLY & RESTART"
echo "  6. Look for 'Fermentation Pi Controller' in the OS list"
