#!/usr/bin/env python3
"""
ESTOIC PAGE SCHEDULER
Publica automáticamente posts estoicos en Facebook cada día.

Modos de uso:
  1. Manual (sin API):    python3 scheduler.py next     → muestra el post del día
  2. Facebook API:        python3 scheduler.py publish  → publica en Facebook
  3. Ver estado:          python3 scheduler.py status
  4. Reiniciar:           python3 scheduler.py reset
  5. Adelantar/Retroceder: python3 scheduler.py skip N

Configuración:
  Crea un archivo .env con:
    FB_PAGE_ID=tu_page_id
    FB_ACCESS_TOKEN=tu_token_largo_duracion
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_FILE = BASE_DIR / "posts.json"
STATE_FILE = BASE_DIR / "state.json"


def load_posts():
    with open(POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"current_day": 0, "total_published": 0, "last_published": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def format_post(post):
    """Formatea un post para Facebook con emojis y estilo atractivo."""
    emoji_map = {
        "control": "🎯", "mindset": "🧠", "resilience": "💪",
        "death": "⏳", "time": "⌛", "discipline": "⚡",
        "action": "🚀", "wisdom": "📚", "gratitude": "🙏",
        "relationships": "🤝", "wealth": "💎", "fame": "👑",
        "emotion": "🧘", "fear": "🦁", "morning": "🌅",
        "evening": "🌙", "character": "🏛️", "acceptance": "🌊",
        "perspective": "🔭", "purpose": "🔥", "virtue": "✨",
        "happiness": "😊", "courage": "⚔️", "freedom": "🕊️",
        "excellence": "🏆", "legacy": "🌍", "trust": "🤲",
        "presence": "🎁", "comparison": "🪞", "ego": "🎭",
        "independence": "🗽", "attitude": "🌈", "life": "🌟",
        "impermanence": "🍂", "service": "💝", "self": "🪷",
        "anxiety": "🍃", "work": "🔨", "milestone": "🎉",
    }
    emoji = emoji_map.get(post.get("category", ""), "🏛️")

    text = f"""{emoji} DÍA {post['day']} DE ESTOICISMO {emoji}

"{post['quote']}"

— {post['author']}

{post['reflection']}

💬 ¿Qué opinas? ¿Cómo aplicas esta enseñanza en tu vida? Cuéntame en los comentarios.

{post['hashtags']}

#estoicismodiario #filosofiaestoica #desarrollopersonal"""
    return text


def get_today_post(posts, state):
    """Obtiene el post que toca hoy."""
    day = state["current_day"]
    if day >= len(posts):
        # Reiniciar ciclo
        day = 0
        state["current_day"] = 0
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
        save_state(state)
        print("🔄 Ciclo completado. Reiniciando desde el Día 1.")

    # El día 0 corresponde al post[0] (day=1)
    post = posts[day]
    return post


def publish_to_facebook(post):
    """Publica el post en Facebook usando la Graph API."""
    page_id = os.environ.get("FB_PAGE_ID")
    access_token = os.environ.get("FB_ACCESS_TOKEN")

    if not page_id or not access_token:
        print("❌ ERROR: Faltan credenciales de Facebook.")
        print("Configura FB_PAGE_ID y FB_ACCESS_TOKEN en .env o variables de entorno.")
        print("\n📋 Guía rápida para obtener el token:")
        print("1. Ve a https://developers.facebook.com")
        print("2. Crea una App (tipo 'Negocio')")
        print("3. Agrega el producto 'Facebook Login'")
        print("4. Ve a Graph API Explorer")
        print("5. Obtén un Token de Página con permisos: pages_manage_posts, pages_read_engagement")
        print("6. Intercámbialo por un token de larga duración (60 días)")
        return False

    try:
        import requests
    except ImportError:
        print("❌ Instala requests: pip install requests")
        return False

    message = format_post(post)
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"

    response = requests.post(url, data={
        "message": message,
        "access_token": access_token
    })

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Publicado exitosamente en Facebook")
        print(f"   Post ID: {result.get('id')}")
        return True
    else:
        print(f"❌ Error al publicar: {response.status_code}")
        print(f"   {response.text}")
        return False


def cmd_next():
    """Muestra el próximo post sin publicarlo."""
    posts = load_posts()
    state = load_state()
    post = get_today_post(posts, state)

    print(format_post(post))
    print(f"\n📊 Progreso: Día {post['day']}/100 | Publicados: {state['total_published']}")
    print("Para publicar: python3 scheduler.py publish")


def cmd_publish():
    """Publica el post del día en Facebook y avanza el contador."""
    posts = load_posts()
    state = load_state()

    if state["current_day"] >= len(posts):
        state["current_day"] = 0
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
        print("🔄 Nuevo ciclo iniciado.")

    post = get_today_post(posts, state)
    print(f"📝 Preparando publicación: Día {post['day']} - {post['category']}")

    success = publish_to_facebook(post)

    if success:
        state["current_day"] += 1
        state["total_published"] += 1
        state["last_published"] = datetime.now().isoformat()
        save_state(state)
        print(f"📈 Avanzado al día {state['current_day'] + 1}")
    else:
        print("\n💡 PUBLICACIÓN MANUAL (copia y pega este texto en Facebook):")
        print("=" * 60)
        print(format_post(post))
        print("=" * 60)


def cmd_status():
    """Muestra el estado actual."""
    posts = load_posts()
    state = load_state()
    day = state["current_day"]

    print("📊 ESTADO DE LA PÁGINA ESTOICA")
    print(f"   Posts totales: {len(posts)}")
    print(f"   Publicados: {state['total_published']}")
    print(f"   Día actual: {day + 1}/100" if day < 100 else f"   Día: Ciclo completado")
    print(f"   Ciclos: {state.get('cycles_completed', 0)}")
    print(f"   Última publicación: {state['last_published'] or 'Nunca'}")

    if day < len(posts):
        post = posts[day]
        print(f"\n📌 Próximo post: Día {post['day']} — {post['category']}")
        print(f"   «{post['quote'][:60]}...»")


def cmd_reset():
    """Reinicia el contador al día 1."""
    state = {"current_day": 0, "total_published": 0, "last_published": None, "cycles_completed": 0}
    save_state(state)
    print("🔄 Contador reiniciado. El próximo post será el Día 1.")


def cmd_skip(days):
    """Adelanta o retrocede N días."""
    posts = load_posts()
    state = load_state()
    new_day = state["current_day"] + days
    if new_day < 0:
        new_day = 0
    elif new_day >= len(posts):
        new_day = new_day % len(posts)
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
    state["current_day"] = new_day
    save_state(state)
    print(f"⏭️ Avanzado a día {new_day + 1}/100" if days > 0 else f"⏪ Retrocedido a día {new_day + 1}/100")


def cmd_list():
    """Lista todos los posts con su estado."""
    posts = load_posts()
    state = load_state()
    current = state["current_day"]

    print(f"{'Día':<5} {'Categoría':<15} {'Autor':<20} {'Cita (inicio)':<50} {'Estado':<10}")
    print("-" * 100)
    for post in posts:
        status = "✅" if post["day"] <= current else "⏳"
        marker = "◀ HOY" if post["day"] == current + 1 else ""
        print(f"{post['day']:<5} {post['category']:<15} {post['author']:<20} {post['quote'][:48]:<50} {status:<10} {marker}")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "next"

    if command == "next":
        cmd_next()
    elif command == "publish":
        cmd_publish()
    elif command == "status":
        cmd_status()
    elif command == "reset":
        confirm = input("¿Reiniciar desde Día 1? (s/n): ")
        if confirm.lower() == "s":
            cmd_reset()
    elif command == "skip":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        cmd_skip(days)
    elif command == "list":
        cmd_list()
    else:
        print("Uso: python3 scheduler.py [next|publish|status|reset|skip N|list]")
        sys.exit(1)
