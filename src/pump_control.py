#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pump Control Module
Main module for pump control with temperature monitoring
"""

import RPi.GPIO as GPIO
import time
import yaml
import logging
import sys
import os
import signal
import atexit
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))
from temp_sensor import DS18B20Sensor


class PumpController:
    """Pump controller"""
    
    LOCK_FILE = Path('/tmp/fermentation_pump.lock')
    STATE_FILE = Path('/tmp/fermentation_pump.state')
    
    def __init__(self, config_file='config.yaml'):
        """
        Initialize the controller
        
        Args:
            config_file: Path to configuration file
        """
        # Check if another instance is running
        if self._is_already_running():
            raise RuntimeError("Pump controller is already running")
        
        # Create lock file with our PID
        self.LOCK_FILE.write_text(str(os.getpid()))
        self._write_state('initializing')
        
        # Register cleanup handlers
        atexit.register(self._cleanup_files)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.config = self._load_config(config_file)
        self._setup_logging()
        self._setup_gpio()
        
        try:
            self.temp_sensor = DS18B20Sensor()
        except Exception as e:
            logging.error(f"Cannot initialize temperature sensor: {e}")
            self.temp_sensor = None
        
        self._write_state('ready')
    
    def _is_already_running(self):
        """Check if another pump controller instance is running"""
        if self.LOCK_FILE.exists():
            try:
                pid = int(self.LOCK_FILE.read_text().strip())
                # Check if process exists
                os.kill(pid, 0)
                # Verify it's actually our process by checking cmdline
                try:
                    with open(f'/proc/{pid}/cmdline', 'r') as f:
                        cmdline = f.read().replace('\x00', ' ')
                        # Check if it's running pump_control.py
                        if 'pump_control.py' not in cmdline and 'pump_control' not in cmdline:
                            # Different process, remove stale lock
                            self.LOCK_FILE.unlink(missing_ok=True)
                            return False
                except FileNotFoundError:
                    # Process doesn't exist
                    self.LOCK_FILE.unlink(missing_ok=True)
                    return False
                return True
            except (OSError, ValueError):
                # Stale lock file, remove it
                self.LOCK_FILE.unlink(missing_ok=True)
        return False
    
    def _write_state(self, state):
        """Write current state to state file"""
        try:
            self.STATE_FILE.write_text(state)
        except:
            pass
    
    @staticmethod
    def get_state():
        """Get current pump state (static method for external access)"""
        state_file = Path('/tmp/fermentation_pump.state')
        lock_file = Path('/tmp/fermentation_pump.lock')
        
        if not lock_file.exists():
            return 'idle'
        
        try:
            pid = int(lock_file.read_text().strip())
            # Check if process exists
            os.kill(pid, 0)
            # Verify it's actually our process
            try:
                with open(f'/proc/{pid}/cmdline', 'r') as f:
                    cmdline = f.read().replace('\x00', ' ')
                    if 'pump_control.py' not in cmdline and 'pump_control' not in cmdline:
                        # Different process, clean up
                        lock_file.unlink(missing_ok=True)
                        state_file.unlink(missing_ok=True)
                        return 'idle'
            except FileNotFoundError:
                # Process doesn't exist
                lock_file.unlink(missing_ok=True)
                state_file.unlink(missing_ok=True)
                return 'idle'
            
            if state_file.exists():
                return state_file.read_text().strip()
            return 'running'
        except (OSError, ValueError):
            # Stale files
            lock_file.unlink(missing_ok=True)
            state_file.unlink(missing_ok=True)
            return 'idle'
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        logging.warning(f"Received signal {signum}, shutting down...")
        self._emergency_shutdown()
        sys.exit(0)
    
    def _emergency_shutdown(self):
        """Emergency shutdown - turn off pump and cleanup"""
        try:
            GPIO.output(self.relay_pin, GPIO.LOW)
        except:
            pass
        try:
            GPIO.cleanup()
        except:
            pass
        self._cleanup_files()
    
    def _cleanup_files(self):
        """Clean up lock and state files"""
        self.LOCK_FILE.unlink(missing_ok=True)
        self.STATE_FILE.unlink(missing_ok=True)
    
    def _load_config(self, config_file):
        """Load configuration"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                'pump': {'run_time': 600, 'gpio_pin': 17},
                'temperature': {
                    'min': 15.0, 'max': 30.0, 'warning': 25.0,
                    'check_interval': 30, 'gpio_pin': 4
                },
                'logging': {
                    'pump_log': 'logs/fermentation.log',
                    'level': 'INFO'
                }
            }
    
    def _setup_logging(self):
        """Setup logging"""
        log_file = self.config['logging']['pump_log']
        log_level = getattr(logging, self.config['logging']['level'])
        
        # Create directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=log_file,
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console output
        console = logging.StreamHandler()
        console.setLevel(log_level)
        logging.getLogger('').addHandler(console)
    
    def _setup_gpio(self):
        """Setup GPIO pins"""
        self.relay_pin = self.config['pump']['gpio_pin']
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        GPIO.output(self.relay_pin, GPIO.LOW)
        logging.info(f"GPIO {self.relay_pin} initialized")
    
    def pump_on(self):
        """Turn pump ON"""
        GPIO.output(self.relay_pin, GPIO.HIGH)
        self._write_state('pump_on')
        logging.info("✓ Pump ON")
    
    def pump_off(self):
        """Turn pump OFF"""
        GPIO.output(self.relay_pin, GPIO.LOW)
        self._write_state('pump_off')
        logging.info("✓ Pump OFF")
    
    def check_temperature_safe(self, temp):
        """
        Check if temperature is in safe range
        
        Args:
            temp: Temperature in C
            
        Returns:
            bool: True if safe
        """
        temp_config = self.config['temperature']
        
        if temp < temp_config['min']:
            logging.warning(
                f"⚠️ Temperature too low "
                f"({temp}C < {temp_config['min']}C)"
            )
            return False
        
        if temp > temp_config['max']:
            logging.error(
                f"❌ Temperature too high "
                f"({temp}C > {temp_config['max']}C)"
            )
            return False
        
        if temp > temp_config['warning']:
            logging.warning(
                f"⚠️ WARNING: High temperature ({temp}C)"
            )
        
        return True
    
    @staticmethod
    def get_temperature():
        """Get current temperature (static method for external access)"""
        try:
            sensor = DS18B20Sensor()
            return sensor.read_temperature()
        except:
            return None
    
    def run_cycle(self):
        """
        Run one pump cycle with temperature monitoring
        
        Returns:
            bool: True on success
        """
        self._write_state('cycle_starting')
        logging.info("="*50)
        logging.info("🚀 Starting pump cycle")
        
        # Check initial temperature
        if self.temp_sensor:
            temp = self.temp_sensor.read_temperature()
            if temp is None:
                logging.error("❌ Cannot read temperature!")
                return False
            
            logging.info(f"🌡️  Initial temperature: {temp}C")
            
            if not self.check_temperature_safe(temp):
                logging.warning("⚠️ Skipping cycle due to temperature")
                return False
            
            initial_temp = temp
        else:
            logging.warning("⚠️ No temperature sensor - continuing without check")
            initial_temp = None
        
        # Start pump
        self.pump_on()
        
        # Run for specified time with monitoring
        run_time = self.config['pump']['run_time']
        check_interval = self.config['temperature']['check_interval']
        elapsed = 0
        
        try:
            while elapsed < run_time:
                sleep_time = min(check_interval, run_time - elapsed)
                time.sleep(sleep_time)
                elapsed += sleep_time
                
                # Check temperature
                if self.temp_sensor:
                    self._write_state('monitoring')
                    temp = self.temp_sensor.read_temperature()
                    if temp is not None:
                        logging.info(
                            f"🌡️  Temperature: {temp}C | "
                            f"Time: {elapsed}/{run_time}s"
                        )
                        
                        # Stop on critical temperature
                        if temp > self.config['temperature']['max']:
                            logging.error(f"❌ CRITICAL TEMPERATURE! Stopping!")
                            self.pump_off()
                            return False
                
                progress = (elapsed / run_time) * 100
                logging.info(f"⏱️  Progress: {progress:.1f}%")
            
            # Normal completion
            self.pump_off()
            
            # Final temperature
            if self.temp_sensor:
                final_temp = self.temp_sensor.read_temperature()
                if final_temp and initial_temp:
                    temp_change = final_temp - initial_temp
                    logging.info(f"🌡️  Final temperature: {final_temp}C")
                    logging.info(f"📊 Change: {temp_change:+.2f}C")
            
            logging.info("✅ Cycle completed successfully")
            self._write_state('completed')
            return True
            
        except KeyboardInterrupt:
            logging.warning("⚠️ Interrupted by user")
            self.pump_off()
            return False
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            self.pump_off()
            return False
        finally:
            logging.info("="*50)
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            self.pump_off()
        except:
            pass
        try:
            GPIO.cleanup()
        except:
            pass
        self._cleanup_files()
        logging.info("GPIO cleanup complete")


def main():
    """Main function"""
    controller = None
    try:
        controller = PumpController()
        success = controller.run_cycle()
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Critical error: {e}")
        return 1
    finally:
        if controller:
            controller.cleanup()


if __name__ == "__main__":
    exit(main())
