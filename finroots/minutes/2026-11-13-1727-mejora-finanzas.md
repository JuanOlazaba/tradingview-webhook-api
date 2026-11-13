# Reunión de mejora · Finanzas y costes · 2026-11-13-1727 UTC

### Operaciones
Orden del día: Costes de IA y servicios frente a resultados; previsión de ingresos; dónde gastar o ahorrar.
Revisad lo publicado, las métricas, el backlog y las respuestas del dueño.

### Operaciones
**Operaciones · Aportación a la reunión (13 nov 2026)**

**Situación real (no hay datos de coste ni de ingresos en el contexto):**
- Las métricas disponibles: 3 vídeos publicados, 3 seguidores, 85–176 visualizaciones por vídeo, 7 likes en total y 0 comentarios. Estamos lejos del objetivo de 100 seguidores y 150 de media de vistas.
- No tengo cifras de gasto en IA, voz, render ni servicios. No propongo previsión de ingresos porque no hay base: el canal no tiene monetización activa y los productos (plantilla, afiliados, guía) están aplazados o pendientes de tu sí.

**Propuestas:**
- **Ahorrar:** no añadir herramientas nuevas (música con licencia, voz premium de ElevenLabs) hasta cumplir el umbral de audiencia que fijemos. Coste: 0 €.
- **Medir antes de gastar:** Operaciones registra, por cada vídeo, el coste real de render (tokens de IA + voz) y lo cruza con vistas a 72 h. Así sabremos el coste por vídeo y por visualización.
- **Previsión:** la rehacemos cuando haya 10 vídeos con datos completos (directiva 8). Hasta entonces, solo escenarios marcados como hipótesis.
- **Coste de oportunidad:** priorizar la conciliación de IDs de TikTok y la validación automática del JSON, que evitan renders inútiles, sobre cualquier gasto nuevo.

**Requiere al dueño:**
- Confirmar el coste mensual actual de las APIs (Anthropic, TikTok) para que podamos calcular el coste por vídeo.
- Decidir el umbral de audiencia que desbloquea la voz premium.

**Próximo paso:** Operaciones entrega la hoja de costes por vídeo antes del domingo 15 nov.

### Producto
**Producto · Aportación (13 nov 2026)**

Coincido con Operaciones: sin datos de coste ni de ingresos no hay previsión fiable. Desde producto, propongo lo siguiente:

**Qué cambiaría**
- **Ingresos:** mantener la monetización en 0 € hasta el umbral de audiencia. La única pieza activa es la plantilla de margen mensual (PDF gratuito, pendiente de Compliance antes del 13 nov). Afiliados, newsletter y guía quedan aplazados según la decisión del consejo.
- **Captación sin coste:** la vía principal es la descripción fijada con "Comenta PLANTILLA y te la enviamos", respuesta manual, sin recogida de datos. Solo en 1 de cada 4 vídeos.

**Por qué**
Con 3 seguidores, cualquier gasto nuevo se pagaría sin retorno medible. El gasto de mayor valor ahora es el que evita renders inútiles (validación del JSON y conciliación de IDs).

**Cómo lo medimos**
- Por vídeo, a 24 h y 72 h: comentarios con PLANTILLA, plantillas enviadas, visitas al perfil y clics en bio.
- Sin conclusiones antes de 10 vídeos.

**Requiere al dueño**
- Confirmar el coste mensual actual de las APIs (lo necesito para el cálculo de coste por plantilla enviada).
- Decidir el umbral de audiencia que desbloquea la voz premium y cualquier herramienta de pago.

### IT
**IT · Aportación (13 nov 2026)**

Coincido con Operaciones y Producto: sin datos de coste no hay previsión. Desde IT, lo que cambiaría:

**Qué cambiaría**
- **Ahorrar en fallos, no en herramientas:** los 3 vídeos publicados no tienen coste de render registrado por vídeo. Lo primero es instrumentarlo: tokens de Claude por rol, duración de voz y tiempo de render, todo en el registro de cada episodio.
- **Validación automática del JSON (prioridad 1):** bloquea renders con cifras sin hipótesis o con cifra de pantalla distinta a la de la voz. Cada render bloqueado es coste evitado y una incidencia menos para Compliance.
- **Conciliación de IDs de TikTok antes del 13 nov:** sin ID verificado no sabemos qué render generó qué métrica, y el coste por visualización sería ficticio.
- **Sin nuevas herramientas** (música con licencia, ElevenLabs) hasta el umbral de audiencia. Coste: 0 €.

**Cómo lo medimos**
- Hoja por vídeo: coste IA + voz + render frente a vistas a 24 h y 72 h.
- Semanal: número de bloqueos del validador y episodios que llegan a Compliance sin hipótesis (objetivo cero).

**Requiere al dueño**
- Coste mensual real de Anthropic y TikTok, para calcular el coste por vídeo.
- Umbral de audiencia que desbloquea la voz premium.

### CEO
```json
{
 "summary": "Sin datos de coste ni ingresos no hay previsión fiable: se mantiene la monetización en 0 € y no se añaden herramientas de pago. Medimos el coste real por vídeo antes de gastar, y la previsión se rehace con 10 vídeos publicados con datos completos. El dueño debe confirmar el coste mensual de las APIs y fijar el umbral de audiencia para la voz premium.",
 "actions": [
  {
   "type": "decision",
   "text": "Desde ya no se contrata ninguna herramienta de pago (voz premium ElevenLabs, música con licencia ni servicios nuevos) hasta que el dueño fije el umbral de audiencia. Coste: 0 €."
  },
  {
   "type": "decision",
   "text": "No se hace previsión de ingresos hasta tener 10 vídeos publicados con datos completos (directiva 8). Hasta entonces, solo escenarios marcados como hipótesis."
  },
  {
   "type": "backlog",
   "item": "Operaciones: entregar antes del domingo 15 nov la hoja de coste por vídeo (tokens de IA por rol, duración de voz y tiempo de render) cruzada con vistas a 24 h y 72 h. Cifras reales cuando estén disponibles; sin estimaciones presentadas como datos. Responsable: Operaciones (IT aporta los datos de render)."
  },
  {
   "type": "backlog",
   "item": "IT: registrar en el registro de cada episodio el coste de render (tokens de Claude por rol, segundos de voz y tiempo de render) desde el próximo render. Responsable: IT. Prioridad tras la validación automática del JSON."
  },
  {
   "type": "owner_request",
   "title": "Coste mensual de APIs y umbral para voz premium",
   "body": "Necesitamos (1) el coste mensual real actual de Anthropic y TikTok para calcular el coste por vídeo y por plantilla enviada, y (2) el umbral de audiencia que desbloquea la voz premium y cualquier herramienta de pago. Opción recomendada para (2): seguidores y media de vistas de los objetivos ya fijados (100 seguidores y 150 vistas de media), sostenidos durante 4 semanas. Coste: 0 € (solo nos dais datos y una decisión). Riesgo: si no se confirma el coste, el cálculo por vídeo queda incompleto y la previsión se retrasa. Si dice que no: seguimos sin herramientas de pago y calculamos el coste solo con las facturas que podamos reconstruir, marcándolo como incompleto.",
   "apply_on_yes": {
    "decision": "Umbral de audiencia para voz premium y herramientas de pago fijado por el dueño; hasta entonces, coste 0 €."
   }
  }
 ]
}
```

### Operaciones
Acciones ejecutadas:
- decisión: Desde ya no se contrata ninguna herramienta de pago (voz premium ElevenLabs, música con licencia ni servicios nuevos) hasta que el dueño fije el umbral de audiencia. Coste: 0 €.
- decisión: No se hace previsión de ingresos hasta tener 10 vídeos publicados con datos completos (directiva 8). Hasta entonces, solo escenarios marcados como hipótesis.
- backlog: Operaciones: entregar antes del domingo 15 nov la hoja de coste por vídeo (tokens de IA por rol, duración de voz y tiempo de render) cruzada con vistas a 24 h y 72 h. Cifras reales cuando estén disponibles; sin estimaciones presentadas como datos. Responsable: Operaciones (IT aporta los datos de render).
- backlog: IT: registrar en el registro de cada episodio el coste de render (tokens de Claude por rol, segundos de voz y tiempo de render) desde el próximo render. Responsable: IT. Prioridad tras la validación automática del JSON.
- petición al dueño: Coste mensual de APIs y umbral para voz premium
