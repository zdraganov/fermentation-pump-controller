#!/bin/bash

# Fermentation Pump Controller - Installation Script
# For Raspberry Pi (Raspbian/Raspberry Pi OS)

set -e

echo "🚀 Fermentation Pump Controller - Инсталация"
echo "=============================================="

# Проверка за root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Моля стартирай скрипта като root: sudo ./install.sh"
    exit 1
fi

# Актуализация на системата
echo "📦 Актуализация на пакети..."
apt-get update
apt-get upgrade -y

# Инсталиране на зависимости
echo "📦 Инсталиране на зависимости..."
apt-get install -y python3 python3-pip python3-dev git

# Инсталиране на Python библиотеки
echo "🐍 Инсталиране на Python библиотеки..."
pip3 install -r requirements.txt

# Активиране на 1-Wire за DS18B20
echo "🔧 Активиране на 1-Wire интерфейс..."
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt; then
    echo "dtoverlay=w1-gpio,gpiopin=4" >> /boot/config.txt
    echo "✓ 1-Wire активиран"
else
    echo "✓ 1-Wire вече е активиран"
fi

# Зареждане на модули
modprobe w1-gpio
modprobe w1-therm

# Създаване на директории
echo "📁 Създаване на директории..."
mkdir -p logs
touch logs/.gitkeep

# Копиране на конфигурационен файл
if [ ! -f config.yaml ]; then
    echo "⚙️ Копиране на конфигурационен файл..."
    cp config.yaml config.yaml
    echo "✓ Моля редактирай config.yaml според нуждите си"
fi

# Инсталиране на systemd services
echo "🔧 Инсталиране на systemd services..."
cp systemd/*.service /etc/systemd/system/
cp systemd/*.timer /etc/systemd/system/

# Актуализиране на пътищата в service файловете
PROJECT_DIR=$(pwd)
sed -i "s|/home/pi/fermentation-pump-controller|${PROJECT_DIR}|g" /etc/systemd/system/pump-*.service
sed -i "s|/home/pi/fermentation-pump-controller|${PROJECT_DIR}|g" /etc/systemd/system/fermentation-dashboard.service

# Reload systemd
systemctl daemon-reload

# Активиране на timers
echo "⏰ Активиране на таймери..."
systemctl enable pump-morning.timer
systemctl enable pump-evening.timer
systemctl start pump-morning.timer
systemctl start pump-evening.timer

# Активиране на web dashboard
echo "🌐 Активиране на web dashboard..."
systemctl enable fermentation-dashboard.service
systemctl start fermentation-dashboard.service

# Тестване на сензор
echo "🧪 Тестване на температурен сензор..."
if python3 tests/test_sensor.py; then
    echo "✓ Сензорът работи!"
else
    echo "⚠️ Проблем със сензора - провери свързването"
fi

# Показване на статус
echo ""
echo "✅ Инсталацията завърши успешно!"
echo ""
echo "📊 Статус на services:"
systemctl status pump-morning.timer --no-pager | grep Active
systemctl status pump-evening.timer --no-pager | grep Active
systemctl status fermentation-dashboard.service --no-pager | grep Active
echo ""
echo "🌐 Web dashboard: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "⚠️ ВАЖНО: Рестартирай Raspberry Pi за да влязат в сила промените:"
echo "   sudo reboot"
echo ""
echo "📚 Виж README.md за повече информация"
echo ""
