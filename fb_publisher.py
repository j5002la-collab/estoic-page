#!/usr/bin/env python3
"""
Facebook Publisher para Página Estoica.
Publica imágenes + caption en Facebook con el formato visual de Mensanity.
"""
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

def load_env():
    """Carga variables de entorno desde .env"""
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


def format_caption(post):
    """Formato de caption estilo Mensanity: corto, directo, con hashtags."""
    emoji_map = {
        "control": "🎯", "mindset": "🧠", "resilience": "💪",
        "death": "⏳", "time": "⌛", "discipline": "⚡",
        "action": "🚀", "wisdom": "📚", "gratitude": "🙏",
        "relationships": "🤝", "wealth": "💎", "fame": "👑",
        "emotion": "🧘", "fear": "🦁", "morning": "🌅",
        "character": "🏛️", "acceptance": "🌊", "courage": "⚔️",
        "happiness": "😊", "virtue": "✨", "legacy": "🌍",
        "freedom": "🕊️", "purpose": "🔥",
    }
    emoji = emoji_map.get(post.get("category", ""), "🏛️")

    return (
        f"{post['reflection']}\n\n"
        f"{post['hashtags']}\n"
        f"#Mensanity #Estoicismo #Disciplina"
    )


def publish_photo(page_id, token, image_path, caption):
    """Sube una foto a Facebook con caption."""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    boundary = '----Boundary7MA4YWxkTrZu0gW'
    body = b''

    # Caption
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="message"\r\n\r\n'
    body += caption.encode('utf-8') + b'\r\n'

    # Image
    fname = os.path.basename(image_path)
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="source"; filename="{fname}"\r\n'.encode()
    body += b'Content-Type: image/png\r\n\r\n'
    body += image_data + b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    url = f"https://graph.facebook.com/v19.0/{page_id}/photos?access_token={token}"
    req = urllib.request.Request(url, data=body, headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
    })

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read()).get('error', {}).get('message', str(e))}


def publish_post(day=None):
    """Publica el post del día especificado (o el siguiente según state.json)."""
    env = load_env()
    page_id = env.get("FB_PAGE_ID", "841827389008994")
    token = env.get("FB_ACCESS_TOKEN", "")

    if not token or len(token) < 20:
        print("❌ No hay token de Facebook configurado en .env")
        return False

    # Determine ciclo and load posts
    state_path = BASE_DIR / "state.json"
    if state_path.exists():
        with open(state_path) as f:
            state = json.load(f)
    else:
        state = {}

    current = state.get("current_day", 0)
    cycle = state.get("cycles_completed", 0)

    # Load correct ciclo file
    if cycle == 0:
        posts_file = BASE_DIR / "posts.json"
    else:
        posts_file = BASE_DIR / f"posts_ciclo{cycle + 1}.json"
        if not posts_file.exists():
            print(f"⚠️  {posts_file.name} no existe, usando posts.json")
            posts_file = BASE_DIR / "posts.json"
            cycle = 0

    with open(posts_file, "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Determine which post to publish
    if day is None:
        if current >= len(posts):
            current = 0
            cycle += 1
            state["cycles_completed"] = cycle
            # Try next ciclo file
            next_posts_file = BASE_DIR / f"posts_ciclo{cycle + 1}.json"
            if next_posts_file.exists():
                with open(next_posts_file, "r", encoding="utf-8") as f:
                    posts = json.load(f)
            else:
                # Reset to ciclo 1 if no more files
                print(f"⚠️  {next_posts_file.name} no existe, reiniciando en posts.json")
                cycle = 0
                state["cycles_completed"] = 0
                with open(BASE_DIR / "posts.json", "r", encoding="utf-8") as f:
                    posts = json.load(f)
        post = posts[current]
    else:
        post = posts[day - 1]  # day is 1-indexed

    # Verify image exists
    image_file = IMAGES_DIR / f"dia_{post['day']:03d}.png"
    if not image_file.exists():
        print(f"❌ Imagen no encontrada: {image_file}")
        print(f"   Ejecuta: python3 image_gen.py all")
        return False

    # Format caption
    caption = format_caption(post)

    print(f"📤 Publicando Día {post['day']} (Ciclo {cycle + 1})...")
    print(f"   Categoría: {post['category']}")
    print(f"   Autor: {post['author']}")
    print(f"   Imagen: {image_file.name}")
    print(f"   Archivo: {posts_file.name}")

    # Publish
    result = publish_photo(page_id, token, str(image_file), caption)

    if 'id' in result:
        print(f"✅ PUBLICADO! Post ID: {result['id']}")
        # Update state
        if day is None:
            state["current_day"] += 1
            state["total_published"] = state.get("total_published", 0) + 1
            from datetime import datetime
            state["last_published"] = datetime.now().isoformat()
            with open(BASE_DIR / "state.json", "w") as f:
                json.dump(state, f, indent=2)
            print(f"   Siguiente: Día {state['current_day'] + 1}")
        return True
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        day = int(sys.argv[1])
        publish_post(day=day)
    else:
        publish_post()
