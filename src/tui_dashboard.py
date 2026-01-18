#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TUI Dashboard - Terminal User Interface"""

import curses
import sys
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from pump_control import PumpController

last_log_lines = []

def is_pump_running():
    """Check if pump is currently running"""
    state = PumpController.get_state()
    return state != 'idle'

def get_pump_pid():
    """Get PID of running pump process"""
    lock_file = Path('/tmp/fermentation_pump.lock')
    if lock_file.exists():
        try:
            return int(lock_file.read_text().strip())
        except:
            pass
    return None

def stop_pump():
    """Stop running pump process"""
    pid = get_pump_pid()
    if pid:
        try:
            import os
            import signal
            os.kill(pid, signal.SIGTERM)
            return True
        except:
            pass
    return False

def read_log_tail(lines=10):
    """Read last N lines from log file"""
    try:
        with open('logs/fermentation.log', 'r') as f:
            return f.readlines()[-lines:]
    except:
        return ["No log file available"]

def run_pump_cycle():
    """Run pump cycle in background"""
    try:
        subprocess.run(
            [sys.executable, str(Path(__file__).parent / 'pump_control.py')],
            check=True
        )
    except Exception as e:
        pass

def draw_dashboard(stdscr):
    """Main TUI drawing function"""
    global last_log_lines
    
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(1000)  # Refresh every second
    
    # Color pairs
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "🥬 FERMENTATION CONTROLLER"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 0, "=" * width, curses.color_pair(1))
        
        # Temperature
        temp = PumpController.get_temperature()
        if temp:
            temp_str = f"{temp:.1f}C"
            temp_color = curses.color_pair(2) if temp < 25 else curses.color_pair(3)
        else:
            temp_str = "N/A"
            temp_color = curses.color_pair(4)
        
        stdscr.addstr(3, 2, "Temperature:", curses.A_BOLD)
        stdscr.addstr(3, 20, temp_str, temp_color | curses.A_BOLD)
        
        # Status
        pump_running = is_pump_running()
        pump_state = PumpController.get_state()
        status = f"🔄 PUMP: {pump_state.upper()}" if pump_running else "✓ Ready"
        status_color = curses.color_pair(3) if pump_running else curses.color_pair(2)
        stdscr.addstr(4, 2, "Status:", curses.A_BOLD)
        stdscr.addstr(4, 20, status, status_color | curses.A_BOLD)
        
        # Time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stdscr.addstr(5, 2, "Time:", curses.A_BOLD)
        stdscr.addstr(5, 20, current_time)
        
        # Controls
        stdscr.addstr(7, 0, "─" * width, curses.color_pair(1))
        stdscr.addstr(8, 2, "CONTROLS:", curses.color_pair(1) | curses.A_BOLD)
        
        if pump_running:
            stdscr.addstr(9, 4, "[R] Run Pump Cycle (disabled - pump running)", curses.color_pair(4))
            stdscr.addstr(10, 4, "[S] Stop Pump", curses.color_pair(3))
        else:
            stdscr.addstr(9, 4, "[R] Run Pump Cycle", curses.color_pair(2))
            stdscr.addstr(10, 4, "[S] Stop Pump (disabled - not running)", curses.color_pair(4))
        
        stdscr.addstr(11, 4, "[L] Toggle Log View")
        stdscr.addstr(12, 4, "[Q] Quit")
        
        # Log section
        log_start = 14
        stdscr.addstr(log_start, 0, "─" * width, curses.color_pair(1))
        stdscr.addstr(log_start + 1, 2, "RECENT LOG:", curses.color_pair(1) | curses.A_BOLD)
        
        last_log_lines = read_log_tail(height - log_start - 3)
        for i, line in enumerate(last_log_lines):
            if log_start + 2 + i < height - 1:
                stdscr.addstr(log_start + 2 + i, 2, line.strip()[:width-4])
        
        stdscr.refresh()
        
        # Handle input
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('r') or key == ord('R'):
            if not is_pump_running():
                thread = threading.Thread(target=run_pump_cycle)
                thread.daemon = True
                thread.start()
        elif key == ord('s') or key == ord('S'):
            if is_pump_running():
                stop_pump()
        elif key == ord('l') or key == ord('L'):
            show_full_log(stdscr)

def show_full_log(stdscr):
    """Show full log in scrollable view"""
    try:
        with open('logs/fermentation.log', 'r') as f:
            lines = f.readlines()
    except:
        lines = ["No log file available"]
    
    offset = max(0, len(lines) - curses.LINES + 3)
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        stdscr.addstr(0, 0, "LOG VIEW (↑/↓ to scroll, Q to return)", curses.A_BOLD)
        stdscr.addstr(1, 0, "=" * width)
        
        for i in range(height - 3):
            if offset + i < len(lines):
                stdscr.addstr(i + 2, 0, lines[offset + i].strip()[:width-1])
        
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1
        elif key == curses.KEY_DOWN and offset < len(lines) - (height - 3):
            offset += 1

def main():
    """Main entry point"""
    try:
        curses.wrapper(draw_dashboard)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
