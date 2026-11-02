# Conectar la cuenta de TikTok "finroots"

TikTok no deja publicar en una cuenta con su usuario y contraseña. El permiso se da en dos pasos:
1. Creas una "app" de TikTok para desarrolladores.
2. Abres un enlace, TikTok te muestra su pantalla oficial de permisos y pulsas **Autorizar**.

Puedes retirar el permiso cuando quieras desde TikTok: Ajustes → Seguridad → Apps y servicios.
Tiempo: unos 20 minutos, más la espera de revisión de TikTok.

**Antes de empezar, comprueba la dirección de tu servidor.**
Entra en <https://dashboard.render.com>, abre el servicio `tradingview-webhook-api` y copia la URL que
aparece arriba (termina en `.onrender.com`). Abajo uso `https://tradingview-webhook-api.onrender.com`;
si la tuya es distinta, cámbiala en todos los pasos. Abre `<tu URL>/privacy` en el navegador: tiene que
salir "Finroots · Política de privacidad". Si no sale, el servidor aún no tiene la última versión
(ver paso 0).

## Paso 0 · Que el servidor tenga la versión nueva
Render publica lo que hay en la rama `main`. Fusiona la rama de Finroots en `main` (o pídemelo y abro la PR)
y espera a que Render termine el despliegue (pestaña *Events*, unos 2 minutos).

## Paso 1 · Crear la cuenta de desarrollador
1. Entra en <https://developers.tiktok.com> → **Log in** con la cuenta de TikTok **finroots**.
2. Acepta los términos de desarrollador si te los pide.

## Paso 2 · Crear la app
1. Arriba a la derecha: tu perfil → **Manage apps** → **Connect an app** (o *Create app*).
2. Rellena **App details**:
   | Campo | Qué poner |
   |---|---|
   | App icon | `finroots/brand/finroots-icon.png` (1024×1024, en el repositorio) |
   | App name | Finroots |
   | Category | Education |
   | Description | Publica los vídeos educativos de finanzas del propio canal Finroots y consulta sus estadísticas. |
   | Terms of Service URL | https://tradingview-webhook-api.onrender.com/terms |
   | Privacy Policy URL | https://tradingview-webhook-api.onrender.com/privacy |
   | Platforms | **Web** → Website URL: https://tradingview-webhook-api.onrender.com |
3. Si TikTok pide **verificar el dominio o la URL**, te dará un fichero (algo como `tiktokAbC123.txt`) con un
   texto dentro. En Render → *Environment*, añade:
   - `TIKTOK_VERIFY_FILENAME` = nombre del fichero (p. ej. `tiktokAbC123.txt`)
   - `TIKTOK_VERIFY_CONTENT` = el texto de dentro

   Guarda, espera al redespliegue y pulsa **Verify** en TikTok.

## Paso 3 · Añadir productos y permisos
1. **Add products** → **Login Kit** → *Redirect URI* (Web):
   `https://tradingview-webhook-api.onrender.com/tiktok/callback`
2. **Add products** → **Content Posting API** → activa **Direct Post**.
3. **Scopes**: marca `user.info.basic`, `user.info.stats`, `video.upload`, `video.publish`, `video.list`.
4. Guarda (**Save**).

## Paso 4 · Pasar las claves al servidor y a GitHub
En la página de la app copia el **Client key** y el **Client secret**.
- **Render** → servicio → *Environment* → añade `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET` → *Save*.
- **GitHub** → repositorio `tradingview-webhook-api` → *Settings* → *Secrets and variables* → *Actions*
  → *New repository secret* → crea los mismos dos: `TIKTOK_CLIENT_KEY` y `TIKTOK_CLIENT_SECRET`.

## Paso 5 · Probar sin esperar la revisión (Sandbox)
1. En la app de TikTok for Developers, cambia a **Sandbox** (arriba) → *Create sandbox* si hace falta.
2. En el sandbox repite los productos y permisos del paso 3. Tiene sus propias claves: usa esas en el paso 4
   mientras pruebas.
3. **Target users** → añade la cuenta **finroots**.

## Paso 6 · Dar el permiso (lo que tú verificas)
1. Abre en el móvil o el ordenador: **https://tradingview-webhook-api.onrender.com/tiktok/connect**
2. TikTok mostrará "Finroots quiere acceder a tu cuenta" con la lista de permisos. Comprueba que la cuenta
   es **finroots** y pulsa **Autorizar**.
3. Aparecerá la página "Cuenta de TikTok conectada" con un código largo. Cópialo.
4. En GitHub crea el secreto **`TIKTOK_REFRESH_TOKEN`** con ese código.

## Paso 7 · Enviar la app a revisión
En la app (no en el Sandbox) pulsa **Submit for review**. TikTok pide:
- Una explicación de uso. Puedes pegar: "Herramienta interna del canal Finroots para subir sus propios
  vídeos educativos como borrador y leer sus estadísticas. Solo se usa con la cuenta finroots."
- Un vídeo corto de demostración. Graba con el móvil la pantalla mientras haces el paso 6 y luego abres
  los borradores de TikTok.

Cuando la aprueben, cambia en Render y GitHub las claves del Sandbox por las de producción y repite el paso 6.

## Paso 8 · Avisarnos
Responde **sí** en el Issue "Conectar la cuenta de TikTok @finroots" o dímelo en el chat. Desde la siguiente
ejecución, cada vídeo llegará a tus **borradores de TikTok** y tú pulsas publicar. Cuando TikTok apruebe
la app, te pediremos el sí para que se publique solo.
