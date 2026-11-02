# Finroots · empresa automatizada

**Empieza aquí: [PANEL.md](PANEL.md)**, el panel de control que se actualiza solo: lo que necesita tu sí,
estado, episodios, reuniones, actividad, costes y directivas.

Un reel diario de educación financiera en TikTok (@finroots), hecho por un equipo de agentes de IA
que se reúnen, discuten, deciden, producen, revisan y publican sin intervención del dueño.

## Organigrama

```
                    Dueño (tú)
                        │  informe semanal en finroots/reports/
                 Consejo de administración  ── 3 consejeros: crecimiento, finanzas, riesgos (veto)
                        │  directivas en finroots/state/directives.md
                       CEO  ── decide la ficha de cada episodio y el plan semanal
   ┌──────────┬─────────┼──────────┬──────────┬────────────┬──────────┐
 Ideas    Marketing  Producto    Estudio   Compliance       IT      Operaciones
 trama y  ganchos,   valor y     guion y   veto legal,   validación, actas, KPIs,
 fichas   copys,     embudo de   escenas   cifras,       render,     backlog,
          hashtags   ingresos    del reel  avisos        TikTok      informes
```

Cada rol es un fichero en `company/` (puedes editarlos para cambiar su personalidad o criterio).
Todos comparten el mismo contexto: la biblia de la serie (`bible.md`), las directivas del consejo,
el historial de episodios, las métricas y el backlog.

## Qué pasa cada día (GitHub Actions, `finroots-daily.yml`)

1. **Comité diario.** Operaciones abre el acta → Ideas propone 3 fichas que continúan la trama →
   Marketing y Producto las critican → el CEO elige y cierra la ficha.
2. **Estudio** escribe el episodio como JSON de escenas (objetos del motor: móvil del banco, huchas,
   gráfica, calendario, bola de nieve, monedas, ticket, cartas…).
3. **IT** lo valida automáticamente; **Compliance** revisa cifras, avisos y riesgos. Si algo falla,
   vuelve al Estudio (máx. 2 vueltas). Sin aprobación de Compliance no se publica.
4. **Marketing** escribe la descripción, hashtags, dos ganchos alternativos y la hora.
5. **Render**: voz neural (edge-tts gratis, o ElevenLabs), efectos sintetizados, subtítulos karaoke
   sincronizados palabra a palabra, MP4 1080×1920 a 30 fps.
6. **Publicación en TikTok** y acta en `minutes/`. El vídeo también queda como artefacto en GitHub.

## Día y noche (`finroots-meetings.yml`)
Cada 4 horas hay una reunión de mejora con un tema distinto: contenido, crecimiento, monetización,
tecnología, finanzas y riesgos (los 6 temas cada día). El CEO cierra cada reunión con acciones que se
ejecutan solas (decisiones, backlog, biblia, ajustes técnicos) y el Estudio va escribiendo episodios
por adelantado hasta tener un colchón de 3. Qué pueden hacer solos y qué necesita tu sí está en
[`governance.md`](governance.md).

## Tu sí (Issues de GitHub)
Cuando los agentes necesitan algo que no pueden decidir solos (dinero, accesos, cambios de riesgo),
abren un Issue con la etiqueta `decision-dueño`. GitHub te avisa por email y en la app.
Respondes en el Issue **sí** o **no**, o escribes instrucciones. `finroots-owner.yml` lo lee al instante,
lo aplica, cierra el Issue y lo registra. Mientras esperan, siguen trabajando en todo lo demás.

## Límites: pausa y reanudación automática
Si se agota algo, la empresa se pausa sola, deja apuntado dónde se quedó y lo retoma al reiniciarse
el límite (`limits.py`). Pasa con la cuota de peticiones de Claude, con el saldo, con el tope de gasto
mensual, con el presupuesto diario (`budget.daily_usd`) y con los minutos de GitHub.
- Las reuniones aplazadas quedan en `state/agenda.json` y son las primeras al reanudar.
- Si el episodio del día no salió, la siguiente reunión lo recupera antes de nada.
- Los episodios del colchón ya están aprobados y con su copy, así que se pueden publicar aunque la IA esté en pausa.
- Solo te avisamos si hace falta tu acción, por ejemplo para recargar saldo. El panel muestra si hay una pausa y hasta cuándo.

## Registro
Nada se borra: actas de cada reunión en `minutes/`, informes en `reports/`, actividad en
`state/activity.jsonl`, costes de IA por día y por rol en `state/costs.json`, peticiones y tus
respuestas en `state/owner_requests.json`, decisiones de dirección en `state/ceo_decisions.md`.
Además, cada cambio queda como commit en GitHub.

Cada domingo (`finroots-board.yml`) el **consejo** lee las métricas reales de TikTok, escucha a
Operaciones, Marketing, Producto, IT y al CEO, vota y fija directivas. Te deja un informe en `reports/`.

## Puesta en marcha (lo que solo puedes hacer tú)

1. **Compliance de tu banco.** Antes de publicar, consulta la norma de actividades externas y guarda
   la respuesta por escrito (el plan original ya lo marca como paso 1).
2. **Clave de Claude.** GitHub → Settings → Secrets and variables → Actions → `ANTHROPIC_API_KEY`.
3. **App de TikTok**: guía paso a paso en [`CONECTAR_TIKTOK.md`](CONECTAR_TIKTOK.md). Resumen:
   - Crea una app, añade los productos *Login Kit* y *Content Posting API* (activa *Direct Post*).
   - Pide los permisos `user.info.basic`, `user.info.stats`, `video.upload`, `video.publish`, `video.list`.
   - URLs de términos y privacidad: `https://<tu-servicio>.onrender.com/terms` y `/privacy`.
   - Redirect URI: `https://<tu-servicio>.onrender.com/tiktok/callback`.
   - En Render, añade `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET` y redespliega.
   - Abre `https://<tu-servicio>.onrender.com/tiktok/connect`, entra con **@finroots** y copia el
     token que aparece en el secreto de GitHub `TIKTOK_REFRESH_TOKEN`. Añade también
     `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET` como secretos de GitHub.
   - Opcional: `GH_PAT` (token con permiso para escribir secretos) para rotar el token solo.
4. **Fusiona esta rama en `main`.** GitHub solo ejecuta los cron desde la rama por defecto.
   Puedes lanzar un día a mano desde Actions → "Finroots · comité diario" → *Run workflow*.

### Modos de publicación (`config.yaml → publishing.mode`)
- `draft` (por defecto): el vídeo llega a tus **borradores/bandeja de TikTok** y tú pulsas publicar
  (10 segundos al día). Funciona desde el primer día.
- `direct`: se publica solo. TikTok exige **auditar la app** antes; hasta entonces solo permite
  publicar en privado (`SELF_ONLY`). Cuando la aprueben, cambia a `direct`.

## Costes aproximados
- Claude: unos 5–10 $/día con el comité diario y las reuniones cada 4 horas (150–300 $/mes). Para
  bajarlo, espacia las reuniones (cron de `finroots-meetings.yml`) o baja el `effort` en `config.yaml`.
  Puedes bajar el `effort` de los roles en `config.yaml` para abaratarlo.
- Voz: gratis con edge-tts; ElevenLabs ~5–22 $/mes si quieres más calidad.
- GitHub Actions: gratis en repos públicos. En privados se usan unos 60–90 min/día y el plan gratuito
  (2.000 min/mes) no llega: hacen falta minutos de pago (unos 0,008 $/min) o hacer el repo público.

## Comandos locales
```bash
pip install -r finroots/requirements.txt && python -m playwright install chromium
python -m finroots.cli validate 2        # valida un episodio
python -m finroots.cli render 2          # genera video.mp4 + reel.html (vista previa)
python -m finroots.cli daily --no-publish
python -m finroots.cli board
```

## Subir la calidad (hoja de ruta de IT)
1. Voz premium (ElevenLabs: pon `ELEVENLABS_API_KEY` y `voice.elevenlabs_voice_id`).
2. Música de fondo con licencia.
3. Nuevos objetos en `render/template.html` (y su ficha en `episode.py`): cada objeto nuevo
   lo pueden usar los agentes al día siguiente.
4. Publicación cruzada en Instagram Reels y YouTube Shorts.
