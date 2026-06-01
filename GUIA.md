# PÁGINA ESTOICA EN FACEBOOK — GUÍA COMPLETA
# ============================================

## 📁 ESTRUCTURA DEL PROYECTO

  /opt/data/estoic-page/
  ├── posts.json          ← 100 posts listos (citas + reflexiones + hashtags)
  ├── scheduler.py        ← Control manual (next, publish, status, reset, skip)
  ├── daily_publish.py    ← Script para cron (publicación automática diaria)
  ├── .env                ← Tus credenciales de Facebook (PRIVADO)
  ├── state.json          ← Progreso (se crea solo)
  ├── output/             ← Posts guardados para copy-paste
  └── publish.log         ← Registro de publicaciones


## 🚀 ARRANQUE RÁPIDO (3 PASOS)

### PASO 1: Prueba manual

  cd /opt/data/estoic-page
  python3 scheduler.py next

Verás el primer post formateado. Si te gusta, continúa.

### PASO 2: Publicar el primer post

Opción A — Manual (sin API, copiar y pegar):
  python3 scheduler.py next
  # Copia el texto y pégalo en tu página de Facebook

Opción B — Automático (con API de Facebook):
  # Primero configura FB_PAGE_ID y FB_ACCESS_TOKEN en .env
  python3 scheduler.py publish


## 🔑 CONFIGURAR FACEBOOK API (Para automatización total)

### 2.1 Crear App de Facebook
  1. Ve a https://developers.facebook.com
  2. Haz clic en "Mis apps" → "Crear app"
  3. Selecciona tipo "Negocio"
  4. Ponle nombre (ej: "EstoicPage")
  5. Completa el registro

### 2.2 Obtener Token de Página
  1. Ve a Graph API Explorer: https://developers.facebook.com/tools/explorer/
  2. Selecciona tu app
  3. En "Permisos" agrega:
     - pages_manage_posts
     - pages_read_engagement
  4. Haz clic en "Generate Access Token"
  5. Autoriza tu página
  6. Cambia a "Page Token" en el dropdown
  7. COPIA ese token (es largo, ~200 caracteres)

### 2.3 Hacer el token permanente (60 días)
  Ve a esta URL en tu navegador (reemplaza los valores):

  https://graph.facebook.com/v19.0/oauth/access_token?
    grant_type=fb_exchange_token&
    client_id=TU_APP_ID&
    client_secret=TU_APP_SECRET&
    fb_exchange_token=TU_TOKEN_DE_PAGINA

  El resultado será un token de larga duración (~60 días).

### 2.4 Guardar credenciales
  Copia .env.example a .env:
    cp .env.example .env

  Edita .env con tus datos reales:
    FB_PAGE_ID=123456789012345
    FB_ACCESS_TOKEN=EAA...

### 2.5 Probar
  python3 scheduler.py publish
  # Si todo sale bien, verás "✅ Publicado exitosamente"


## 🤖 AUTOMATIZAR CON CRON (Publicación diaria automática)

### Opción A: Probar primero (una sola ejecución)
  python3 daily_publish.py
  cat publish.log

### Opción B: Programar publicación diaria (ej: 9:00 AM)

Con crontab -e agrega:
  0 9 * * * cd /opt/data/estoic-page && /usr/bin/python3 daily_publish.py

O cada 2 días:
  0 9 */2 * * cd /opt/data/estoic-page && /usr/bin/python3 daily_publish.py

### Opción C: Varios horarios (mañana y noche)
  0 9 * * * cd /opt/data/estoic-page && /usr/bin/python3 daily_publish.py
  0 20 * * * cd /opt/data/estoic-page && /usr/bin/python3 daily_publish.py


## 📊 COMANDOS DEL SCHEDULER

  python3 scheduler.py next       → Ver el próximo post
  python3 scheduler.py publish    → Publicar en Facebook
  python3 scheduler.py status     → Ver progreso
  python3 scheduler.py list       → Listar todos los posts
  python3 scheduler.py skip 3     → Saltar 3 días
  python3 scheduler.py skip -1    → Retroceder 1 día
  python3 scheduler.py reset      → Volver al día 1


## 📈 PLAN DE CRECIMIENTO — DE 0 A $500/MES

### Fase 1: Contenido (Mes 1-2)
  ☐ Publicar 1 vez al día (100 días cubiertos)
  ☐ Publicar en 5-10 grupos de FB sobre filosofía, estoicismo, desarrollo personal
  ☐ Responder TODOS los comentarios en < 24h
  ☐ Meta: 1,000 seguidores

### Fase 2: Engagement (Mes 2-3)
  ☐ Agregar 1 reel/semana con citas estoicas
  ☐ Hacer 1 live de 15 min a la semana ("Café Estoico")
  ☐ Crear un grupo privado ("Estoicos en Acción")
  ☐ Meta: 5,000 seguidores

### Fase 3: Monetización (Mes 3-4)
  ☐ Vender e-book "30 Días de Estoicismo" ($7-12 USD)
  ☐ Programa de afiliados Amazon (libros estoicos)
  ☐ Activar estrellas de Facebook en lives
  ☐ Meta: $200/mes

### Fase 4: Escala (Mes 5-6)
  ☐ Mentoría 1:1 ($25-50/sesión)
  ☐ Suscripciones de fans ($2.99/mes)
  ☐ Mini-curso de 5 lecciones por email ($19-29)
  ☐ Meta: $500/mes


## 🛠️ SOLUCIÓN DE PROBLEMAS

### "Error: Token expirado"
  → El token de página dura ~60 días. Genera uno nuevo en Graph API Explorer.

### "Error: Permission error"
  → Asegúrate de que tu app tenga permisos: pages_manage_posts, pages_read_engagement

### "La app no está en modo Live"
  → Ve a developers.facebook.com → Tu App → App Review → Modo "Live"

### "No veo mis posts en la página"
  → Verifica que estás usando un PAGE token, no un USER token.
  → En Graph API Explorer, selecciona "Page Token" en el dropdown.


## 📞 RECURSOS ÚTILES

  Graph API Explorer:  https://developers.facebook.com/tools/explorer/
  Documentación Feed:  https://developers.facebook.com/docs/graph-api/reference/v19.0/page/feed
  Verificar token:      https://developers.facebook.com/tools/debug/accesstoken/
  Meta Business Suite:  https://business.facebook.com/  (programar posts manualmente)


## 💡 TIPS DE ORO

  1. Publica a las 7-9 AM o 7-9 PM (mejor alcance)
  2. Usa imágenes con las citas (3x más engagement)
  3. Los posts con pregunta reciben 2x más comentarios
  4. Responde comentarios en la primera hora (algoritmo lo premia)
  5. Comparte el post en tu perfil personal para darle alcance inicial
  6. Únete a grupos de estoicismo/filosofía y comparte valor (no solo links)
