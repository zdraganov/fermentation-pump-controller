#!/usr/bin/env python3
"""Тест на температурен сензор"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from temp_sensor import DS18B20Sensor

try:
    print("🧪 Тестване на DS18B20...")
    sensor = DS18B20Sensor()
    temp = sensor.read_temperature()
    if temp:
        print(f"✓ Температура: {temp}°C")
        exit(0)
    else:
        print("❌ Не може да се прочете температура")
        exit(1)
except Exception as e:
    print(f"❌ Грешка: {e}")
    exit(1)
