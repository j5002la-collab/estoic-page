#!/usr/bin/env python3
"""
Script diario para cron. Publica imagen + caption en Facebook cada día.
Usa fb_publisher.py para subir la imagen generada.
"""
import sys
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "publish.log"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")


def main():
    # Run the publisher
    result = subprocess.run(
        ["python3", str(BASE_DIR / "fb_publisher.py")],
        capture_output=True, text=True, timeout=120,
        cwd=str(BASE_DIR)
    )

    if result.returncode == 0 and "✅ PUBLICADO" in result.stdout:
        log("✅ Publicación diaria exitosa")
        print(result.stdout)
    elif "❌" in result.stdout:
        log("❌ Error en publicación")
        print(result.stderr or result.stdout)
    else:
        log(f"⚠️ Resultado inesperado (exit {result.returncode})")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)


if __name__ == "__main__":
    main()
