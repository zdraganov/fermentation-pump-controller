#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temperature Sensor Module - DS18B20
Reading temperature from DS18B20 sensor
"""

import glob
import time
import logging

class DS18B20Sensor:
    """Class for working with DS18B20 temperature sensor"""
    
    def __init__(self, base_dir='/sys/bus/w1/devices/'):
        """
        Initialize the sensor
        
        Args:
            base_dir: Base directory for 1-Wire devices
        """
        self.base_dir = base_dir
        self.device_file = None
        self._find_device()
    
    def _find_device(self):
        """Find DS18B20 device"""
        try:
            device_folder = glob.glob(self.base_dir + '28*')[0]
            self.device_file = device_folder + '/w1_slave'
            logging.info(f"DS18B20 found: {device_folder}")
        except IndexError:
            logging.error("DS18B20 sensor not found!")
            raise Exception("DS18B20 not found. Check wiring.")
    
    def _read_temp_raw(self):
        """Read raw data from sensor"""
        try:
            with open(self.device_file, 'r') as f:
                return f.readlines()
        except Exception as e:
            logging.error(f"Read error: {e}")
            return None
    
    def read_temperature(self, retries=3):
        """
        Read temperature from sensor
        
        Args:
            retries: Number of retry attempts on error
            
        Returns:
            float: Temperature in °C or None on error
        """
        for attempt in range(retries):
            lines = self._read_temp_raw()
            
            if lines is None:
                time.sleep(0.5)
                continue
            
            # Check for valid reading (YES)
            if lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                continue
            
            # Extract temperature
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return round(temp_c, 2)
        
        logging.error(f"Cannot read temperature after {retries} attempts")
        return None
    
    def read_temperature_f(self):
        """Return temperature in Fahrenheit"""
        temp_c = self.read_temperature()
        if temp_c is not None:
            return round(temp_c * 9.0 / 5.0 + 32.0, 2)
        return None


def main():
    """Test function"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        sensor = DS18B20Sensor()
        temp = sensor.read_temperature()
        
        if temp is not None:
            print(f"🌡️  Temperature: {temp}°C")
            return 0
        else:
            print("❌ Error reading temperature")
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
