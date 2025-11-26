# 🥬 Fermentation Pump Controller

Автоматизирана система за контрол на помпа за ферментация с температурен мониторинг, базирана на Raspberry Pi.

## 🎯 Предназначение

Проектът автоматизира процеса на ферментация (киселене на зеле) чрез:
- Автоматично пускане на помпа 2 пъти дневно по 10 минути
- Непрекъснат мониторинг на температурата
- Защита при прегряване/преохлаждане
- Web интерфейс за наблюдение
- Логване и графики

## 🛠️ Хардуер

### Необходими компоненти:

| Компонент | Спецификация | Цена |
|-----------|--------------|------|
| Raspberry Pi | 3/4/Zero W | Имам |
| Неръждаема помпа 12V | 1100 L/h, food-grade | 50 лв |
| AC/DC адаптер | 220V → 12V 3A | 15 лв |
| Relay модул | 12V, оптично изолиран | 8 лв |
| DS18B20 сензор | Водоустойчив модул | 8 лв |
| Силиконов маркуч | 16mm, 3m, food-grade | 30 лв |
| Скоби и кабели | - | 10 лв |
| **ОБЩО** | | **~121 лв** |

Виж [пълния shopping list](docs/shopping_list.md)

## 🔌 Свързване
```
Raspberry Pi: ├─ Pin 1 (3.3V) → DS18B20 VCC ├─ Pin 2 (5V) → Relay VCC ├─ Pin 6 (GND) → Relay GND ├─ Pin 7 (GPIO 4) → DS18B20 Data ├─ Pin 9 (GND) → DS18B20 GND └─ Pin 11 (GPIO 17) → Relay IN
Relay → 12V Adapter → Pump
Виж [детайлна схема](docs/wiring_diagram.txt)
```

## 🚀 Инсталация

### Бърза инсталация:

```bash
git clone https://github.com/zdraganov/fermentation-pump-controller.git
cd fermentation-pump-controller
chmod +x install.sh
./install.sh
```

### Ръчна инсталация:

```bash
# 1. Клонирай repo
git clone https://github.com/zdraganov/fermentation-pump-controller.git
cd fermentation-pump-controller

# 2. Инсталирай зависимости
pip3 install -r requirements.txt

# 3. Активирай 1-Wire за DS18B20
sudo bash -c 'echo "dtoverlay=w1-gpio,gpiopin=4" >> /boot/config.txt'
sudo reboot

# 4. Конфигурирай настройките
nano config.yaml

# 5. Тествай системата
python3 tests/test_sensor.py
python3 tests/test_relay.py

# 6. Инсталирай systemd services
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pump-morning.timer pump-evening.timer
sudo systemctl enable fermentation-dashboard.service
sudo systemctl start fermentation-dashboard.service
```

## ⚙️ Конфигурация
Редактирай config.yaml:
```yaml
pump:
  run_time: 600  # секунди (10 минути)
  gpio_pin: 17

temperature:
  min: 15.0      # °C - минимална температура
  max: 30.0      # °C - максимална температура
  warning: 25.0  # °C - предупреждение
  check_interval: 30  # секунди

schedule:
  morning: "09:00"
  evening: "21:00"

logging:
  pump_log: "logs/fermentation.log"
  temp_log: "logs/temperature.log"
  level: "INFO"

web:
  enabled: true
  port: 5000
```

## 📊 Използване
Ръчно пускане на помпа:

```bash
python3 src/pump_control.py
```

Проверка на температура:
```bash
python3 src/temp_sensor.py
```

Web interface:
```bash
python3 src/web_dashboard.py
# Отвори: http://[IP-на-Pi]:5000
```

Графики:
```bash
python3 src/plot_temperature.py
# Генерира: temperature_graph.png
```

Логове:
```bash
tail -f logs/fermentation.log
tail -f logs/temperature.log
```

Статус на services:
```bash
sudo systemctl status pump-morning.timer
sudo systemctl status pump-evening.timer
sudo systemctl status fermentation-dashboard.service
```

## 📈 Мониторинг
Real-time температура:
```bash
watch -n 5 python3 src/temp_sensor.py
```

Web Dashboard:
Отвори в браузър: http://[IP-на-Pi]:5000
Логове в реално време:
```bash
tail -f logs/fermentation.log
```
## 🔧 Отстраняване на проблеми
Сензорът не се открива:
```bash
# Провери дали 1-Wire е активиран
ls /sys/bus/w1/devices/
# Трябва да видиш: 28-xxxxxxxxxxxx

# Ако не:
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

Relay не работи:
```bash
python3 tests/test_relay.py
```

Помпата не се включва:
* Провери захранването (12V)
* Провери свързването на relay
* Виж логовете за грешки

## 📚 Документация
* [Хардуер и свързване](docs/hardware.md)
* [Shopping list](docs/shopping_list.md)
* [Wiring diagram](docs/wiring_diagram.txt)

## 📧 Контакт
При въпроси: [zhivko.draganov@gmail.com]
