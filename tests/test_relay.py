#!/usr/bin/env python3
"""Тест на relay"""

import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

print("🧪 Тестване на relay...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    print("Включване...")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(2)
    print("Изключване...")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("✓ Relay работи!")
except Exception as e:
    print(f"❌ Грешка: {e}")
finally:
    GPIO.cleanup()
