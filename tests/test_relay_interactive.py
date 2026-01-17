#!/usr/bin/env python3
"""Interactive relay test"""

import RPi.GPIO as GPIO
import sys

RELAY_PIN = 17

print("🧪 Interactive Relay Test")
print("Commands: O = On, F = Off, Q = Quit")
print("-" * 40)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

try:
    while True:
        cmd = input("Enter command (O/F/Q): ").strip().upper()
        
        if cmd == 'O':
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            print("✓ Relay ON")
        elif cmd == 'F':
            GPIO.output(RELAY_PIN, GPIO.LOW)
            print("✓ Relay OFF")
        elif cmd == 'Q':
            print("Exiting...")
            break
        else:
            print("❌ Invalid command. Use O, F, or Q")
            
except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("✓ Cleanup complete")
