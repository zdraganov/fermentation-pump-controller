#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pump Control Module
Основен модул за управление на помпата с температурен мониторинг
"""

import RPi.GPIO as GPIO
import time
import yaml
import logging
import sys
from datetime import datetime
from pathlib import Path

# Добави src директорията в path
sys.path.insert(0, str(Path(__file__).parent))
from temp_sensor import DS18B20Sensor


class PumpController:
    """Контролер на помпата"""
    
    def __init__(self, config_file='config.yaml'):
        """
        Инициализация на контролера
        
        Args:
            config_file: Път към конфигурационен файл
        """
        self.config = self._load_config(config_file)
        self._setup_logging()
        self._setup_gpio()
        
        try:
            self.temp_sensor = DS18B20Sensor()
        except Exception as e:
            logging.error(f"Не може да се инициализира температурен сензор: {e}")
            self.temp_sensor = None
    
    def _load_config(self, config_file):
        """Зарежда конфигурацията"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default конфигурация
            return {
                'pump': {'run_time': 600, 'gpio_pin': 17},
                'temperature': {
                    'min': 15.0, 'max': 30.0, 'warning': 25.0,
                    'check_interval': 30
                },
                'logging': {
                    'pump_log': 'logs/fermentation.log',
                    'level': 'INFO'
                }
            }
    
    def _setup_logging(self):
        """Настройва логването"""
        log_file = self.config['logging']['pump_log']
        log_level = getattr(logging, self.config['logging']['level'])
        
        # Създай директория ако не съществува
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=log_file,
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Добави и конзолен output
        console = logging.StreamHandler()
        console.setLevel(log_level)
        logging.getLogger('').addHandler(console)
    
    def _setup_gpio(self):
        """Настройва GPIO пиновете"""
        self.relay_pin = self.config['pump']['gpio_pin']
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.LOW)
        logging.info(f"GPIO {self.relay_pin} инициализиран")
    
    def pump_on(self):
        """Включва помпата"""
        GPIO.output(self.relay_pin, GPIO.HIGH)
        logging.info("✓ Помпа ВКЛЮЧЕНА")
    
    def pump_off(self):
        """Изключва помпата"""
        GPIO.output(self.relay_pin, GPIO.LOW)
        logging.info("✓ Помпа ИЗКЛЮЧЕНА")
    
    def check_temperature_safe(self, temp):
        """
        Проверява дали температурата е в безопасен диапазон
        
        Args:
            temp: Температура в °C
            
        Returns:
            bool: True ако е безопасно
        """
        temp_config = self.config['temperature']
        
        if temp < temp_config['min']:
            logging.warning(
                f"⚠️ Температурата е твърде ниска "
                f"({temp}°C < {temp_config['min']}°C)"
            )
            return False
        
        if temp > temp_config['max']:
            logging.error(
                f"❌ Температурата е твърде висока "
                f"({temp}°C > {temp_config['max']}°C)"
            )
            return False
        
        if temp > temp_config['warning']:
            logging.warning(
                f"⚠️ ВНИМАНИЕ: Висока температура ({temp}°C)"
            )
        
        return True
    
    def run_cycle(self):
        """
        Изпълнява един цикъл на помпата с температурен мониторинг
        
        Returns:
            bool: True при успех
        """
        logging.info("="*50)
        logging.info("🚀 Стартиране на цикъл на помпа")
        
        # Провери началната температура
        if self.temp_sensor:
            temp = self.temp_sensor.read_temperature()
            if temp is None:
                logging.error("❌ Не може да се прочете температура!")
                return False
            
            logging.info(f"🌡️  Начална температура: {temp}°C")
            
            if not self.check_temperature_safe(temp):
                logging.warning("⚠️ Прескачам цикъла поради температура")
                return False
            
            initial_temp = temp
        else:
            logging.warning("⚠️ Няма температурен сензор - продължавам без проверка")
            initial_temp = None
        
        # Стартирай помпата
        self.pump_on()
        
        # Работи определено време със мониторинг
        run_time = self.config['pump']['run_time']
        check_interval = self.config['temperature']['check_interval']
        elapsed = 0
        
        try:
            while elapsed < run_time:
                sleep_time = min(check_interval, run_time - elapsed)
                time.sleep(sleep_time)
                elapsed += sleep_time
                
                # Провери температурата
                if self.temp_sensor:
                    temp = self.temp_sensor.read_temperature()
                    if temp is not None:
                        logging.info(
                            f"🌡️  Температура: {temp}°C | "
                            f"Време: {elapsed}/{run_time}s"
                        )
                        
                        # Спри при критична температура
                        if temp > self.config['temperature']['max']:
                            logging.error(f"❌ КРИТИЧНА ТЕМПЕРАТУРА! Спиране!")
                            self.pump_off()
                            return False
                
                progress = (elapsed / run_time) * 100
                logging.info(f"⏱️  Прогрес: {progress:.1f}%")
            
            # Нормално завършване
            self.pump_off()
            
            # Финална температура
            if self.temp_sensor:
                final_temp = self.temp_sensor.read_temperature()
                if final_temp and initial_temp:
                    temp_change = final_temp - initial_temp
                    logging.info(f"🌡️  Крайна температура: {final_temp}°C")
                    logging.info(f"📊 Промяна: {temp_change:+.2f}°C")
            
            logging.info("✅ Цикълът завърши успешно")
            return True
            
        except KeyboardInterrupt:
            logging.warning("⚠️ Прекъснато от потребител")
            self.pump_off()
            return False
        except Exception as e:
            logging.error(f"❌ Грешка: {e}")
            self.pump_off()
            return False
        finally:
            logging.info("="*50)
    
    def cleanup(self):
        """Почиства GPIO ресурсите"""
        GPIO.cleanup()
        logging.info("GPIO cleanup завърши")


def main():
    """Главна функция"""
    controller = None
    try:
        controller = PumpController()
        success = controller.run_cycle()
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Критична грешка: {e}")
        return 1
    finally:
        if controller:
            controller.cleanup()


if __name__ == "__main__":
    exit(main())
