#!/bin/bash
# Uninstall script - Disables and removes systemd services

set -e

echo "=========================================="
echo "Fermentation Controller - Uninstall"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script must be run as root (use sudo)"
    exit 1
fi

echo "This will:"
echo "  - Stop all running services"
echo "  - Disable all timers and services"
echo "  - Remove systemd service files"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Stopping services..."

# Stop and disable timers
systemctl stop pump-morning.timer 2>/dev/null || true
systemctl stop pump-evening.timer 2>/dev/null || true
systemctl disable pump-morning.timer 2>/dev/null || true
systemctl disable pump-evening.timer 2>/dev/null || true
echo "✓ Timers stopped and disabled"

# Stop and disable services
systemctl stop pump-morning.service 2>/dev/null || true
systemctl stop pump-evening.service 2>/dev/null || true
systemctl disable pump-morning.service 2>/dev/null || true
systemctl disable pump-evening.service 2>/dev/null || true
echo "✓ Services stopped and disabled"

echo ""
echo "Removing systemd files..."

# Remove service files
rm -f /etc/systemd/system/pump-morning.timer
rm -f /etc/systemd/system/pump-evening.timer
rm -f /etc/systemd/system/pump-morning.service
rm -f /etc/systemd/system/pump-evening.service
echo "✓ Service files removed"

# Reload systemd
systemctl daemon-reload
echo "✓ Systemd reloaded"

# Turn off relay
echo "✓ Turning off relay..."
python3 scripts/emergency-stop.py 2>/dev/null || echo "  (Could not access GPIO)"

echo ""
echo "=========================================="
echo "✅ Uninstall complete!"
echo "=========================================="
echo ""
echo "Note: Project files and logs are still in place."
echo "To remove completely, delete the project directory."
