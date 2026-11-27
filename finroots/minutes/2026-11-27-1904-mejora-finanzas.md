# Reunión de mejora · Finanzas y costes · 2026-11-27-1904 UTC

### Operaciones
Orden del día: Costes de IA y servicios frente a resultados; previsión de ingresos; dónde gastar o ahorrar.
Revisad lo publicado, las métricas, el backlog y las respuestas del dueño.

### Operaciones
**Operaciones · Finanzas y costes (27 nov 2026)**

**Situación real**
- 3 vídeos publicados, 3 seguidores, 341 vistas en total (186, 93, 62). Muestra insuficiente para cualquier conclusión.
- Coste por vídeo: sin datos reales de tokens, voz ni render (directiva 10). No presento cifras estimadas.
- Ingresos: 0 €. No hay previsión de ingresos hasta tener 10 vídeos con datos completos (directiva 8).

**Propuestas**
1. **Coste:** registrar tokens de Claude por rol, segundos de voz y tiempo de render en cada episodio, desde el próximo render. Hoja de coste con datos reales tras 3 renders.
2. **Gasto cero hasta el umbral:** mantener 0 € en voz premium, música con licencia y herramientas nuevas. Medir si la voz actual basta.
3. **Ahorro de tiempo del dueño:** un checklist único de publicación (etiqueta IA, aviso en descripción, ID verificado) para que Marketing lo ejecute sin depender de su revisión.
4. **Bloqueo de render sin evidencia:** cumplir la directiva 3 (validador JSON) antes de gastar más tokens en episodios con cifras; hoy solo se renderizan episodios sin cifras.

**Medición:** coste real por vídeo vs. vistas a 24 h y 72 h, revisado tras 10 vídeos.

**Requiere al dueño**
- Confirmar que se mantiene el gasto en 0 € hasta fijar el umbral de audiencia.
- Decidir si el umbral de 1.000 seguidores y 150 vistas por vídeo se adopta como criterio para voz premium (#10).

### Producto
**Producto · Finanzas y costes**

**Qué cambiaría:** nada de gasto en monetización. El embudo (plantilla, newsletter, afiliados, guía) sigue a coste 0 € y sin activar. Priorizo que el embudo se mida antes de crecer.

**Por qué:** con 3 vídeos, 3 seguidores y una media de unas 114 vistas, no hay base para previsión de ingresos ni para pagar nada. El CTA "Comenta PLANTILLA" y el envío del PDF siguen bloqueados hasta el visto bueno escrito de Compliance y el sí del dueño (directiva 7).

**Cómo lo medimos:**
- Registro a 24 h y 72 h: visitas al perfil, clics en bio, comentarios con PLANTILLA y envíos manuales, sin datos personales.
- Revisión tras 10 vídeos con datos completos. Sin conclusiones antes.
- Si hay visitas pero ninguna petición de plantilla, revisamos el CTA, no el producto.

**Ahorro de tiempo del dueño:** el checklist de publicación (etiqueta IA, aviso en descripción, ID verificado) lo ejecuta Marketing. Producto entrega la revisión escrita de la plantilla antes del viernes 27 nov.

**Requiere al dueño:**
- Confirmar gasto 0 € hasta fijar el umbral.
- Decidir si el umbral de 1.000 seguidores y 150 vistas por vídeo se usa como criterio para voz premium (#10). Hoy es solo una propuesta de Marketing, y estamos lejos de él.

### IT
**IT · Finanzas y costes (27 nov 2026)**

**Qué cambiaría:** añadir al validador JSON un campo de coste por episodio que se rellene automáticamente: tokens de entrada y salida por rol, segundos de voz y tiempo de render. Hoy no tenemos ningún dato real y no debemos estimarlo.

**Por qué:** la directiva 10 prohíbe presentar costes sin datos reales, y el validador (directiva 3, prioridad 1) ya lee cada JSON antes de renderizar. Aprovecharlo evita un registro manual que se olvida y nos da cifras a partir de los próximos 3 renders.

**Estado técnico:** hasta que el validador tenga evidencia escrita de bloqueo, no renderizamos episodios con cifras. Eso también limita el gasto de tokens en episodios que habría que rehacer.

**Medición:** coste real por vídeo frente a vistas a 24 h y 72 h, en la hoja de coste, revisado tras 10 vídeos publicados.

**Gasto:** 0 € en voz premium, música con licencia o herramientas nuevas. Mantenemos la voz edge actual y no cambiamos voice.edge_rate sin render de prueba.

**Requiere al dueño:**
- Confirmar el gasto en 0 € hasta fijar el umbral de audiencia para voz premium (#10).
- Decidir si el umbral de 1.000 seguidores y 150 vistas por vídeo se usa como criterio. Hoy estamos a 3 seguidores y 114 vistas de media, así que no se activará pronto.

### CEO
```json
{
 "summary": "Publicados 3 vídeos con 3 seguidores y 341 vistas en total (media de unas 114). Muestra insuficiente para conclusiones y sin datos reales de coste, así que no hay previsión de ingresos ni gasto nuevo. Mantenemos el gasto en 0 € y medimos coste real frente a vistas antes de decidir nada.",
 "actions": [
  {
   "type": "decision",
   "text": "Mantener el gasto en 0 € (voz premium, música con licencia y herramientas nuevas) hasta que el dueño fije el umbral de audiencia para voz premium (#10). No se contrata nada nuevo en este periodo."
  },
  {
   "type": "decision",
   "text": "No se presenta ninguna cifra de coste por vídeo ni previsión de ingresos hasta tener datos reales de tokens, voz y render (directiva 10) y 10 vídeos con datos completos (directiva 8). Se usa solo la medición ya prevista, sin estimaciones."
  },
  {
   "type": "backlog",
   "item": "Marketing: redactar y aplicar un checklist único de publicación (etiqueta de IA verificada, aviso legal breve en la descripción, ID de TikTok registrado y respuesta manual estándar), para que la publicación no dependa de la revisión del dueño. Responsable: Marketing, con verificación de Operaciones. Sin incluir CTA a la plantilla hasta visto bueno escrito de Compliance y sí del dueño."
  },
  {
   "type": "backlog",
   "item": "IT: incluir en el registro de cada episodio el campo de coste (tokens de entrada y salida por rol, segundos de voz y tiempo de render), rellenado por el validador JSON cuando haya datos reales. Sin valores estimados. Responsable: IT. Prioridad tras la validación de bloqueo (directiva 3)."
  }
 ]
}
```

### Operaciones
Acciones ejecutadas:
- decisión: Mantener el gasto en 0 € (voz premium, música con licencia y herramientas nuevas) hasta que el dueño fije el umbral de audiencia para voz premium (#10). No se contrata nada nuevo en este periodo.
- decisión: No se presenta ninguna cifra de coste por vídeo ni previsión de ingresos hasta tener datos reales de tokens, voz y render (directiva 10) y 10 vídeos con datos completos (directiva 8). Se usa solo la medición ya prevista, sin estimaciones.
- backlog: Marketing: redactar y aplicar un checklist único de publicación (etiqueta de IA verificada, aviso legal breve en la descripción, ID de TikTok registrado y respuesta manual estándar), para que la publicación no dependa de la revisión del dueño. Responsable: Marketing, con verificación de Operaciones. Sin incluir CTA a la plantilla hasta visto bueno escrito de Compliance y sí del dueño.
- backlog: IT: incluir en el registro de cada episodio el campo de coste (tokens de entrada y salida por rol, segundos de voz y tiempo de render), rellenado por el validador JSON cuando haya datos reales. Sin valores estimados. Responsable: IT. Prioridad tras la validación de bloqueo (directiva 3).
