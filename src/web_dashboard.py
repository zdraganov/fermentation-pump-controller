#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web Dashboard"""

from flask import Flask, render_template_string, send_file
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from temp_sensor import DS18B20Sensor

app = Flask(__name__)

try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {'web': {'port': 5000, 'auto_refresh': 30}}

try:
    sensor = DS18B20Sensor()
except:
    sensor = None

HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>🥬 Ферментация</title>
<meta http-equiv="refresh" content="{{ refresh }}">
<style>
body{font-family:Arial;text-align:center;padding:50px;background:#667eea;color:#fff}
.temp{font-size:72px;margin:20px 0}.label{font-size:24px}
a{color:#fff;text-decoration:underline}
</style></head><body>
<h1>🥬 Киселене на зеле</h1>
<div class="temp">{{ temp }}°C</div>
<div class="label">{{ status }}</div>
<p>{{ time }}</p>
<p><a href="/">Обнови</a> | <a href="/log">Лог</a></p>
</body></html>'''

@app.route('/')
def index():
    if sensor:
        temp = sensor.read_temperature()
        status = "Работи нормално" if temp else "Грешка"
        temp_str = f"{temp:.1f}" if temp else "N/A"
    else:
        temp_str = "N/A"
        status = "Няма сензор"
    return render_template_string(HTML, temp=temp_str, status=status, 
                                   time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   refresh=config['web'].get('auto_refresh', 30))

@app.route('/log')
def log():
    try:
        with open('logs/fermentation.log', 'r') as f:
            return f'<pre>{f.read()}</pre>'
    except:
        return '<pre>Няма лог файл</pre>'

if __name__ == '__main__':
    from datetime import datetime
    app.run(host='0.0.0.0', port=config['web'].get('port', 5000))
