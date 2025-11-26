#!/usr/bin/env python3
"""Генериране на графики"""

import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

LOG_FILE = 'logs/temperature.log'
OUTPUT = 'temperature_graph.png'

dates, temps = [], []

if Path(LOG_FILE).exists():
    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?([\d.]+)°C', line)
            if match:
                date_str, temp = match.groups()
                dates.append(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
                temps.append(float(temp))

if dates:
    plt.figure(figsize=(12, 6))
    plt.plot(dates, temps, marker='o', linewidth=2, color='#667eea')
    plt.axhline(y=20, color='g', linestyle='--', alpha=0.7, label='Оптимално (20°C)')
    plt.axhline(y=25, color='orange', linestyle='--', alpha=0.7, label='Внимание (25°C)')
    plt.axhline(y=30, color='r', linestyle='--', alpha=0.7, label='Максимум (30°C)')
    plt.xlabel('Време')
    plt.ylabel('Температура (°C)')
    plt.title('Температура на ферментацията')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=150)
    print(f"✓ График записан: {OUTPUT}")
else:
    print("❌ Няма данни за график")
