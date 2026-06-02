# Plan: Fase 2 — Reciclaje, Crecimiento y Monetización

**Objetivo:** Completar items 2, 3, 4 de la operación Mensanity
**Estado item 1:** ✅ PDF generado (33 págs, 94 KB, `/productos/30-dias-estoicismo.pdf`)
**Modo:** Ejecución directa, sin pedir autorización, commits automáticos

---

## Item 2: Sistema de Reciclaje de Contenido (post día 100+)

**Problema:** Después del día 100, no hay más posts.
**Solución:** Script `reciclar.py` que genera variaciones sobre los 100 posts originales.

**Archivos:**
- `reciclar.py` — Genera `posts_ciclo2.json` con variaciones (cambia hashtags, reordena reflexiones, alterna categorías)
- Modificar `fb_publisher.py` para que cuando state.current_day >= 100, cargue `posts_ciclo2.json`
- Se pueden generar infinitos ciclos cambiando semillas

**Implementación:**
1. Crear `reciclar.py` que lee `posts.json`, aplica transformaciones (swap hashtags, sinónimos en reflexión, reorden de categorías), genera nuevo JSON
2. Actualizar `fb_publisher.py` para detectar fin de ciclo y cargar siguiente ciclo
3. También actualizar `image_gen.py` para regenerar imágenes del nuevo ciclo
4. Probar generando ciclo 2

---

## Item 3: Estrategia de Crecimiento (scripts para grupos FB)

**Problema:** Llegar a más seguidores requiere distribución activa.
**Solución:** Scripts que generan contenido optimizado para compartir en grupos.

**Archivos:**
- `growth/share_builder.py` — Genera snippets para FB groups: quote corta + imagen + CTA suave a Mensanity
- `growth/hashtag_optimizer.py` — Analiza y sugiere hashtags trending en estoicismo
- `growth/content_calendar.json` — Calendario de contenido extra (reels, lives, encuestas)

**Implementación:**
1. Crear `share_builder.py` que toma cada post y genera un "snippet para grupos" (texto más corto, más punch, con CTA)
2. Guardar en `growth/snippets_grupos.json` — 100 snippets listos para copiar/pegar
3. Crear `content_calendar.json` con ideas semanales: 1 reel, 1 live, 2 encuestas

---

## Item 4: Mini-Curso de 5 Emails Automáticos

**Problema:** Monetizar con un funnel de email.
**Solución:** 5 lecciones en markdown listas para cargar en cualquier plataforma de email marketing.

**Archivos:**
- `productos/mini-curso/dia-1.md` — La Dicotomía del Control
- `productos/mini-curso/dia-2.md` — Memento Mori
- `productos/mini-curso/dia-3.md` — Amor Fati
- `productos/mini-curso/dia-4.md` — Disciplina Estoica
- `productos/mini-curso/dia-5.md` — Implementación Diaria + Call to Action
- `productos/mini-curso/landing-page.md` — Texto para página de venta

**Implementación:**
1. Crear los 5 archivos markdown con contenido profesional
2. Cada email: saludo, enseñanza, ejercicio, cierre
3. Landing page con copy de ventas para $19 USD
4. Estructura compatible con Mailchimp/ConvertKit/Gumroad

---

## Orden de Ejecución

1. **Item 2** — `reciclar.py` + actualizar publisher (prioridad: evitar quedarse sin contenido)
2. **Item 3** — `share_builder.py` + `content_calendar.json` (prioridad: crecimiento inmediato)
3. **Item 4** — Mini-curso 5 emails + landing page (prioridad: monetización)

Cada item se commitea individualmente al repo.

---

## Validación

- Item 2: `python3 reciclar.py` genera `posts_ciclo2.json` con 100 posts válidos
- Item 3: `python3 share_builder.py` genera snippets en español listos para copiar
- Item 4: Los 5 .md tienen estructura email válida (saludo, cuerpo, cierre)
