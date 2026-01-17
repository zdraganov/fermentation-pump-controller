# 🥬 Fermentation Pump Controller

Automated fermentation pump control system with temperature monitoring, based on Raspberry Pi.

## 🎯 Purpose

This project automates the fermentation process (cabbage pickling) through:
- Automatic pump activation 2 times daily for 10 minutes
- Continuous temperature monitoring
- Protection against overheating/overcooling
- TUI (Terminal User Interface) for monitoring and control
- Logging and graphs

## 🛠️ Hardware

### Required Components:

| Component | Specification | Price |
|-----------|--------------|------|
| Raspberry Pi | 3/4/Zero W | Have |
| Stainless Steel Pump 12V | 1100 L/h, food-grade | $50 |
| AC/DC Adapter | 220V → 12V 3A | $15 |
| Relay Module | 12V, optically isolated | $8 |
| DS18B20 Sensor | Waterproof module | $8 |
| Silicone Hose | 16mm, 3m, food-grade | $30 |
| Clamps and Cables | - | $10 |
| **TOTAL** | | **~$121** |

See [full shopping list](docs/shopping_list.md)

## 🔌 Wiring
```
Raspberry Pi:
├─ Pin 1 (3.3V) → DS18B20 VCC
├─ Pin 2 (5V) → Relay VCC
├─ Pin 6 (GND) → Relay GND
├─ Pin 7 (GPIO 4) → DS18B20 Data
├─ Pin 9 (GND) → DS18B20 GND
└─ Pin 11 (GPIO 17) → Relay IN

Relay → 12V Adapter → Pump
```

See [detailed wiring diagram](docs/wiring_diagram.txt)

## 🚀 Installation

### Quick Installation:

```bash
git clone https://github.com/zdraganov/fermentation-pump-controller.git
cd fermentation-pump-controller
sudo make install
```

### Manual Installation:

```bash
# 1. Clone repo
git clone https://github.com/zdraganov/fermentation-pump-controller.git
cd fermentation-pump-controller

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Enable 1-Wire for DS18B20
sudo bash -c 'echo "dtoverlay=w1-gpio,gpiopin=4" >> /boot/config.txt'
sudo reboot

# 4. Configure settings
nano config.yaml

# 5. Test system
python3 tests/test_sensor.py
python3 tests/test_relay.py

# 6. Install systemd services
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pump-morning.timer pump-evening.timer
```

## ⚙️ Configuration

Edit config.yaml:
```yaml
pump:
  run_time: 600  # seconds (10 minutes)
  gpio_pin: 17   # GPIO pin for relay (BCM 17 = Physical Pin 11)

temperature:
  min: 15.0      # °C - minimum operating temperature
  max: 30.0      # °C - maximum operating temperature
  warning: 25.0  # °C - warning temperature
  check_interval: 30  # seconds between checks
  gpio_pin: 4    # GPIO pin for DS18B20 (BCM 4 = Physical Pin 7)

schedule:
  morning: "09:00"  # Morning cycle
  evening: "21:00"  # Evening cycle

logging:
  pump_log: "logs/fermentation.log"
  temp_log: "logs/temperature.log"
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

## 📊 Usage

### Service Management:
```bash
make start          # Start all services
make stop           # Stop all services
make uninstall      # Remove all services
```

### Manual Operations:
```bash
make run-pump       # Manually trigger pump cycle
make emergency-stop # Emergency stop - turn off relay immediately
make tui            # Open TUI dashboard
```

### TUI Dashboard:
```bash
make tui
```

Controls:
- `R` - Run pump cycle
- `S` - Stop pump
- `L` - View full log (scrollable)
- `Q` - Quit

### Testing:
```bash
python3 tests/test_sensor.py          # Test temperature sensor
python3 tests/test_relay.py            # Test relay
python3 tests/test_gpio_pins.py        # Verify GPIO pin configuration
```

### Logs:
```bash
tail -f logs/fermentation.log
tail -f logs/temperature.log
```

### Service Status:
```bash
sudo systemctl status pump-morning.timer
sudo systemctl status pump-evening.timer
systemctl list-timers  # Show next scheduled runs
```

## 📈 Monitoring

Real-time temperature:
```bash
watch -n 5 python3 src/temp_sensor.py
```

TUI Dashboard:
```bash
make tui
```

Real-time logs:
```bash
tail -f logs/fermentation.log
```

## 🔧 Troubleshooting

Sensor not detected:
```bash
# Check if 1-Wire is enabled
ls /sys/bus/w1/devices/
# Should see: 28-xxxxxxxxxxxx

# If not:
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

Relay not working:
```bash
python3 tests/test_relay.py
# Or verify GPIO pins:
python3 tests/test_gpio_pins.py
```

Pump not turning on:
* Check power supply (12V)
* Check relay wiring
* Check logs for errors
* Use emergency stop if needed: `make emergency-stop`

## 📚 Documentation
* [Hardware and Wiring](docs/hardware.md)
* [Shopping List](docs/shopping_list.md)
* [Wiring Diagram](docs/wiring_diagram.txt)

## 📧 Contact
For questions: [zhivko.draganov@gmail.com]
