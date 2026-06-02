#!/usr/bin/env python3
"""
Genera PDF profesional del e-book '30 Días de Estoicismo'.
Formato A5, tipografía limpia, listo para vender en Gumroad.
"""
import sys, os, json
sys.path.insert(0, '/opt/data/site-packages')
from fpdf import FPDF

class EstoicPDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A5')
        self.set_auto_page_break(True, 20)
        # Add Unicode-capable fonts
        self.add_font('DSans', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.add_font('DSans', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        self.add_font('DSans', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')  # fallback
        self.add_font('DSans', 'BI', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')  # fallback
        self.add_font('DSerif', '', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
        self.add_font('DSerif', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')
        self.add_font('DSerif', 'I', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')  # fallback
        self.add_font('DSerif', 'BI', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')  # fallback
        # Colors
        self.dark = (20, 20, 30)
        self.white = (255, 255, 255)
        self.gold = (180, 145, 70)
        self.gray = (100, 100, 110)
        self.light_gray = (200, 200, 210)
        self.bg_dark = (18, 18, 26)

    def header(self):
        if self.page_no() > 1:
            self.set_font('DSans', 'I', 7)
            self.set_text_color(*self.gray)
            self.cell(0, 5, '30 Días de Estoicismo — Mensanity', align='L')
            self.cell(0, 5, f'{self.page_no()}', align='R', new_x="LMARGIN", new_y="NEXT")
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
            self.ln(4)

    def footer(self):
        pass

    def cover_page(self):
        self.add_page()
        # Dark background
        self.set_fill_color(*self.bg_dark)
        self.rect(0, 0, self.w, self.h, 'F')

        # Gold accent line
        self.set_draw_color(*self.gold)
        self.set_line_width(1)
        self.line(30, 60, self.w - 30, 60)
        self.line(30, self.h - 60, self.w - 30, self.h - 60)

        # Title
        self.set_y(70)
        self.set_font('DSans', 'B', 28)
        self.set_text_color(*self.white)
        self.multi_cell(0, 12, '30 DÍAS DE\nESTOICISMO', align='C')

        # Subtitle
        self.ln(8)
        self.set_font('DSans', '', 13)
        self.set_text_color(*self.gray)
        self.cell(0, 8, 'Transforma tu mente en un mes', align='C', new_x="LMARGIN", new_y="NEXT")

        # Author
        self.ln(30)
        self.set_font('DSans', 'B', 14)
        self.set_text_color(*self.gold)
        self.cell(0, 8, 'MENSANITY', align='C', new_x="LMARGIN", new_y="NEXT")

        self.set_font('DSans', '', 10)
        self.set_text_color(*self.gray)
        self.cell(0, 8, 'Filosofía estoica para la vida moderna', align='C', new_x="LMARGIN", new_y="NEXT")

    def intro_page(self):
        self.add_page()
        self.set_font('DSans', 'B', 16)
        self.set_text_color(*self.gold)
        self.cell(0, 10, 'INTRODUCCIÓN', align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        intro = (
            "El estoicismo no es una filosofía antigua para académicos. Es un sistema "
            "operativo para la vida moderna.\n\n"
            "Marco Aurelio era emperador. Séneca era banquero y dramaturgo. Epicteto era "
            "esclavo. Los tres enfrentaron presión extrema, pérdidas, traiciones, enfermedad "
            "y muerte. Y los tres encontraron la fórmula para mantener la calma en medio del caos.\n\n"
            "Este libro es tu guía práctica de 30 días. Cada día contiene:\n"
            "  • Una cita original de los grandes estoicos\n"
            "  • Una reflexión para aplicar HOY\n"
            "  • Un ejercicio práctico\n"
            "  • Espacio para escribir tus pensamientos\n\n"
            "No necesitas leerlo de corrido. Vive un día a la vez. Al final de los 30 días, "
            "habrás entrenado tu mente para ver el mundo con otros ojos."
        )
        self.set_font('DSans', '', 10)
        self.set_text_color(*self.gray)
        self.multi_cell(0, 6.5, intro, align='J')

    def day_page(self, day, quote, author, reflection, exercise):
        self.add_page()

        # Day number badge
        self.set_fill_color(*self.gold)
        self.set_text_color(*self.white)
        self.set_font('DSans', 'B', 11)
        x = self.w - 35
        self.rect(x, 12, 25, 10, 'F')
        self.set_xy(x, 13)
        self.cell(25, 8, f'DÍA {day}', align='C')

        # Quote
        self.set_y(35)
        self.set_font('DSans', 'B', 13)
        self.set_text_color(*self.white)
        self.multi_cell(0, 7, f'"{quote}"', align='C')

        # Author
        self.ln(4)
        self.set_font('DSans', 'I', 10)
        self.set_text_color(*self.gold)
        self.cell(0, 6, f'— {author}', align='C', new_x="LMARGIN", new_y="NEXT")

        # Separator
        self.ln(6)
        self.set_draw_color(*self.gold)
        y = self.get_y()
        self.line(50, y, self.w - 50, y)
        self.ln(6)

        # Reflection
        self.set_font('DSans', '', 10)
        self.set_text_color(*self.light_gray)
        self.multi_cell(0, 6, reflection, align='J')

        # Exercise
        self.ln(8)
        self.set_fill_color(*self.bg_dark)
        y = self.get_y()
        self.rect(15, y - 3, self.w - 30, 35, 'F')

        self.set_y(y)
        self.set_font('DSans', 'B', 10)
        self.set_text_color(*self.gold)
        self.cell(0, 6, 'EJERCICIO DEL DÍA', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font('DSans', '', 9)
        self.set_text_color(*self.light_gray)
        self.set_x(20)
        self.multi_cell(self.w - 40, 5.5, exercise, align='C')

        # Journal space
        self.ln(10)
        self.set_font('DSans', 'I', 9)
        self.set_text_color(*self.gray)
        self.cell(0, 6, 'Mis reflexiones:', align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        for _ in range(7):
            self.set_draw_color(*self.gray)
            self.line(20, self.get_y() + 5, self.w - 20, self.get_y() + 5)
            self.ln(8)

    def conclusion_page(self):
        self.add_page()
        self.set_font('DSans', 'B', 16)
        self.set_text_color(*self.gold)
        self.cell(0, 10, 'CONCLUSIÓN', align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        text = (
            "Has completado 30 días de entrenamiento mental. El estoicismo no termina aquí. "
            "Esto fue el calentamiento. La verdadera prueba es aplicar estas enseñanzas cuando "
            "la vida te golpea de verdad.\n\n"
            "Recuerda:\n"
            "  • No puedes controlar lo que pasa, pero sí cómo respondes.\n"
            "  • La muerte no es el fin, es la urgencia de vivir bien AHORA.\n"
            "  • El obstáculo ES el camino.\n"
            "  • La felicidad está en la calidad de tus pensamientos.\n\n"
            "No pretendas ser estoico. Vívelo."
        )
        self.set_font('DSans', '', 10)
        self.set_text_color(*self.gray)
        self.multi_cell(0, 6.5, text, align='J')

        self.ln(15)
        self.set_font('DSans', 'B', 12)
        self.set_text_color(*self.gold)
        self.cell(0, 8, 'MENSANITY', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('DSans', '', 9)
        self.set_text_color(*self.gray)
        self.cell(0, 6, 'facebook.com/Mensanity', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, 'Posts diarios de estoicismo para tu crecimiento personal', align='C')


def generate_pdf():
    pdf = EstoicPDF()

    # Cover
    pdf.cover_page()

    # Intro
    pdf.intro_page()

    # Load posts
    posts_path = '/opt/data/estoic-page/posts.json'
    with open(posts_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    # Exercises map
    exercises = {
        "control": "Haz una lista de 5 cosas que te preocupan. Al lado de cada una, escribe 'CONTROLO' o 'NO CONTROLO'. Durante 24 horas, solo ocúpate de las que controlas.",
        "mindset": "Cada vez que tengas un pensamiento negativo hoy, detente y pregúntate: '¿Es esto 100% verdad o es una historia que me estoy contando?'",
        "resilience": "Identifica un obstáculo actual. Escribe 3 formas en que este obstáculo podría ser en realidad una ventaja disfrazada.",
        "death": "Escribe tu propio obituario en 5 líneas. ¿Qué te gustaría que dijera? Ahora vive HOY de acuerdo a eso.",
        "time": "Hoy, elimina UNA actividad que te roba tiempo sin darte valor. Reemplázala con 30 minutos de lectura o ejercicio.",
        "emotion": "La próxima vez que sientas enojo hoy, espera 60 segundos antes de reaccionar. En esos 60 segundos, respira profundo 3 veces.",
        "gratitude": "Antes de dormir, escribe 3 cosas por las que estás agradecido hoy. No pueden ser las mismas de ayer.",
        "action": "Identifica algo que has estado posponiendo. Haz la versión más pequeña posible de esa tarea AHORA. No esperes.",
        "discipline": "Elige un pequeño hábito que quieras construir. Comprométete a hacerlo solo por 5 minutos hoy. Mañana, otros 5.",
        "fear": "Escribe tu miedo más grande en un papel. Luego escribe: '¿Qué es lo peor que podría pasar realmente?' y responde honestamente.",
        "virtue": "Hoy haz un acto de bondad anónimo. No se lo cuentes a nadie. Hazlo solo por el placer de hacer el bien.",
        "relationships": "Piensa en alguien que te irrita. Envía un mensaje genuino de agradecimiento o aprecio. No esperes respuesta.",
        "morning": "Mañana, antes de tocar el teléfono, siéntate 2 minutos en silencio y visualiza cómo quieres que sea tu día.",
        "character": "Define tu 'código personal' en 3 reglas. Ej: 'Siempre digo la verdad', 'Nunca me rindo', 'Ayudo sin esperar nada'.",
        "wisdom": "Hoy escucha el doble de lo que hablas. En cada conversación, haz al menos 2 preguntas antes de dar tu opinión.",
        "acceptance": "Piensa en algo que salió mal esta semana. Ahora dilo en voz alta y agrega: '...y está bien. Es parte del camino.'",
        "purpose": "Escribe en una frase: 'Mi vida vale la pena porque...' Si no puedes, dedica 15 minutos a pensar qué te haría completarla.",
        "wealth": "Identifica 3 cosas que compraste y no necesitabas. Dona, regala o vende una de ellas esta semana.",
    }

    # Generate 30 day pages
    for i, post in enumerate(posts[:30]):
        day = i + 1
        exercise = exercises.get(post.get("category", ""),
            "Reflexiona sobre la cita de hoy durante 5 minutos. Escribe qué significa para ti en este momento de tu vida.")
        pdf.day_page(day, post['quote'], post['author'], post['reflection'], exercise)
        print(f"  📄 Día {day}")

    # Conclusion
    pdf.conclusion_page()

    # Save
    output_path = '/opt/data/estoic-page/productos/30-dias-estoicismo.pdf'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)

    import os as _os
    size_kb = _os.path.getsize(output_path) / 1024
    print(f"\n✅ PDF generado: {output_path}")
    print(f"   Tamaño: {size_kb:.0f} KB")
    print(f"   Páginas: {pdf.page_no()}")
    print(f"   Formato: A5")
    return output_path

if __name__ == "__main__":
    generate_pdf()
