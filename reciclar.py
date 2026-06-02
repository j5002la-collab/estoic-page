#!/usr/bin/env python3
"""
Sistema de reciclaje de contenido estoico.
Cuando se acaban los 100 posts originales, genera ciclos infinitos
con variaciones para que nunca se repita exactamente lo mismo.
"""
import json, random, copy
from pathlib import Path

BASE = Path(__file__).parent

# Variaciones de hashtags por categoría
HASHTAG_VARIATIONS = {
    "control": ["#control #estoicismo #Epicteto", "#pazinterior #filosofia #estoico", "#serenidad #mindset #sabiduria"],
    "mindset": ["#mentalidad #estoicismo #pensamientos", "#mente #filosofia #crecimiento", "#mindset #MarcoAurelio #reflexion"],
    "resilience": ["#resiliencia #fortaleza #estoicismo", "#superacion #adversidad #estoico", "#fuerza #obstaculo #crecimiento"],
    "death": ["#mementomori #estoicismo #vida", "#mortalidad #urgencia #presente", "#muerte #filosofia #MarcoAurelio"],
    "time": ["#tiempo #productividad #estoicismo", "#presente #Seneca #sabiduria", "#disciplina #enfoque #vida"],
    "emotion": ["#emociones #control #estoicismo", "#ira #serenidad #Seneca", "#paz #autocontrol #filosofia"],
    "gratitude": ["#gratitud #estoicismo #felicidad", "#agradecimiento #vida #plenitud", "#mindfulness #presente #alegria"],
    "action": ["#accion #disciplina #estoicismo", "#resultados #enfoque #productividad", "#ejecucion #habitos #cambio"],
    "discipline": ["#disciplina #habitos #estoicismo", "#constancia #rutina #exito", "#fuerza #voluntad #progreso"],
    "fear": ["#miedo #valentia #estoicismo", "#coraje #superacion #confianza", "#temores #accion #libertad"],
    "virtue": ["#virtud #integritad #estoicismo", "#valores #caracter #sabiduria", "#bondad #excelencia #moral"],
    "relationships": ["#relaciones #estoicismo #sabiduria", "#amistad #respeto #filosofia", "#personas #crecimiento #social"],
    "wisdom": ["#sabiduria #aprendizaje #estoicismo", "#conocimiento #reflexion #filosofia", "#mente #educacion #pensar"],
    "acceptance": ["#aceptacion #amorfati #estoicismo", "#fluir #destino #paz", "#soltar #confianza #vida"],
    "purpose": ["#proposito #mision #estoicismo", "#sentido #pasión #vida", "#ikigai #camino #destino"],
    "wealth": ["#riqueza #minimalismo #estoicismo", "#abundancia #libertad #suficiente", "#desapego #simpleza #paz"],
    "character": ["#caracter #integritad #estoicismo", "#valores #principios #honor", "#etica #moral #conducta"],
    "morning": ["#manana #rutina #estoicismo", "#amanecer #disciplina #habitos", "#madrugar #exito #proposito"],
    "happiness": ["#felicidad #estoicismo #paz", "#alegria #plenitud #vida", "#bienestar #interior #mente"],
    "courage": ["#valentia #coraje #estoicismo", "#miedo #superacion #fortaleza", "#heroismo #accion #determinacion"],
}

REFLECTION_STARTERS = [
    "Pregúntate hoy:", "Reflexiona:", "Un ejercicio práctico:", "Aplica esto:",
    "Hoy intenta:", "Recuerda:", "La clave está en:", "Prueba esto:",
    "Piensa en:", "Esta semana:", "Cada día:", "El secreto:",
    "No olvides:", "Ten presente:", "La práctica:", "El desafío:",
]


def generate_cycle(cycle_number, seed=42):
    """Genera un nuevo ciclo de 100 posts con variaciones."""
    random.seed(seed + cycle_number * 137)

    with open(BASE / "posts.json", "r", encoding="utf-8") as f:
        original = json.load(f)

    new_posts = []
    for post in original:
        new = copy.deepcopy(post)

        # 1. Shuffle hashtags: usa una variación de la misma categoría
        cat = post["category"]
        if cat in HASHTAG_VARIATIONS:
            new["hashtags"] = random.choice(HASHTAG_VARIATIONS[cat])
            # Siempre agrega #Mensanity
            if "#Mensanity" not in new["hashtags"]:
                new["hashtags"] += " #Mensanity #Estoicismo"

        # 2. Cambia el starter de la reflexión
        old_ref = post["reflection"]
        # Encuentra la primera oración y cámbiale el inicio
        if ". " in old_ref:
            parts = old_ref.split(". ", 1)
            new["reflection"] = random.choice(REFLECTION_STARTERS) + " " + parts[1] if len(parts) > 1 else old_ref

        # 3. Rota categorías entre posts vecinos (cada 3 posts)
        if post["day"] % 3 == 0:
            cats = list(set(p["category"] for p in original))
            new["category"] = random.choice(cats)

        # 4. Alternate day offset
        new["day"] = post["day"] + cycle_number * 100

        new_posts.append(new)

    return new_posts


def generate_all_cycles(num_cycles=5):
    """Genera N ciclos adicionales (500 posts más)."""
    for c in range(1, num_cycles + 1):
        posts = generate_cycle(c, seed=42)
        path = BASE / f"posts_ciclo{c+1}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Ciclo {c+1}: {len(posts)} posts → {path.name}")


if __name__ == "__main__":
    generate_all_cycles(5)
    print("\n🎉 5 ciclos adicionales generados (500 posts extra).")
    print("   El publisher cargará automáticamente el siguiente ciclo.")
