#!/bin/bash
# Stop services temporarily (without disabling)

set -e

echo "=========================================="
echo "Fermentation Controller - Stop Services"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script must be run as root (use sudo)"
    exit 1
fi

echo "Stopping all services..."
echo ""

# Stop timers
systemctl stop pump-morning.timer 2>/dev/null && echo "✓ Morning timer stopped" || echo "  Morning timer not running"
systemctl stop pump-evening.timer 2>/dev/null && echo "✓ Evening timer stopped" || echo "  Evening timer not running"

# Stop services
systemctl stop pump-morning.service 2>/dev/null && echo "✓ Morning service stopped" || echo "  Morning service not running"
systemctl stop pump-evening.service 2>/dev/null && echo "✓ Evening service stopped" || echo "  Evening service not running"

# Turn off relay
echo ""
echo "Turning off relay..."
python3 scripts/emergency-stop.py 2>/dev/null && echo "✓ Relay turned off" || echo "  (Could not access GPIO)"

echo ""
echo "✅ All services stopped"
echo ""
echo "Services remain enabled and will restart on reboot."
echo "To start services again, run: sudo ./scripts/start.sh"
