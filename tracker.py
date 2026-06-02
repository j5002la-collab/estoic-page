#!/usr/bin/env python3
"""
TRACKER DE MÉTRICAS — Mensanity
Recolecta datos diarios de Facebook y los almacena en metrics.json
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
METRICS_FILE = BASE_DIR / "metrics.json"
LOG_FILE = BASE_DIR / "tracker.log"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")


def load_env():
    env = {}
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k] = v
    return env


def fb_get(url_path, token):
    """Call Facebook Graph API."""
    separator = '&' if '?' in url_path else '?'
    url = f"https://graph.facebook.com/v19.0/{url_path}{separator}access_token={token}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        return {"error": err.get('error', {}).get('message', str(e))}
    except Exception as e:
        return {"error": str(e)}


def collect_metrics():
    """Recolecta todas las métricas del día."""
    env = load_env()
    token = env.get("FB_ACCESS_TOKEN", "")
    page_id = env.get("FB_PAGE_ID", "841827389008994")

    if not token or len(token) < 20:
        log("❌ No hay token de Facebook")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    metrics = {"date": today, "timestamp": datetime.now().isoformat()}

    # 1. Page followers
    data = fb_get(f"{page_id}?fields=followers_count,fan_count,name", token)
    if "error" not in data:
        metrics["followers"] = data.get("followers_count", 0)
        metrics["fans"] = data.get("fan_count", 0)
        metrics["page_name"] = data.get("name", "")
        log(f"   👥 Seguidores: {metrics['followers']}")
    else:
        log(f"   ⚠️ Error seguidores: {data['error']}")

    # 2. Posts from last 7 days (engagement)
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    data = fb_get(
        f"{page_id}/feed?fields=id,created_time,message,likes.limit(0).summary(true),"
        f"comments.limit(0).summary(true),shares,insights.metric(post_impressions,post_engaged_users)"
        f"&since={since}&limit=25",
        token
    )

    if "error" not in data and "data" in data:
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_impressions = 0
        total_engaged = 0
        post_count = 0

        for post in data["data"]:
            post_count += 1
            likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = post.get("shares", {}).get("count", 0)

            total_likes += likes
            total_comments += comments
            total_shares += shares

            # Insights if available
            insights = post.get("insights", {}).get("data", [])
            for ins in insights:
                if ins.get("name") == "post_impressions":
                    total_impressions += ins.get("values", [{}])[0].get("value", 0)
                if ins.get("name") == "post_engaged_users":
                    total_engaged += ins.get("values", [{}])[0].get("value", 0)

        metrics["posts_7d"] = post_count
        metrics["likes_7d"] = total_likes
        metrics["comments_7d"] = total_comments
        metrics["shares_7d"] = total_shares
        metrics["impressions_7d"] = total_impressions or (total_likes * 50)  # rough estimate if no insights
        metrics["engaged_7d"] = total_engaged or (total_likes + total_comments + total_shares)

        engagement_rate = 0
        if metrics["impressions_7d"] > 0:
            engagement_rate = round((total_likes + total_comments + total_shares) / metrics["impressions_7d"] * 100, 2)

        metrics["engagement_rate"] = engagement_rate

        log(f"   ❤️ Likes 7d: {total_likes} | 💬 {total_comments} | 🔄 {total_shares}")
        log(f"   📊 Engagement: {engagement_rate}% | 📈 Impressions: {metrics['impressions_7d']}")
    else:
        log(f"   ⚠️ Error posts: {data.get('error', 'No data')}")

    # 3. Save to metrics history
    history = []
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r") as f:
            history = json.load(f)

    # Don't duplicate same-day entries
    history = [h for h in history if h.get("date") != today]
    history.append(metrics)
    history.sort(key=lambda x: x.get("date", ""))

    with open(METRICS_FILE, "w") as f:
        json.dump(history, f, indent=2)

    log(f"   💾 Métricas guardadas ({len(history)} días de historial)")
    return metrics


def generate_report():
    """Genera un reporte de las últimas 7/30 días."""
    if not METRICS_FILE.exists():
        print("No hay datos aún. Ejecuta collect primero.")
        return

    with open(METRICS_FILE, "r") as f:
        history = json.load(f)

    if len(history) < 2:
        print("Necesito al menos 2 días de datos para un reporte.")
        return

    today_data = history[-1]
    week_ago = history[-min(7, len(history))]
    month_ago = history[-min(30, len(history))] if len(history) >= 30 else history[0]

    # Followers growth
    follower_delta_7d = today_data.get("followers", 0) - week_ago.get("followers", 0)
    follower_delta_30d = today_data.get("followers", 0) - month_ago.get("followers", 0)

    # Average engagement
    recent_rates = [h.get("engagement_rate", 0) for h in history[-7:]]
    avg_engagement = sum(recent_rates) / len(recent_rates) if recent_rates else 0

    report = f"""
═══ REPORTE MENSANITY ═══
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

👥 SEGUIDORES
   Hoy:     {today_data.get('followers', '?'):,}
   7 días:  {'+' if follower_delta_7d >= 0 else ''}{follower_delta_7d:,}
   30 días: {'+' if follower_delta_30d >= 0 else ''}{follower_delta_30d:,}

📊 ENGAGEMENT (últimos 7 días)
   Likes:      {today_data.get('likes_7d', 0):,}
   Comentarios:{today_data.get('comments_7d', 0):,}
   Shares:     {today_data.get('shares_7d', 0):,}
   Engagement: {today_data.get('engagement_rate', 0)}% (prom: {avg_engagement:.1f}%)

📈 PROYECCIÓN
   Crecimiento diario: {follower_delta_7d/7:.1f} seguidores/día
   Meta 1,000: en {max(0, (1000 - today_data.get('followers', 0)) / max(follower_delta_7d/7, 0.1)):.0f} días
   Meta 5,000: en {max(0, (5000 - today_data.get('followers', 0)) / max(follower_delta_7d/7, 0.1)):.0f} días
   Meta 10,000: en {(10000 - today_data.get('followers', 0)) / max(follower_delta_7d/7, 0.1):.0f} días

💰 MONETIZACIÓN ESTIMADA
   (basado en 1-2% conversión de seguidores a ventas)
   E-book ($7): ${today_data.get('followers', 0) * 0.01 * 7:.0f}/mes potencial
   Comunidad ($5): ${today_data.get('followers', 0) * 0.005 * 5:.0f}/mes potencial
   Total estimado: ${today_data.get('followers', 0) * 0.01 * 7 + today_data.get('followers', 0) * 0.005 * 5:.0f}/mes
═══
"""
    print(report)

    # Save report
    report_path = BASE_DIR / "reportes" / f"reporte_{datetime.now().strftime('%Y%m%d')}.txt"
    os.makedirs(report_path.parent, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    print(f"📄 Reporte guardado: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        generate_report()
    else:
        collect_metrics()
        generate_report()
