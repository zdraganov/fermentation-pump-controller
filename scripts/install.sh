#!/bin/bash

# Fermentation Pump Controller - Installation Script
# For Raspberry Pi (Raspbian/Raspberry Pi OS)

set -e

echo "🚀 Fermentation Pump Controller - Installation"
echo "=============================================="

# Check for root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo ./install.sh"
    exit 1
fi

# Update system
echo "📦 Updating packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y python3 python3-pip python3-dev python3-venv git

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Install Python libraries
echo "🐍 Installing Python libraries..."
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# Load config and generate systemd timer files
echo "⚙️  Generating systemd timer files from config..."
venv/bin/python3 << 'PYTHON_SCRIPT'
import yaml
from pathlib import Path

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

morning_time = config['schedule']['morning']
evening_time = config['schedule']['evening']

# Generate morning timer
morning_timer = f"""[Unit]
Description=Fermentation Pump Morning Timer

[Timer]
OnCalendar=*-*-* {morning_time}:00
Persistent=false

[Install]
WantedBy=timers.target
"""

# Generate evening timer
evening_timer = f"""[Unit]
Description=Fermentation Pump Evening Timer

[Timer]
OnCalendar=*-*-* {evening_time}:00
Persistent=false

[Install]
WantedBy=timers.target
"""

# Write timer files
Path('systemd/pump-morning.timer').write_text(morning_timer)
Path('systemd/pump-evening.timer').write_text(evening_timer)

print(f"✓ Morning timer: {morning_time}")
print(f"✓ Evening timer: {evening_time}")
PYTHON_SCRIPT

# Enable 1-Wire for DS18B20
echo "🔧 Enabling 1-Wire interface..."
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
    echo "dtoverlay=w1-gpio,gpiopin=4" >> /boot/config.txt
    echo "✓ 1-Wire enabled"
else
    echo "✓ 1-Wire already enabled"
fi

# Load modules
modprobe w1-gpio
modprobe w1-therm

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
touch logs/.gitkeep

# Copy config file
if [ ! -f config.yaml ]; then
    echo "⚙️ Copying config file..."
    cp config.yaml config.yaml
    echo "✓ Please edit config.yaml according to your needs"
fi

# Install systemd services
echo "🔧 Installing systemd services..."
cp systemd/*.service /etc/systemd/system/
cp systemd/*.timer /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable timers (but don't start them yet)
echo "⏰ Enabling timers..."
systemctl enable pump-morning.timer
systemctl enable pump-evening.timer
echo "✓ Timers enabled (will start on next boot)"

# Test sensor
echo "🧪 Testing temperature sensor..."
if python3 tests/test_sensor.py; then
    echo "✓ Sensor works!"
else
    echo "⚠️ Sensor problem - check wiring"
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📊 Services enabled (will start on reboot):"
echo "   - pump-morning.timer (09:00)"
echo "   - pump-evening.timer (21:00)"
echo ""
echo "To start services now without rebooting:"
echo "   sudo ./scripts/start.sh"
echo ""
echo "To open TUI dashboard:"
echo "   make tui"
echo ""
echo "⚠️ IMPORTANT: Reboot Raspberry Pi for 1-Wire changes:"
echo "   sudo reboot"
echo ""
echo "📚 See README.md for more information"
echo ""
