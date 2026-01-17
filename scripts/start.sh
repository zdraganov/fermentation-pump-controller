#!/bin/bash
# Start services

set -e

echo "=========================================="
echo "Fermentation Controller - Start Services"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script must be run as root (use sudo)"
    exit 1
fi

echo "Starting all services..."
echo ""

# Start timers
systemctl start pump-morning.timer && echo "✓ Morning timer started (will run at 09:00)"
systemctl start pump-evening.timer && echo "✓ Evening timer started (will run at 21:00)"

echo ""
echo "✅ All services started"
echo ""
echo "📅 Next scheduled runs:"
systemctl list-timers pump-morning.timer pump-evening.timer --no-pager
echo ""
echo "💡 To run pump manually: make run-pump"
echo "💡 To open TUI dashboard: make tui"
