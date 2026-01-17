#!/usr/bin/env python3
"""Temperature sensor test"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from temp_sensor import DS18B20Sensor

try:
    print("🧪 Testing DS18B20...")
    sensor = DS18B20Sensor()
    temp = sensor.read_temperature()
    if temp:
        print(f"✓ Temperature: {temp}°C")
        exit(0)
    else:
        print("❌ Cannot read temperature")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
