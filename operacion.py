#!/usr/bin/env python3
"""
🧘 OPERACIÓN MENSANITY — Orquestador Maestro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ejecuta y monitorea TODA la operación estoica:
  1. Publicación diaria (fb_publisher.py)
  2. Tracking de métricas (tracker.py)
  3. Reportes semanales
  4. Revenue tracking
  5. Dashboard auto-generado
  6. Logs centralizados

Uso:
  python3 operacion.py daily      → Ejecuta tareas diarias
  python3 operacion.py weekly     → Reporte semanal completo
  python3 operacion.py status     → Estado general de la operación
  python3 operacion.py dashboard  → Regenera dashboard HTML
  python3 operacion.py revenue N  → Registra ingreso ($N)
"""
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "estado_operacion.json"
REVENUE_FILE = BASE_DIR / "revenue.json"
METRICS_FILE = BASE_DIR / "metrics.json"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"
LOG_DIR = BASE_DIR / "logs"

os.makedirs(LOG_DIR, exist_ok=True)

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOG_DIR / f"operacion_{datetime.now().strftime('%Y%m')}.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_script(script_name, timeout=120):
    """Ejecuta un script Python y captura salida."""
    path = BASE_DIR / script_name
    if not path.exists():
        log(f"❌ Script no encontrado: {script_name}", "ERROR")
        return None

    try:
        result = subprocess.run(
            ["python3", str(path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(BASE_DIR)
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT", "success": False}
    except Exception as e:
        return {"exit_code": -1, "stdout": "", "stderr": str(e), "success": False}


def cmd_daily():
    """Ejecuta tareas diarias: publicar + trackear."""
    log("═══ INICIO OPERACIÓN DIARIA ═══")

    state = load_json(STATE_FILE, {
        "days_running": 0,
        "total_posts": 0,
        "total_errors": 0,
        "last_daily": None,
        "last_weekly": None,
        "total_revenue_usd": 0,
        "started_at": datetime.now().isoformat()
    })

    # 1. Publicar post del día
    log("📤 Publicando post...")
    pub_result = run_script("fb_publisher.py")
    if pub_result and pub_result["success"] and "PUBLICADO" in pub_result["stdout"]:
        log("   ✅ Post publicado")
        state["total_posts"] += 1
    elif pub_result:
        log(f"   ⚠️ Publicación: {pub_result['stderr'][:200] or pub_result['stdout'][:200]}")
        state["total_errors"] += 1
    else:
        log("   ❌ Error ejecutando fb_publisher.py")
        state["total_errors"] += 1

    # 2. Trackear métricas
    log("📊 Recolectando métricas...")
    track_result = run_script("tracker.py")
    if track_result and track_result["success"]:
        log("   ✅ Métricas actualizadas")
    else:
        log("   ⚠️ Tracker: posible token expirado", "WARN")

    # 3. Update state
    state["days_running"] += 1
    state["last_daily"] = datetime.now().isoformat()
    save_json(STATE_FILE, state)

    # 4. Print summary
    metrics = load_json(METRICS_FILE, [])
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})

    print(f"""
═══ RESUMEN DIARIO ═══
📅 Día {state['days_running']} de operación
📤 Posts publicados: {state['total_posts']}
👥 Seguidores: {metrics[-1].get('followers', '?') if metrics else '?'}
💰 Revenue total: ${revenue.get('total', 0):.2f}
❌ Errores acumulados: {state['total_errors']}
═══
""")

    return True


def cmd_weekly():
    """Genera reporte semanal completo."""
    log("═══ REPORTE SEMANAL ═══")

    state = load_json(STATE_FILE)
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    metrics = load_json(METRICS_FILE, [])

    # Run tracker first to get fresh data
    run_script("tracker.py")

    # Reload metrics
    metrics = load_json(METRICS_FILE, [])

    # Calculate weekly stats
    week_data = metrics[-7:] if len(metrics) >= 7 else metrics
    start_followers = week_data[0].get("followers", 0) if week_data else 0
    end_followers = week_data[-1].get("followers", 0) if week_data else 0
    follower_growth = end_followers - start_followers
    avg_engagement = sum(d.get("engagement_rate", 0) for d in week_data) / max(len(week_data), 1)

    # Revenue this week
    week_ago = datetime.now() - timedelta(days=7)
    week_revenue = sum(
        t.get("amount", 0) for t in revenue.get("transactions", [])
        if t.get("date", "") >= week_ago.strftime("%Y-%m-%d")
    )

    days_running = state.get("days_running", 0)
    daily_growth = follower_growth / max(days_running, 1)
    followers_now = end_followers

    # Projections
    proj_1k = max(0, int((1000 - followers_now) / max(daily_growth, 0.1)))
    proj_5k = max(0, int((5000 - followers_now) / max(daily_growth, 0.1)))
    proj_10k = max(0, int((10000 - followers_now) / max(daily_growth, 0.1)))
    est_monthly = round(followers_now * 0.01 * 7 + followers_now * 0.005 * 5)

    report = f"""
╔══════════════════════════════════════════╗
║     🧘 REPORTE SEMANAL MENSANITY        ║
║     {datetime.now().strftime('%Y-%m-%d')}                          ║
╚══════════════════════════════════════════╝

👥 AUDIENCIA
   Seguidores:     {followers_now:,}
   Crecimiento 7d: {'+' if follower_growth >= 0 else ''}{follower_growth:,}
   Crecimiento/día: {daily_growth:.1f}

📊 ENGAGEMENT
   Tasa promedio:  {avg_engagement:.1f}%

📈 PROYECCIONES
   1,000 seguidores:  {proj_1k} días → { (datetime.now() + timedelta(days=proj_1k)).strftime('%d %b') if proj_1k < 365 else 'N/A'}
   5,000 seguidores:  {proj_5k} días → { (datetime.now() + timedelta(days=proj_5k)).strftime('%d %b %Y') if proj_5k < 730 else 'N/A'}
   10,000 seguidores: {proj_10k} días → { (datetime.now() + timedelta(days=proj_10k)).strftime('%d %b %Y') if proj_10k < 1825 else 'N/A'}

💰 REVENUE
   Esta semana:   ${week_revenue:.2f}
   Total acumulado: ${revenue.get('total', 0):.2f}
   Estimado mensual: ${est_monthly:,}
   Meta $500/mes:  {est_monthly / 500 * 100:.0f}%

📦 OPERACIÓN
   Días activo:    {days_running}
   Posts totales:  {state.get('total_posts', 0)}
   Errores:        {state.get('total_errors', 0)}

╚══════════════════════════════════════════╝
"""
    print(report)

    # Save report
    report_dir = BASE_DIR / "reportes"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"semanal_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_path, "w") as f:
        f.write(report)
    log(f"Reporte guardado: {report_path}")

    state["last_weekly"] = datetime.now().isoformat()
    save_json(STATE_FILE, state)

    return report


def cmd_revenue(amount):
    """Registra un ingreso."""
    try:
        amount = float(amount)
    except ValueError:
        log(f"❌ Monto inválido: {amount}", "ERROR")
        return

    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    transaction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "amount": amount,
        "source": "manual"
    }
    revenue["transactions"].append(transaction)
    revenue["total"] = sum(t["amount"] for t in revenue["transactions"])
    revenue["last_updated"] = datetime.now().isoformat()
    save_json(REVENUE_FILE, revenue)

    log(f"💰 Revenue registrado: +${amount:.2f} → Total: ${revenue['total']:.2f}")

    # Check milestone
    if revenue["total"] >= 500:
        log(f"🎉 ¡META DE $500 ALCANZADA! Total: ${revenue['total']:.2f}", "MILESTONE")
    elif revenue["total"] >= 100:
        log(f"📈 Hito: $100 acumulados. Total: ${revenue['total']:.2f}", "MILESTONE")


def cmd_status():
    """Muestra el estado general de la operación."""
    state = load_json(STATE_FILE)
    revenue = load_json(REVENUE_FILE, {"total": 0, "transactions": []})
    metrics = load_json(METRICS_FILE, [])

    followers = metrics[-1].get("followers", "?") if metrics else "?"
    engagement = metrics[-1].get("engagement_rate", "?") if metrics else "?"

    print(f"""
╔══════════════════════════════╗
║   🧘 MENSANITY — ESTADO     ║
╚══════════════════════════════╝

📅 Días operando:  {state.get('days_running', 0)}
📤 Posts publicados: {state.get('total_posts', 0)}
❌ Errores:         {state.get('total_errors', 0)}

👥 Seguidores: {followers}
📊 Engagement: {engagement}%

💰 Revenue total:  ${revenue.get('total', 0):.2f}
🎯 Meta $500:      {revenue.get('total', 0) / 500 * 100:.0f}%

🕐 Último daily:   {state.get('last_daily', 'Nunca')}
📄 Último weekly:  {state.get('last_weekly', 'Nunca')}
""")

    if revenue["total"] > 0:
        print("📋 Últimas transacciones:")
        for t in revenue.get("transactions", [])[-5:]:
            print(f"   {t['date']} | ${t['amount']:.2f} | {t.get('source', '?')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 operacion.py [daily|weekly|status|revenue N|dashboard]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "daily":
        cmd_daily()
    elif cmd == "weekly":
        cmd_weekly()
    elif cmd == "status":
        cmd_status()
    elif cmd == "revenue" and len(sys.argv) > 2:
        cmd_revenue(sys.argv[2])
    elif cmd == "dashboard":
        # Dashboard is static HTML that reads metrics.json
        log("Dashboard disponible en dashboard.html")
    else:
        print(f"Comando desconocido: {cmd}")
        print("Uso: python3 operacion.py [daily|weekly|status|revenue N|dashboard]")
        sys.exit(1)
