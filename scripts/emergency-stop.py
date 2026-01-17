#!/usr/bin/env python3
"""
Emergency Relay Stop
Immediately turns off the relay (GPIO 17)
"""

import RPi.GPIO as GPIO

RELAY_PIN = 17  # BCM GPIO 17

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("✓ Relay turned OFF (GPIO 17)")
    GPIO.cleanup()
except Exception as e:
    print(f"❌ Error: {e}")
    GPIO.cleanup()
