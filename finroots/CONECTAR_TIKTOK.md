# Conectar la cuenta de TikTok "Finroots"

TikTok no permite que nadie publique en una cuenta con su usuario y contraseña. El permiso se da así:
1. Creas una "app" de TikTok para desarrolladores.
2. Abres un enlace y TikTok te muestra la pantalla oficial de permisos, donde pulsas **Autorizar**.

Puedes retirar el permiso cuando quieras desde TikTok: Ajustes → Seguridad → Apps y servicios.
Tiempo: unos 15 minutos, más la espera de revisión de TikTok.

> Dirección de tu API en Render (compruébala en el panel de Render; abajo uso esta):
> **https://tradingview-webhook-api.onrender.com**

## 1. Crear la app (developers.tiktok.com)
1. Entra en <https://developers.tiktok.com> con la cuenta de TikTok **Finroots** → *Manage apps* → *Connect an app*.
2. Rellena:
   - **App name:** Finroots
   - **Category:** Education
   - **Description:** Publica los vídeos educativos de finanzas del propio canal Finroots y lee sus estadísticas.
   - **Terms of Service URL:** https://tradingview-webhook-api.onrender.com/terms
   - **Privacy Policy URL:** https://tradingview-webhook-api.onrender.com/privacy
   - **Platforms:** Web → Website URL: https://tradingview-webhook-api.onrender.com
3. **Add products:**
   - *Login Kit* → Redirect URI: `https://tradingview-webhook-api.onrender.com/tiktok/callback`
   - *Content Posting API* → activa **Direct Post**.
4. **Scopes:** `user.info.basic`, `user.info.stats`, `video.upload`, `video.publish`, `video.list`.
5. Pulsa **Submit for review**. Mientras TikTok revisa, puedes usar la pestaña **Sandbox** y añadir la
   cuenta Finroots como *Target user* para probar.

## 2. Darle las claves al servidor
En <https://dashboard.render.com> → servicio `tradingview-webhook-api` → *Environment*, añade:
- `TIKTOK_CLIENT_KEY` = *Client key* de la app
- `TIKTOK_CLIENT_SECRET` = *Client secret* de la app

Guarda los cambios. Render redespliega solo. Las mismas dos variables van también en GitHub:
repositorio → *Settings → Secrets and variables → Actions → New repository secret*.

## 3. Dar el permiso (el paso que tú verificas)
Abre **https://tradingview-webhook-api.onrender.com/tiktok/connect**. TikTok te mostrará la pantalla
oficial "Finroots quiere acceder a tu cuenta", con la lista de permisos. Comprueba que es la cuenta
Finroots y pulsa **Autorizar**.

La página siguiente muestra un código largo. Cópialo en GitHub como secreto **`TIKTOK_REFRESH_TOKEN`**.

## 4. Avisar a los agentes
Responde **sí** en el Issue "Conectar la cuenta de TikTok @finroots". En la siguiente ejecución
publicarán solos, en modo borrador: el vídeo te llega a TikTok y tú pulsas publicar.
Cuando TikTok apruebe la app, los agentes te pedirán el sí para pasar a publicación automática total.
