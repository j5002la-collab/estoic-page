#!/usr/bin/env python3
"""
Script diario para cron. Si tiene credenciales de Facebook, publica automáticamente.
Si no, guarda el post en output/today.txt para copiar y pegar manualmente.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_FILE = BASE_DIR / "posts.json"
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_DIR = BASE_DIR / "output"
LOG_FILE = BASE_DIR / "publish.log"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")


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
    return (
        f"{emoji} DÍA {post['day']} DE ESTOICISMO {emoji}\n\n"
        f"\"{post['quote']}\"\n\n"
        f"— {post['author']}\n\n"
        f"{post['reflection']}\n\n"
        f"💬 ¿Cómo aplicas esta enseñanza en tu vida? Comparte en los comentarios.\n\n"
        f"{post['hashtags']}\n\n"
        f"#estoicismodiario #filosofiaestoica #desarrollopersonal"
    )


def publish_to_facebook(post):
    page_id = os.environ.get("FB_PAGE_ID")
    access_token = os.environ.get("FB_ACCESS_TOKEN")

    if not page_id or not access_token:
        return False

    try:
        import requests
    except ImportError:
        return False

    message = format_post(post)
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"

    try:
        response = requests.post(url, data={
            "message": message,
            "access_token": access_token
        }, timeout=30)

        if response.status_code == 200:
            result = response.json()
            log(f"✅ Publicado en Facebook — Post ID: {result.get('id')}")
            return True
        else:
            log(f"❌ Error API: {response.status_code} — {response.text[:200]}")
            return False
    except Exception as e:
        log(f"❌ Error de conexión: {e}")
        return False


def main():
    posts = load_posts()
    state = load_state()

    # Manejar fin de ciclo
    if state["current_day"] >= len(posts):
        state["current_day"] = 0
        state["cycles_completed"] = state.get("cycles_completed", 0) + 1
        log(f"🔄 Ciclo {state['cycles_completed']} iniciado")

    post = posts[state["current_day"]]
    log(f"📝 Preparando Día {post['day']} — {post['category']}")

    # Intentar publicar en Facebook
    published = publish_to_facebook(post)

    if not published:
        # Guardar para publicación manual
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / f"dia_{post['day']:03d}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(format_post(post))
        log(f"💾 Guardado para copiar/pegar: {output_file}")

    # Avanzar al siguiente día
    state["current_day"] += 1
    state["total_published"] += 1
    state["last_published"] = datetime.now().isoformat()
    save_state(state)

    if published:
        log(f"✅ Día {post['day']} completado — siguiente: Día {state['current_day'] + 1}")
    else:
        log(f"📋 Día {post['day']} listo para publicar manualmente")


if __name__ == "__main__":
    main()
