#!/usr/bin/env python3
"""Temperature-controlled relay test"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import RPi.GPIO as GPIO
from temp_sensor import DS18B20Sensor

RELAY_PIN = 17
TEMP_THRESHOLD = 20.0

print("🧪 Temperature-Controlled Relay Test")
print(f"Threshold: {TEMP_THRESHOLD}°C")
print("Relay ON if temp < 20°C, OFF if temp >= 20°C")
print("Press Ctrl+C to stop")
print("-" * 50)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

sensor = DS18B20Sensor()

try:
    while True:
        temp = sensor.read_temperature()
        
        if temp is not None:
            if temp < TEMP_THRESHOLD:
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                status = "ON"
            else:
                GPIO.output(RELAY_PIN, GPIO.LOW)
                status = "OFF"
            
            print(f"Temperature: {temp:.2f}°C | Relay: {status}")
        else:
            print("❌ Cannot read temperature")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nStopped by user")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("✓ Cleanup complete")
