# Reunión de mejora · Calidad de vídeo y tecnología · 2026-11-11-1727 UTC

### Operaciones
Orden del día: Voz, ritmo, nuevos objetos visuales, fiabilidad de la cadena, publicación cruzada.
Revisad lo publicado, las métricas, el backlog y las respuestas del dueño.

### IT
Como CTO, propongo dos mejoras concretas y una advertencia sobre fiabilidad. Máximo 2 cambios técnicos, según la directiva.

**1. Voz y ritmo (coste 0 €, esfuerzo bajo)**
- Ajustar `voice.edge_rate` a un valor ligeramente más lento (p. ej. +0 % en lugar de +10 %) en los episodios con cifras, para que el "ilustrativa" se entienda en pantalla y en voz.
- Medir: duración media por reel (objetivo 55–75 s) y retención a 3 s por tipo de gancho, sin sacar conclusiones antes de 10 vídeos.

**2. Fiabilidad de la cadena (coste 0 €, esfuerzo bajo-medio)**
- Añadir a la validación del JSON una comprobación automática: toda cifra grande en `counter`, `chart`, `display` o `options` debe tener nota de hipótesis y marca de "ilustrativa". Si falta, el render se bloquea y avisa.
- Medir: número de bloqueos por semana y episodios que llegan a Compliance sin hipótesis (objetivo: cero).

**Advertencia:** los vídeos actuales de la cuenta tienen 60–176 visualizaciones y 0–3 likes. Las mejoras de voz y ritmo no deben confundirse con la causa del bajo alcance; los datos aún no permiten atribuirla.

**Sobre objetos y publicación cruzada:**
- Nuevos objetos visuales: propongo esperar a tener 10 vídeos publicados. Cada objeto nuevo requiere revisión de Compliance si incluye cifras.
- Publicación cruzada a Instagram y YouTube Shorts: requiere crear cuentas nuevas, así que **necesita el sí del dueño**. Prefiero no abrirla hasta que la cadena de TikTok sea estable.

**Lo que necesito del dueño:** solo la decisión sobre la publicación cruzada. Lo demás lo ejecuto yo.

### Estudio
**Estudio · aportación**

**Voz y ritmo.** Apoyo bajar `voice.edge_rate`, pero solo en episodios con cifras, que es lo que propone IT. Matiz: el ritmo lento no arregla que "ilustrativa" se pierda. Lo arreglo en el guion: la palabra va al final de la frase corta, con pausa "..." detrás, y también en el `note` de pantalla. Medición: duración por reel dentro de 55–75 s y revisión manual de que "ilustrativa" suena en cada escena con cifra.

**Fiabilidad.** Apoyo la validación automática, con dos añadidos:
- Comprobar que la cifra de pantalla coincide con la de la voz de esa escena.
- Exigir en el JSON un campo de hipótesis (capital, años, tipo) cuando haya cifras.

Esto cierra el hueco de los ep. 5 y 7: recalculo ambos a mano antes de cualquier render y envío la hipótesis a Compliance. Sigue en el backlog.

**Objetos nuevos.** De acuerdo en esperar. Antes de pedir ninguno, usaré mejor el catálogo actual: varío objetos entre episodios (ya exigido: 3 distintos).

**Retención a 3 s.** Necesito la fuente (API o TikTok Studio). Sin ella no puedo etiquetar ganchos con datos. Hoy solo tenemos vistas, likes y comentarios.

**Publicación cruzada.** Necesita el sí del dueño (cuentas nuevas). Coincido en aplazarla. No añado esa petición ahora.

**Aviso de alcance.** Con 60–176 vistas no atribuyo nada a voz o ritmo.

### Operaciones
**Operaciones · aportación**

**Estado de la cadena (datos reales, 8 nov):** 3 vídeos publicados, 60–176 vistas, 0–3 likes, 0 comentarios. Retención a 3 s y visitas al perfil: sin fuente todavía. Directiva 3 (conciliar IDs antes del 13 nov) y directiva 1 (5 vídeos esta semana) siguen abiertas: hay que confirmarlas hoy.

**Voz y ritmo.** De acuerdo con IT y Estudio. Cambio en el guion, no solo en el motor: las cifras van al final de la frase corta, con "ilustrativa" dicho en voz. Cualquier ajuste de `voice.edge_rate` lo validamos en un render de prueba antes de tocar los episodios programados.

**Fiabilidad.** Prioridad 1. Antes del próximo render: validación automática (cifra en pantalla ↔ voz, hipótesis presente, marca "ilustrativa"). Bloqueo y aviso si falla. Métrica: bloqueos por semana y episodios que llegan a Compliance sin hipótesis (objetivo cero).

**Objetos nuevos.** Esperar a 10 vídeos. Mientras, rotar los 3 objetos distintos ya exigidos.

**Publicación cruzada.** Aplazada. Requiere cuentas nuevas: **petición al dueño**, con la opción recomendada "no abrir todavía". Si dice que sí, Operaciones la ejecuta con revisión de Compliance.

**Lo que necesito del dueño:** solo la decisión sobre publicación cruzada.

**Acta:**
- Decisión: validación automática antes de cualquier render (IT, esta semana).
- Decisión: sin cambios de objetos hasta 10 vídeos (Estudio).
- Pendiente: fuente de retención a 3 s (dueño: autorizar TikTok Studio o API).

### CEO
```json
{
 "summary": "Cerramos la reunión de calidad: la prioridad es la validación automática de la cadena (cifra en pantalla ↔ voz, hipótesis presente, marca 'ilustrativa') antes de cualquier render. La voz se ajusta en el guion (cifra al final de frase corta, 'ilustrativa' dicho en voz) y no solo con edge_rate; cualquier cambio de ritmo se prueba antes en un render de prueba. Objetos y publicación cruzada se mantienen congelados: objetos hasta 10 vídeos y publicación cruzada pendiente del sí del dueño.",
 "actions": [
  {
   "type": "decision",
   "text": "Antes de cualquier render, validación automática obligatoria: (a) toda cifra en counter, chart, display u options lleva nota de hipótesis (capital, años, tipo) y marca 'ilustrativa'; (b) la cifra de pantalla coincide con la de la voz de esa escena; (c) si falla, el render se bloquea y se avisa a IT y Compliance. Responsable: IT. Plazo: antes del próximo render."
  },
  {
   "type": "decision",
   "text": "Voz: no se cambia voice.edge_rate en episodios programados sin render de prueba. En episodios con cifras, la palabra 'ilustrativa' va al final de frase corta con pausa '...' y aparece en el note de pantalla. Revisión manual de cada escena con cifra. Responsable: Estudio."
  },
  {
   "type": "decision",
   "text": "Sin cambios de catálogo de objetos hasta tener 10 vídeos publicados con datos completos. Se mantiene la rotación de al menos 3 tipos de objeto distintos entre episodios consecutivos. Responsable: Estudio."
  },
  {
   "type": "backlog",
   "item": "IT: implementar la validación automática del JSON (bloqueo + aviso) y registrar métricas semanales: número de bloqueos y episodios que llegan a Compliance sin hipótesis (objetivo cero). Responsable: IT. Prioridad 1."
  },
  {
   "type": "backlog",
   "item": "Operaciones: confirmar hoy la directiva 1 (5 vídeos del 9 al 15 nov, 19:00–21:00 Madrid) y la conciliación de IDs de TikTok antes del viernes 13 nov. Responsable: Operaciones."
  },
  {
   "type": "owner_request",
   "title": "Publicación cruzada a Instagram Reels y YouTube Shorts",
   "body": "Recomendación: no abrirla todavía. Motivo: requiere crear cuentas nuevas y la cadena de TikTok aún no es estable (3 vídeos, 60–176 vistas, fiabilidad en validación). Coste: 0 € en herramientas, pero trabajo de Operaciones y revisión de Compliance por cada cuenta. Riesgo de abrirla ahora: duplicar errores y dispersar la audiencia antes de tener datos. Si dice que no: seguimos solo en TikTok y revisamos la decisión tras 10 vídeos publicados.",
   "apply_on_yes": {
    "accion": "abrir cuentas de Instagram y YouTube",
    "condicion": "revisión previa de Compliance y cadena TikTok estable"
   }
  }
 ]
}
```

### Operaciones
Acciones ejecutadas:
- decisión: Antes de cualquier render, validación automática obligatoria: (a) toda cifra en counter, chart, display u options lleva nota de hipótesis (capital, años, tipo) y marca 'ilustrativa'; (b) la cifra de pantalla coincide con la de la voz de esa escena; (c) si falla, el render se bloquea y se avisa a IT y Compliance. Responsable: IT. Plazo: antes del próximo render.
- decisión: Voz: no se cambia voice.edge_rate en episodios programados sin render de prueba. En episodios con cifras, la palabra 'ilustrativa' va al final de frase corta con pausa '...' y aparece en el note de pantalla. Revisión manual de cada escena con cifra. Responsable: Estudio.
- decisión: Sin cambios de catálogo de objetos hasta tener 10 vídeos publicados con datos completos. Se mantiene la rotación de al menos 3 tipos de objeto distintos entre episodios consecutivos. Responsable: Estudio.
- backlog: IT: implementar la validación automática del JSON (bloqueo + aviso) y registrar métricas semanales: número de bloqueos y episodios que llegan a Compliance sin hipótesis (objetivo cero). Responsable: IT. Prioridad 1.
- backlog: Operaciones: confirmar hoy la directiva 1 (5 vídeos del 9 al 15 nov, 19:00–21:00 Madrid) y la conciliación de IDs de TikTok antes del viernes 13 nov. Responsable: Operaciones.
- petición al dueño: Publicación cruzada a Instagram Reels y YouTube Shorts
