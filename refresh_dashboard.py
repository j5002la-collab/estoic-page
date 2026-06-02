#!/usr/bin/env python3
"""Regenera el dashboard autónomo con datos frescos para copiar a otra máquina."""
import json, os

BASE = '/opt/data/estoic-page'

# Load data
for fname in ['metrics.json', 'revenue.json', 'estado_operacion.json']:
    path = os.path.join(BASE, fname)
    globals()[fname.replace('.json','')] = json.load(open(path)) if os.path.exists(path) else {}

# Read template
with open(os.path.join(BASE, 'dashboard.html')) as f:
    html = f.read()

# Embed data
old_fetch = """fetch('metrics.json?' + Date.now())
    .then(r => r.json())
    .then(data => {
        renderDashboard(data);
    })"""
html = html.replace(old_fetch, f"const data = {json.dumps(metrics)}; renderDashboard(data);")

# Add state info
embed = f"<script>const ESTADO={json.dumps(estado_operacion)};const REVENUE={json.dumps(revenue)};</script>"
html = html.replace('<script>', embed + '<script>', 1)

path = os.path.join(BASE, 'dashboard_standalone.html')
with open(path, 'w') as f:
    f.write(html)
print(f"✅ Dashboard regenerado: {path} ({os.path.getsize(path)/1024:.1f} KB)")
