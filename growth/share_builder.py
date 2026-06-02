#!/usr/bin/env python3
"""
Genera snippets optimizados para compartir en grupos de Facebook.
Un snippet por cada post: texto corto, punch, call-to-action suave.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent

CTAS = [
    "🔔 Más contenido en Mensanity.",
    "📌 Síguenos para contenido diario.",
    "💡 Estoicismo práctico en Mensanity.",
    "🧘 Reflexiones diarias → Mensanity.",
    "⚡ Un post estoico cada día en Mensanity.",
    "🔥 Filosofía que sirve → Mensanity.",
    "🎯 Mentalidad estoica diaria en Mensanity.",
]

EMOJIS = ["🧘", "💪", "🎯", "🔥", "⚡", "💡", "🏛️", "🌊", "⏳", "🦁"]


def build_snippet(post):
    """Crea un snippet para grupos de FB."""
    # Quote corta (max 150 chars)
    quote = post['quote']
    if len(quote) > 150:
        quote = quote[:147] + "..."

    # CTA al final
    cta = CTAS[post['day'] % len(CTAS)]
    emoji = EMOJIS[post['day'] % len(EMOJIS)]

    snippet = f"""{quote}

— {post['author']}

{post['reflection'][:200]}

{cta}"""
    return snippet


def generate_all():
    with open(BASE.parent / "posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    snippets = []
    for post in posts:
        snippets.append({
            "day": post["day"],
            "category": post["category"],
            "snippet": build_snippet(post),
            "hashtags": post["hashtags"],
            "grupos_sugeridos": ["estoicismo", "filosofía", "desarrollo personal", "mindset", "emprendimiento"]
        })

    out_dir = BASE.parent / "growth"
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / "snippets_grupos.json", "w", encoding="utf-8") as f:
        json.dump(snippets, f, ensure_ascii=False, indent=2)

    # Also create a readable .txt version
    with open(out_dir / "snippets_grupos.txt", "w", encoding="utf-8") as f:
        for s in snippets:
            f.write(f"{'='*60}\n")
            f.write(f"DÍA {s['day']} | {s['category']}\n")
            f.write(f"{'='*60}\n")
            f.write(s['snippet'])
            f.write(f"\n\n")

    print(f"✅ {len(snippets)} snippets generados")
    print(f"   growth/snippets_grupos.json")
    print(f"   growth/snippets_grupos.txt")


if __name__ == "__main__":
    generate_all()
