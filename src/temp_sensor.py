#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temperature Sensor Module - DS18B20
Четене на температура от DS18B20 сензор
"""

import glob
import time
import logging

class DS18B20Sensor:
    """Клас за работа с DS18B20 температурен сензор"""
    
    def __init__(self, base_dir='/sys/bus/w1/devices/'):
        """
        Инициализация на сензора
        
        Args:
            base_dir: Базова директория за 1-Wire устройства
        """
        self.base_dir = base_dir
        self.device_file = None
        self._find_device()
    
    def _find_device(self):
        """Намира DS18B20 устройството"""
        try:
            device_folder = glob.glob(self.base_dir + '28*')[0]
            self.device_file = device_folder + '/w1_slave'
            logging.info(f"DS18B20 открит: {device_folder}")
        except IndexError:
            logging.error("DS18B20 сензор не е открит!")
            raise Exception("DS18B20 не е намерен. Провери свързването.")
    
    def _read_temp_raw(self):
        """Чете сурови данни от сензора"""
        try:
            with open(self.device_file, 'r') as f:
                return f.readlines()
        except Exception as e:
            logging.error(f"Грешка при четене: {e}")
            return None
    
    def read_temperature(self, retries=3):
        """
        Чете температурата от сензора
        
        Args:
            retries: Брой опити при грешка
            
        Returns:
            float: Температурата в °C или None при грешка
        """
        for attempt in range(retries):
            lines = self._read_temp_raw()
            
            if lines is None:
                time.sleep(0.5)
                continue
            
            # Провери за валидно четене (YES)
            if lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                continue
            
            # Извлечи температурата
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return round(temp_c, 2)
        
        logging.error(f"Не може да се прочете температура след {retries} опита")
        return None
    
    def read_temperature_f(self):
        """Връща температурата във Fahrenheit"""
        temp_c = self.read_temperature()
        if temp_c is not None:
            return round(temp_c * 9.0 / 5.0 + 32.0, 2)
        return None


def main():
    """Тестова функция"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        sensor = DS18B20Sensor()
        temp = sensor.read_temperature()
        
        if temp is not None:
            print(f"🌡️  Температура: {temp}°C")
            return 0
        else:
            print("❌ Грешка при четене на температура")
            return 1
    except Exception as e:
        print(f"❌ Грешка: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
