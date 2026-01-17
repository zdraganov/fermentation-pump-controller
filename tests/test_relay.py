#!/usr/bin/env python3
"""Relay test"""

import RPi.GPIO as GPIO
import time

RELAY_PIN = 17

print("🧪 Testing relay...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    print("Turning on...")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(10)
    print("Turning off...")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("✓ Relay works!")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    GPIO.cleanup()
