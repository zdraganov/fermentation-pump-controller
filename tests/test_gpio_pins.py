#!/usr/bin/env python3
"""
GPIO Pin Verification Test
Tests the actual GPIO pins to confirm correct wiring
"""

import RPi.GPIO as GPIO
import time
import sys

# Pin configuration from config.yaml (BCM numbering)
RELAY_PIN = 17  # BCM GPIO 17 (Physical pin 11)
TEMP_SENSOR_PIN = 4  # BCM GPIO 4 (Physical pin 7)

def test_relay_pin():
    """Test relay control on GPIO pin"""
    print(f"\n{'='*50}")
    print(f"Testing RELAY on GPIO {RELAY_PIN}")
    print(f"{'='*50}")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    
    try:
        print("\n1. Turning relay ON...")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("   ✓ Relay should be ON now")
        print("   → Listen for relay click")
        print("   → Check if pump is running")
        input("\n   Press ENTER to continue...")
        
        print("\n2. Turning relay OFF...")
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("   ✓ Relay should be OFF now")
        print("   → Listen for relay click")
        print("   → Check if pump stopped")
        input("\n   Press ENTER to continue...")
        
        print("\n3. Quick ON/OFF test (3 cycles)...")
        for i in range(3):
            print(f"   Cycle {i+1}/3: ON", end="", flush=True)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            time.sleep(1)
            print(" → OFF", flush=True)
            GPIO.output(RELAY_PIN, GPIO.LOW)
            time.sleep(1)
        
        print("\n✅ Relay test complete!")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        return False
    finally:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        GPIO.cleanup()

def test_temperature_sensor():
    """Test DS18B20 temperature sensor"""
    print(f"\n{'='*50}")
    print(f"Testing TEMPERATURE SENSOR on GPIO {TEMP_SENSOR_PIN}")
    print(f"{'='*50}")
    
    import glob
    
    try:
        # Check if 1-Wire is enabled
        device_folder = glob.glob('/sys/bus/w1/devices/28*')
        
        if not device_folder:
            print("\n❌ No DS18B20 sensor found!")
            print("\nTroubleshooting:")
            print("1. Check if 1-Wire is enabled:")
            print("   grep 'dtoverlay=w1-gpio' /boot/config.txt")
            print(f"2. Verify GPIO pin {TEMP_SENSOR_PIN} is configured for 1-Wire")
            print("3. Check sensor wiring:")
            print("   - VCC → 3.3V (Pin 1)")
            print(f"   - DATA → GPIO {TEMP_SENSOR_PIN} (Pin 7)")
            print("   - GND → Ground (Pin 9)")
            print("4. Reboot after enabling 1-Wire")
            return False
        
        print(f"\n✓ Sensor found: {device_folder[0]}")
        
        # Read temperature
        device_file = device_folder[0] + '/w1_slave'
        
        print("\nReading temperature (5 samples)...")
        for i in range(5):
            with open(device_file, 'r') as f:
                lines = f.readlines()
            
            if lines[0].strip()[-3:] == 'YES':
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos+2:]
                    temp_c = float(temp_string) / 1000.0
                    print(f"   Sample {i+1}: {temp_c:.2f}°C")
                    time.sleep(1)
            else:
                print(f"   Sample {i+1}: Read error, retrying...")
                time.sleep(1)
        
        print("\n✅ Temperature sensor test complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*50)
    print("GPIO PIN VERIFICATION TEST")
    print("="*50)
    print("\nThis script will test:")
    print(f"1. Relay control on GPIO {RELAY_PIN}")
    print(f"2. Temperature sensor on GPIO {TEMP_SENSOR_PIN}")
    print("\nMake sure all hardware is connected!")
    
    response = input("\nContinue? (y/n): ").lower()
    if response != 'y':
        print("Test cancelled.")
        return 1
    
    # Test relay
    relay_ok = test_relay_pin()
    
    # Test temperature sensor
    temp_ok = test_temperature_sensor()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Relay (GPIO {RELAY_PIN}):     {'✅ PASS' if relay_ok else '❌ FAIL'}")
    print(f"Temperature (GPIO {TEMP_SENSOR_PIN}): {'✅ PASS' if temp_ok else '❌ FAIL'}")
    print("="*50)
    
    if relay_ok and temp_ok:
        print("\n✅ All tests passed! GPIO pins are correctly configured.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check wiring and configuration.")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        GPIO.cleanup()
        exit(1)
