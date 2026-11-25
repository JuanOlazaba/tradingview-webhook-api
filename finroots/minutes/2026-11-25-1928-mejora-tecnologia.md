# Reunión de mejora · Calidad de vídeo y tecnología · 2026-11-25-1928 UTC

### Operaciones
Orden del día: Voz, ritmo, nuevos objetos visuales, fiabilidad de la cadena, publicación cruzada.
Revisad lo publicado, las métricas, el backlog y las respuestas del dueño.

### IT
**IT (CTO) · Reunión de calidad de vídeo y tecnología · 25 nov**

Antes de tocar nada, la cadena necesita fiabilidad. Propongo:

**1. Fiabilidad de la cadena (prioridad 1).** El validador de JSON sigue sin confirmarse como operativo, y la directiva 3 lo exige antes del miércoles 25. Hoy no puedo certificar que esté activo, así que lo tomo como pendiente y no como hecho. Cambio: ningún render con cifras sin pasar el validador; si falla, bloqueo y aviso a IT y Compliance. Medida: bloqueos semanales y episodios que llegan a Compliance sin hipótesis (objetivo cero).

**2. Voz y ritmo.** No cambio `voice.edge_rate` sin render de prueba (decisión del 11 nov). Propongo un render de prueba con un episodio sin cifras y comparar duración y ritmo. Medida: duración final dentro de 55–75 s y revisión manual de una escena con cifra.

**3. Nuevos objetos visuales.** Sin cambios de catálogo hasta 10 vídeos con datos completos. Mientras, reutilizo los objetos existentes con rotación de al menos 3 tipos distintos.

**4. Publicación cruzada.** Descartada por ahora: añade cuentas nuevas y acceso de terceros, requiere el sí del dueño (#9 pendiente).

**Qué necesito del dueño:** nada nuevo. Recuerdo que la música con licencia y la voz premium siguen en pausa hasta que fije el umbral de audiencia.

**Coste:** 0 €. Sin datos reales de tokens y render todavía, no presento cifras de coste.

### Estudio
**Estudio · Guion y realización · 25 nov**

**1. Fiabilidad.** Respaldo a IT: sin validador confirmado, no renderizo ningún episodio con cifras. Añado una comprobación manual previa en cada escena con cifra: voz y pantalla coinciden, nota "ilustrativa" y hipótesis completa (capital, años, tipo). Los episodios sin cifras siguen adelante. Medida: 0 episodios que lleguen a Compliance sin hipótesis.

**2. Voz y ritmo.** Apoyo el render de prueba con un episodio sin cifras, sin tocar `edge_rate`. Medimos duración total (55–75 s) y palabras de voz (150–200). Los últimos reels publicados duraron 67, 78 y 89 s: dos se pasan del límite, así que el ajuste inicial va en el guion (frases más cortas, 12–13 escenas), no en la velocidad. En cifras, "ilustrativa" va al final de frase corta con "...".

**3. Objetos.** Sin cambios de catálogo. Mantengo la rotación de al menos 3 objetos distintos entre episodios consecutivos y evito repetir `display` como cierre fuerte siempre. Registro por ficha: tipo de gancho (pregunta o afirmación), formato y recuento de palabras.

**4. Publicación cruzada.** De acuerdo: pausada hasta el sí del dueño (#9).

**Dueño:** nada nuevo. **Coste:** 0 €, sin cifras de coste hasta tener datos reales.

### Operaciones
**Operaciones · Reunión de calidad de vídeo y tecnología · 25 nov**

Coincido con IT y Estudio. Antes de tocar voz o catálogo, hay que cerrar lo que las directivas ya exigen y no consta como hecho:

1. **Fiabilidad (prioridad 1).** El validador de JSON sigue sin confirmación de operativo. Lo registro como **pendiente**. Propongo que IT entregue hoy una evidencia concreta (prueba con un JSON con cifra sin nota de hipótesis que debe bloquearse) y que, si no llega, no se renderice ningún episodio con cifras. Estado de los retenidos (eps. 15, 17, 20, 23, 24) sin cambios.
2. **Voz y ritmo.** De acuerdo con el render de prueba sin cifras y sin tocar `edge_rate`. Lo mediremos con duración real (55–75 s) y palabras de voz (150–200). Dato a vigilar: 67, 78 y 89 s en los últimos reels; ajuste en guion, como propone Estudio.
3. **Objetos.** Sin cambios de catálogo. Rotación de 3 tipos distintos y registro de tipo de gancho, formato y recuento de palabras por ficha.
4. **Publicación cruzada.** Pausada. Requiere sí del dueño (#9) y no se pide de nuevo.

**Registro de hoy (datos reales):** 3 vídeos publicados; 186, 93 y 62 vistas a 24–72 h según métricas; sin conclusiones antes de 10 vídeos. Retención a 3 s no reportada (pendiente de confirmar en TikTok Studio).

**Qué necesito del dueño:** nada nuevo.

**Coste:** 0 €. Sin datos reales de tokens, voz ni render: no presento cifras de coste.

**Próximo paso:** IT entrega evidencia del validador hoy; Estudio prepara el render de prueba sin cifras.

### CEO
```json
{
 "summary": "La reunión de calidad de vídeo y tecnología acuerda priorizar la fiabilidad de la cadena: el validador de JSON sigue pendiente de confirmación, así que ningún episodio con cifras se renderiza sin pasar por él. La voz no se toca sin render de prueba; el ajuste de duración (55–75 s, 150–200 palabras) se hace en el guion, no en la velocidad. Sin cambios de catálogo de objetos ni publicación cruzada, que sigue pendiente del sí del dueño (#9).",
 "actions": [
  {
   "type": "decision",
   "text": "Ningún render con cifras sin evidencia escrita de IT de que el validador de JSON bloquea una cifra sin nota de hipótesis. Hasta entonces, solo se renderizan episodios sin cifras. Los eps. 15, 17, 20, 23 y 24 siguen retenidos."
  },
  {
   "type": "decision",
   "text": "Sin cambios en voice.edge_rate. Se hace un render de prueba con un episodio sin cifras para medir duración (55–75 s) y palabras de voz (150–200). Si el resultado se pasa, el ajuste se hace en el guion (frases más cortas, 12–13 escenas)."
  },
  {
   "type": "decision",
   "text": "Catálogo de objetos sin cambios hasta 10 vídeos con datos completos. Rotación de al menos 3 tipos distintos entre episodios consecutivos, y no repetir display como cierre fuerte siempre. Cada ficha registra tipo de gancho, formato y recuento de palabras."
  },
  {
   "type": "backlog",
   "item": "IT: entregar hoy evidencia del validador de JSON (prueba con cifra sin nota de hipótesis que debe bloquearse) y registrar bloqueos semanales y episodios que llegan a Compliance sin hipótesis (objetivo cero). Responsable: IT. Prioridad 1."
  },
  {
   "type": "backlog",
   "item": "Estudio: preparar y renderizar el episodio de prueba sin cifras, midiendo duración total y palabras de voz, y documentar el resultado en el registro. Responsable: Estudio, con Operaciones para la medición. Sin cambiar edge_rate."
  },
  {
   "type": "bible",
   "text": "Nota de continuidad (25 nov): el ritmo de la serie se ajusta con frases más cortas y menos escenas (12–13) antes que con la velocidad de voz. Las cifras de cualquier episodio nuevo siguen marcadas como ilustrativas con 'ilustrativa' al final de frase corta y pausa '...'."
  }
 ]
}
```

### Operaciones
Acciones ejecutadas:
- decisión: Ningún render con cifras sin evidencia escrita de IT de que el validador de JSON bloquea una cifra sin nota de hipótesis. Hasta entonces, solo se renderizan episodios sin cifras. Los eps. 15, 17, 20, 23 y 24 siguen retenidos.
- decisión: Sin cambios en voice.edge_rate. Se hace un render de prueba con un episodio sin cifras para medir duración (55–75 s) y palabras de voz (150–200). Si el resultado se pasa, el ajuste se hace en el guion (frases más cortas, 12–13 escenas).
- decisión: Catálogo de objetos sin cambios hasta 10 vídeos con datos completos. Rotación de al menos 3 tipos distintos entre episodios consecutivos, y no repetir display como cierre fuerte siempre. Cada ficha registra tipo de gancho, formato y recuento de palabras.
- backlog: IT: entregar hoy evidencia del validador de JSON (prueba con cifra sin nota de hipótesis que debe bloquearse) y registrar bloqueos semanales y episodios que llegan a Compliance sin hipótesis (objetivo cero). Responsable: IT. Prioridad 1.
- backlog: Estudio: preparar y renderizar el episodio de prueba sin cifras, midiendo duración total y palabras de voz, y documentar el resultado en el registro. Responsable: Estudio, con Operaciones para la medición. Sin cambiar edge_rate.
- biblia: Nota de continuidad (25 nov): el ritmo de la serie se ajusta con frases más cort
