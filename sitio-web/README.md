# Sitio web de DeepDatas

Sitio institucional renovado de [deepdatas.com](https://deepdatas.com): un sitio estático de varias páginas, pensado para publicarse en **Azure Static Web Apps**. Incluye una pequeña API (Azure Functions, Python) para el formulario de contacto.

## Páginas

| Ruta | Contenido |
| --- | --- |
| `/` | Propuesta de valor (datos e IA para distribuidoras, pymes y consumo masivo), clientes, industrias, desafíos que resolvemos, recorrido de los datos hasta un agente de IA, casos, testimonios, formas de empezar |
| `/industrias/…` | Una página por industria (consumo masivo, distribuidoras mayoristas, pymes, retail, materiales eléctricos y construcción, autopartes y repuestos, industria y manufactura y agro): desafíos, soluciones, indicadores, tablero de ejemplo, casos, testimonios, preguntas frecuentes y notas del blog |
| `/inteligencia-artificial/` | IA para empresas: casos de uso, conversación de ejemplo con un agente, gráfico de datos para IA, principios de seguridad, proceso y preguntas frecuentes |
| `/blog/` y `/en/blog/` | Artículos (uno por archivo en `blog/es/` y `blog/en/`), cada uno en `/blog/<archivo>/` o `/en/blog/<archivo>/` |
| `/diagnostico/` | Oferta de diagnóstico de datos: entregables, ejemplo de informe (datos ficticios), proceso, preguntas frecuentes y formulario |
| `/autoevaluacion/` | Autoevaluación de 6 preguntas: puntaje de 0 a 100, nivel y prioridades al instante; se puede guardar en PDF y dejar los datos de contacto |
| `/servicios/` | Detalle de los cuatro servicios, niveles de analítica, formas de trabajo y tecnología |
| `/ejemplos/` | Tres tableros interactivos de ejemplo (datos ficticios) con el desafío, la solución y el beneficio |
| `/nosotros/` | Misión, pilares, especialidades del equipo y ubicación |
| `/contacto/` | Formulario, medios de contacto, mapa y preguntas frecuentes |
| `/gracias/` | Confirmación del formulario cuando el navegador no tiene JavaScript |
| `/404.html` | Página de error (en español, con un enlace a la versión en inglés) |
| `/en/...` | Versión en inglés de todas las páginas salvo el blog (ver «Versión en inglés») |

## Estructura

```
build.py                 Genera el sitio en public/ a partir de src/
blog.py                  Lee los artículos de blog/<idioma>/ (Markdown)
blog/es/, blog/en/       Artículos del blog, uno por archivo .md, en cada idioma
contenido/linkedin.md    Publicaciones sugeridas para LinkedIn (no se publica en el sitio)
contenido/testimonios.md Guía para pedir testimonios a los clientes (no se publica en el sitio)
casos.py                 Casos de éxito (se publican al marcarlos como publicados)
testimonios.py           Testimonios de clientes (se publican con su autorización)
industrias.py            Textos de las páginas por industria, en español e inglés
dashboards.py            Datos ficticios de los tableros de ejemplo
pipeline.py              Textos (en los dos idiomas) y geometría del gráfico «Del dato disperso al agente de IA»
i18n.py                  Rutas de cada página en español e inglés y textos de los componentes compartidos
requirements.txt         Dependencias para generar el sitio (Jinja2)
src/layout.html          Estructura común: encabezado, menú, pie y metadatos
src/forms.html           Formulario de contacto (se usa en Contacto y en Diagnóstico)
src/testimonials.html    Testimonios (inicio, casos e industrias)
src/charts.html          Componentes de los gráficos de los tableros de ejemplo
src/pipeline.html        Gráfico interactivo de orígenes de datos, curado y agente de IA (Servicios e IA)
src/flow.html            Inicio: una pregunta recorre los sistemas, el curado y el agente de IA (textos en los dos idiomas)
src/pages/               Contenido de cada página (en src/pages/en/, la versión en inglés)
src/mapa.html            El mapa de la oficina: la imagen del barrio y el de Google, que se carga al pedirlo
src/hero.html            Portada del inicio: la pregunta en voz alta, con tres preguntas que se eligen, y la red de cinco sistemas que se unen en un núcleo (textos en los dos idiomas)
src/icons/               Íconos SVG (Bootstrap Icons, licencia MIT)
src/assets/              CSS, JavaScript, tipografías e imágenes
tools/                   Generadores de imágenes y video: íconos de vidrio, la imagen del cierre de cada página (nucleo.cjs), la foto que usaba la portada vieja —revelado y agrandado— (portada_foto.py, a partir de tools/hero/portada-original.webp, hoy sin uso), la imagen del mapa de la oficina (mapa.py) y el control del camino de publicación de casos y testimonios (probar_publicacion.py), el control de la portada del inicio (probar_portada.cjs), la foto retocada de otra oficina (hero_foto.py, hoy sin uso) y el video del asistente de la página de IA (video/)
src/staticwebapp.config.json  Seguridad, caché, página 404 y redirecciones
public/                  Sitio generado: es lo que se publica (no editar a mano)
api/contacto/            Función que recibe el formulario y envía el correo
azure-static-web-apps-*.yml   Pipeline de Azure DevOps para publicar
```

## Editar el sitio

1. Modificá los archivos de `src/` (los textos están en `src/pages/`; los colores y tipografías, al inicio de `src/assets/css/site.css`).
2. Generá el sitio:

   ```
   pip install -r requirements.txt
   python build.py
   ```

3. Revisalo localmente con `python -m http.server 8000 --directory public` y abrí http://localhost:8000.
4. Subí los cambios **incluyendo la carpeta `public/`**: Azure publica esa carpeta tal cual.

`build.py` también genera `sitemap.xml` y `robots.txt`, y agrega a los enlaces de CSS y JavaScript un código de versión para que los navegadores siempre descarguen la última versión.

## Lo que ve el buscador

**Título y descripción.** Cada página los declara en `PAGES` / `PAGES_EN` (`build.py`), las de industrias en `industrias.py` y los artículos en su propio encabezado. Google los corta: **60 caracteres el título y 160 la descripción**. Al final de cada generación, `build.py` avisa qué textos se pasaron y por cuánto; si aparece el aviso, acortalos antes de publicar. Los límites están en `TITULO_MAX` y `DESCRIPCION_MAX`.

Un artículo puede llevar un título más corto solo para el buscador (`seo_title` en su encabezado): arriba del artículo se sigue leyendo el `title` largo y en la pestaña y en Google va el corto. Si no lleva `seo_title`, se usa el `title`.

**Preguntas frecuentes.** Las páginas que tienen preguntas (diagnóstico, IA, contacto, tablero de ventas y las ocho de industrias, en los dos idiomas) publican además el marcado `FAQPage`, que es lo que le permite a Google mostrarlas desplegadas debajo del resultado. Sale de la misma lista `(pregunta, respuesta)` que arma la página, con `{{ faq_schema(faqs) }}` dentro de su `{% block head %}` —en `industria.html`, `{{ faq_schema(ind.faqs) }}`—, así el marcado y lo que se ve no se pueden separar. **Google pide que la respuesta esté visible en la página**: no agregues al marcado preguntas que no estén también en el `<details>`. Si una página nueva tiene preguntas, sumale ese bloque.

**Datos estructurados que ya hay:** `ProfessionalService` en el inicio (en los dos idiomas), `BlogPosting` en cada artículo y `FAQPage` en las 23 páginas con preguntas.

## Versión en inglés

El sitio se publica en español (raíz) y en inglés (`/en/`), el blog incluido.

- Cada página en inglés tiene su plantilla en `src/pages/en/`, con el mismo nombre de archivo que la española. Sus títulos y descripciones están en `PAGES_EN` (`build.py`) y sus rutas en `ROUTES` (`i18n.py`).
- Los textos de los componentes que comparten todas las páginas (menú, pie, formularios, planes, logos, tableros y gráfico de datos) están en `i18n.py`; los de la escena del inicio, en `src/hero.html`; los de los tableros de ejemplo, en `dashboards.py`; los de los casos, en `CASES_EN` (`casos.py`); los de las industrias, en `industrias.py`, y las traducciones de los testimonios, en `testimonios.py`.
- En las plantillas, los enlaces internos se escriben con `{{ url('servicios') }}` para que apunten a la página del mismo idioma.
- Cada página enlaza su versión en el otro idioma desde el encabezado y el pie, y declara las dos versiones con `hreflang` (también en `sitemap.xml`).
- Al cambiar un texto en español, actualizá también la versión en inglés.

## El mapa de la oficina

En `/contacto/` y `/nosotros/` el mapa de Google venía en un `iframe`. Aunque llevaba `loading="lazy"`, las dos páginas son cortas y el mapa entra en pantalla enseguida, así que **cargaba siempre: unos 400 KB de JavaScript de terceros y entre 20 y 30 pedidos**, los mire o no el visitante.

Ahora esas páginas muestran primero una imagen del barrio (`src/mapa.html`) y el mapa de Google se carga recién al tocar **«Ver el mapa»** (`site.js`). Sin JavaScript el enlace sigue andando: abre Google Maps en otra pestaña, igual que si se lo abre con ctrl o con la rueda del mouse.

La imagen la arma `tools/mapa.py` con los mosaicos de **OpenStreetMap**: baja los que cubren el encuadre, los pega, recorta y marca la dirección. Escribe `src/assets/img/mapa/oficina-{800,1600}.webp` (la grande cubre el mismo terreno con el doble de detalle, para pantallas de alta densidad). Los mosaicos quedan guardados en `tools/mapa-cache/`, que no se sube, y la imagen ya armada se versiona: el sitio no le pega al servidor de mosaicos al compilar.

**Licencia.** Los datos son de OpenStreetMap, con licencia ODbL, y **la atribución tiene que verse junto al mapa**: va en `src/mapa.html`, abajo a la derecha de la imagen, y no se saca. Si se muda la oficina, cambiá `DIRECCION` en `tools/mapa.py` (las coordenadas salen de Nominatim), volvé a correrlo y actualizá la dirección en las páginas y en `i18n.py`.

## Agenda online

Los botones «Coordinar llamada» abren en otra pestaña la página de reservas de Microsoft Bookings (`BOOKING_URL` en `build.py`). Para cambiarla (por ejemplo, por Calendly), reemplazá el enlace y regenerá el sitio; si lo dejás vacío, los botones vuelven a llevar al formulario de contacto. La política de privacidad menciona Microsoft Bookings mientras haya un enlace configurado. Contacto también ofrece la agenda antes del formulario, y Clarity registra cada clic como `agendar_reunion`.

## Publicación en Azure Static Web Apps

El pipeline `azure-static-web-apps-lemon-water-04480390f.yml` es el mismo que usa hoy el sitio en producción, con dos cambios:

- `app_location: "public"`: publica el sitio generado.
- `api_location: "api"`: publica la función del formulario de contacto.

Para reemplazar el sitio actual, copiá el contenido de esta carpeta a la raíz del repositorio de Azure DevOps y hacé push a `main`. Las ramas `dev` y `release` generan entornos de prueba.

## Formulario de contacto

La función `api/contacto` valida la consulta, descarta spam (ver [Contra los bots](#contra-los-bots)) y envía el correo con **Microsoft Graph** desde el buzón de Microsoft 365 (Office 365 ya no acepta el envío por SMTP con usuario y contraseña). Configuración única:

1. En el [portal de Azure](https://portal.azure.com) > **Microsoft Entra ID** > **Registros de aplicaciones** > **Nuevo registro**.
2. **Permisos de API** > **Microsoft Graph** > **Permisos de aplicación** > `Mail.Send` > **Conceder consentimiento de administrador**.
3. **Certificados y secretos** > **Nuevo secreto de cliente**. Copiá el valor y anotá su vencimiento.
4. Recomendado: limitá la aplicación para que solo pueda enviar desde `fbloise@deepdatas.com` ([RBAC para aplicaciones en Exchange Online](https://learn.microsoft.com/exchange/permissions-exo/application-rbac)).
5. En la Static Web App > **Configuración** > **Variables de entorno**:

| Variable | Valor |
| --- | --- |
| `GRAPH_TENANT_ID` | Id. de directorio (inquilino) |
| `GRAPH_CLIENT_ID` | Id. de aplicación (cliente) |
| `GRAPH_CLIENT_SECRET` | Valor del secreto del paso 3 |
| `MAIL_SENDER` | Opcional. Buzón que envía (por defecto `fbloise@deepdatas.com`) |
| `CONTACT_RECIPIENTS` | Opcional. Destinatarios separados por coma (por defecto, el mismo buzón) |
| `TURNSTILE_SECRET` | Opcional. Clave secreta del Turnstile (ver abajo). Vacía = sin verificación |

Mientras no esté configurado, el formulario muestra un aviso con el email de contacto en lugar de fallar en silencio.

### Contra los bots

Tres capas, de la más barata a la más efectiva:

1. **Campo trampa.** Un campo `website` escondido fuera de pantalla que una persona no ve. Si llega completo, la función responde «enviado» y descarta el mensaje, sin avisar que lo detectó: así el bot no aprende a esquivarlo. Frena a los que completan todo el HTML, no a los que manejan un navegador de verdad.
2. **Límite por IP.** Cinco envíos cada diez minutos. Vive en la memoria de cada instancia de la función, así que se reinicia en cada arranque en frío y no se comparte entre instancias: frena ráfagas de un mismo origen, no reemplaza un firewall.
3. **[Turnstile](https://developers.cloudflare.com/turnstile/) de Cloudflare.** Es el que realmente separa personas de bots. El widget deja un token en el formulario y `api/contacto` lo valida contra Cloudflare antes de enviar el correo; la validación es del lado del servidor, que es lo que un bot no puede saltear. Es gratis, no exige que el sitio esté en Cloudflare y no rastrea al visitante.

**Para activarlo**, en [dash.cloudflare.com](https://dash.cloudflare.com) > **Turnstile** creá un widget para `deepdatas.com` y después, **en este orden**:

1. Pegá la **clave de sitio** (la pública) en `TURNSTILE_SITE_KEY`, en `build.py`, y publicá. Hasta acá el widget ya se ve, pero todavía no se verifica nada.
2. Cargá la **clave secreta** en `TURNSTILE_SECRET`, en las variables de entorno de la Static Web App.

Al revés queda roto un rato: el servidor pediría un token que las páginas publicadas todavía no traen y rechazaría todas las consultas. Con cualquiera de las dos vacía, el formulario funciona como antes.

Dos cosas que conviene saber antes de activarlo:

- **El Turnstile necesita JavaScript.** Hoy el formulario funciona sin JS (envío tradicional y redirección a `/gracias/`); con el Turnstile activo, quien lo tenga desactivado no puede generar el token y recibe el aviso con el email de contacto. Es inherente a cualquier CAPTCHA, no a esta implementación.
- **Si no se puede consultar a Cloudflare** (está caído, se cortó la red), el envío pasa y queda anotado en los registros. Entre perder consultas reales durante una caída ajena y que se cuele spam un rato, lo segundo es más barato, y las otras dos capas siguen en pie. Lo que nunca se ignora es un «no» de Cloudflare.

El Turnstile distingue bots de personas; no valida identidad. No comprueba que quien escribe sea quien dice ser.

Los formularios envían el idioma de la página (`lang`): la función responde en ese idioma, sin JavaScript redirige a `/gracias/` o `/en/thank-you/`, y los correos que llegan desde la versión en inglés tienen el asunto con `[EN]`. Las consultas de la autoevaluación llegan con el interés «Autoevaluación de datos» (o «AI readiness check») y el resultado con todas las respuestas en el mensaje.

## Blog

El blog va en los dos idiomas: `blog/es/` se publica en `/blog/` y `blog/en/` en `/en/blog/`. Para publicar un artículo, creá un archivo `.md` en la carpeta del idioma (por ejemplo `blog/es/mi-articulo.md`, que se publica en `/blog/mi-articulo/`) con este encabezado y el texto en Markdown debajo:

```
---
title: Título del artículo
seo_title: Título corto para la pestaña y Google
description: Resumen de unas 25 palabras para Google y LinkedIn
date: 2026-10-20
tags: Power BI, Tableros de gestión
cta: diagnostico
es: mi-articulo
---
```

`seo_title` es opcional y sirve cuando el título del artículo es largo: en la página se sigue leyendo el `title` y en la pestaña va el corto, que con « | DeepDatas» tiene que entrar en 60 caracteres. La `description` no puede pasar de 160. `cta` define el llamado a la acción del final: `diagnostico`, `casos` o `ia`. Los artículos con fecha futura no se publican hasta que se vuelva a generar el sitio en esa fecha. Cada artículo se suma solo al blog, al inicio, al sitemap y a los artículos relacionados.

**`es` solo va en los artículos en inglés** y dice de qué artículo en español son traducción (su nombre de archivo, sin `.md`). De ahí salen tres cosas: el `hreflang` que relaciona las dos versiones, el enlace del encabezado al otro idioma y las notas que muestra cada página de industria, que en `industrias.py` se listan con el nombre del artículo en español. Un artículo en inglés sin `es` se publica igual, pero queda suelto: sin par y sin aparecer en las industrias.

Cada idioma lleva su propio nombre de archivo, así que la dirección en inglés se escribe en inglés (`/blog/calidad-de-datos/` ↔ `/en/blog/data-quality/`). Los enlaces dentro del texto de un artículo se escriben a mano: al traducir hay que apuntarlos a la versión en inglés (`/en/blog/…`, `/en/dashboard-examples/`).

## Casos de éxito

Los casos están en `casos.py`. Cada uno tiene `'publicado': False` hasta que se completen sus datos reales:

1. Reemplazá cada `[completar]` por el dato real (resultados, duración) y, si el cliente lo autoriza, agregá su logo. El testimonio del cliente va en `testimonios.py` (ver «Testimonios»).
2. Revisalo con `python build.py --borradores` y abrí la carpeta `vista-previa/` (no se sube al repositorio).
3. Cambiá `'publicado'` a `True` y ejecutá `python build.py`.

Con al menos un caso publicado aparecen la página `/casos/`, el ítem «Casos» del menú y la sección de casos del inicio. `build.py` no deja publicar un caso que todavía tenga datos `[completar]`.

## Diseño 2026: «luz sobre los datos»

Las secciones claras (marfil) cuentan la historia del negocio y las «profundas» (azul noche, `section-deep`) muestran dónde viven los datos, con el naranja de la marca y una luz azul como fuentes de luz. Los estilos del rediseño están en `src/assets/css/design.css` (se carga después de `site.css`) y sus interacciones en `src/assets/js/design.js`:

- **Núcleo de datos** (`[data-core]`, inicio, sección clara): una constelación de registros dibujada en vivo en un `canvas` (`design.js`, sin librerías ni imágenes). Cada punto lleva el color del sistema donde vive hoy (ERP, CRM, planillas, WhatsApp, correo); con el scroll los puntos viajan desde cinco nubes hasta una esfera ordenada que se enciende desde el centro, como en apple.com. Mientras están dispersos, el cursor los aparta; una vez ordenados, la esfera lo sigue. Sin animación se dibuja una sola vez el estado final. Los nombres de los sistemas que se ven sobre las nubes salen de `data-labels` (uno por idioma). La etapa es pegajosa desde arriba y el encabezado flota encima, así que `size()` baja las nubes de arriba lo necesario para que su nombre no quede debajo del encabezado: el cálculo sale de `--header-h`, no de un número fijo, y por eso aguanta cualquier alto de ventana. `poster.webp` (`src/assets/img/core/`, generado con `tools/nucleo.cjs`) ya solo se usa en el cierre de cada página.
- **Pregunta y respuesta** (`src/flow.html`, `[data-flow]`, inicio, debajo del núcleo): una pregunta recorre los cinco sistemas, el curado los convierte en un solo modelo y el agente de IA escribe la respuesta con sus fuentes. Es HTML con líneas SVG (`design.js`): el recorrido se reproduce al entrar en pantalla, cada pregunta de ejemplo lo vuelve a reproducir con su respuesta y, al pasar el cursor por un sistema, se ilumina su camino. Los textos de los dos idiomas están en el mismo archivo (datos ficticios). Sin animación o sin JavaScript se ve el estado final con la primera respuesta. El gráfico detallado del recorrido (`src/pipeline.html`) sigue en Servicios y en la página de IA.
- **Portada del inicio: la pregunta en voz alta y la red que la alimenta** (`src/hero.html`, estilos `.vz*` en `design.css`, movimiento en `design.js`): «Una pregunta. Todos tus sistemas. *Una sola respuesta.*» Dos filas sobre las mismas columnas, así los sistemas quedan debajo del título y el núcleo debajo de la respuesta.
  **Arriba, lo que manda.** El título, el texto y los botones a la izquierda, alineados con el logo del encabezado; a la derecha, **una tablet apaisada en su soporte, sobre el escritorio** (`.vz-escena`): en su pantalla vive la demostración, con el micrófono, lo que se está preguntando y la onda. Debajo, **tres preguntas que se eligen de verdad** (ventas de ayer, clientes que se fueron, riesgo de quiebre): la elegida queda marcada con el relleno y con un tilde —el color no es el único aviso—, se escribe sola en la barra y abajo aparece su respuesta con los tres sistemas de donde salió cada número. **Es una demostración, no un micrófono**: no usa la Web Speech API, así que no pide permiso al entrar, no manda audio a ningún lado y funciona en cualquier navegador; para una consultora que vende confidencialidad eso no es un detalle. La respuesta lleva la pastilla «demo · datos ficticios». Una copia invisible de la pregunta (`.vz-said-ghost`) reserva el alto de la barra, así no crece renglón a renglón mientras se escribe ni empuja lo que tiene abajo.
  **La escena de la tablet** (`.vz-escena`). El marco sigue el mismo lenguaje que el teléfono de más abajo —marco oscuro, filete por dentro y sombra profunda— pero **sin proporción fija**: el alto lo manda el contenido, que cambia con el idioma, así nunca se corta nada. Como la pantalla es apaisada, la respuesta se reparte en dos columnas (el número a la izquierda, el detalle a la derecha) y las fuentes cruzan abajo; la pregunta no se repite en la tarjeta, porque ya se lee en la barra, pero sigue ahí para los lectores de pantalla, que de la barra no leen nada.
  **El giro** (`.vz-dispositivo`, `rotateY(-9deg)`): el canto derecho se acerca y el izquierdo se va para atrás, así la tablet «mira» hacia el texto, y de paso se ve de costado la pata trasera (`.vz-stand`), que es lo que le da cuerpo al conjunto. La escena además baja dos centímetros y se achica un 10%, las dos cosas en el `transform`: el desplazamiento para no mover al resto de la maqueta, y la escala porque achicar el ancho a secas partiría los textos de adentro en más renglones y la pantalla dejaría de ser apaisada. Es poco ángulo y con mucha distancia de cámara a propósito: adentro hay texto y botones de verdad, y pasarse los deja borrosos y más difíciles de tocar. En una sola columna —celular— el giro se apaga: la pantalla es chica y leerla en ángulo cuesta.
  **El escritorio** (`.vz-piso`) es un plano acostado con `rotateX(74deg)` desde su borde de atrás, que viene hacia quien mira; se desvanece en los bordes con una máscara, para que sea la sugerencia de una mesa y no una mesa recortada, y lleva la sombra del apoyo. Su ancho se calcula con `min(132%, 100% + 2 gutter)` y la sección recorta a lo ancho (`overflow-x: clip`, que a diferencia de `hidden` no crea un contenedor de scroll), porque el plano se ensancha al acostarse y empujaría la página.
  **Si se toca el ancho de la tablet**, hay que mirar que las tres preguntas sigan entrando en un renglón: si saltan a dos, la pantalla deja de ser apaisada.
  **Abajo, la red.** Los cinco sistemas (ERP, CRM, Planillas, WhatsApp, Correo), las curvas que los unen en un solo núcleo —la misma constelación de registros que cuenta el núcleo de datos de más abajo, dibujada en el mismo `canvas` y con los mismos colores por sistema— y, desde ahí, una línea que sube hasta la respuesta. Varios sistemas, un solo número.
  **Los datos viajan por las curvas**: fluyen despacio solos, para que la portada no esté muerta al entrar, y **el scroll los empuja** (`POR_PIXEL`), así bajar la página mueve la información de los sistemas al núcleo y del núcleo a la respuesta. Cada pregunta manda una tanda nueva: los datos se encienden y el núcleo se aviva durante 2,4 s.
  **Las curvas no están en el HTML.** `design.js` las calcula midiendo dónde quedó cada pastilla, el núcleo y la tarjeta de la respuesta, porque eso depende del ancho, del largo de los textos y del idioma. Si la maqueta está apilada —una sola columna, en celular— los sistemas quedan arriba del núcleo en vez de a su costado: lo detecta y engancha las curvas por abajo de cada pastilla, bajando en vez de cruzar. La capa de curvas (`.vz-wires`) va detrás de las pastillas y de las tarjetas, cubriendo toda la portada, porque la línea de salida tiene que llegar a la fila de arriba.
  **Los tres estados.** Sin animación (`prefers-reduced-motion`) quedan las curvas y el núcleo ya formado, sin datos viajando, y los botones siguen respondiendo, pero al instante. Sin JavaScript se lee la primera pregunta con su respuesta ya escrita en el HTML, y lo que no haría nada —el botón del micrófono, las tres preguntas y la red entera, que dibuja JavaScript— no se muestra; el micrófono queda como dibujo.
  En pantallas bajas (una notebook de 1280 × 800) la portada entera no entra en `100svh`, así que se aprieta en vez de dejar la última fuente cortada al medio.
  `node tools/probar_portada.cjs` (después de `python3 build.py`) recorre la matriz —los dos idiomas × escritorio y celular × con animación, sin animación y sin JavaScript— con la política de seguridad de producción puesta y controla contraste, zonas para tocar, scroll horizontal, teclado, que la barra no cambie de alto mientras escribe, que cada pregunta traiga su respuesta y sus fuentes, y que cada curva arranque en su sistema y termine en el núcleo o en la respuesta.
- **La imagen que usaba la portada vieja** ya no se publica, pero el original queda en `tools/hero/portada-original.webp` por si se vuelve a usar. Está **generada con IA** (Gemini / Nano Banana, de Google): no es la foto de una oficina real y la persona que aparece no existe, así que no hay derecho de imagen que ceder ni autor humano al que atribuir. Los términos de Google no reclaman la propiedad de lo generado y permiten usarlo comercialmente (verificado el 27 de octubre de 2026; si cambian, hay que volver a mirarlo). Dos cosas presentes: lleva la marca de agua invisible **SynthID**, que la deja identificable como generada, y el nivel de consumidor de Gemini no incluye la indemnización que Google sí ofrece en sus productos empresariales.
- **Portadas**: Nosotros, Servicios y Contacto usan fotos de Unsplash (licencia de Unsplash, uso comercial sin atribución) recortadas en `src/assets/img/covers/`: equipo trabajando en una oficina luminosa ([Vitaly Gariev](https://unsplash.com/photos/CXxH2EiX760)) para Nosotros, un consultor ayudando frente a la pantalla en un loft ([Proxyclick](https://unsplash.com/photos/l90zRbWvCoE), espejada) para Servicios y una oficina abierta con luz natural ([Arlington Research](https://unsplash.com/photos/kN_kViDchA0), espejada) para Contacto. La persona o el grupo va a la derecha, porque el texto ocupa la izquierda.
- **Carrusel de industrias** (`[data-rail]`), **teléfono con el asistente** (`[data-pin]`, los pasos cambian la pantalla), **brillo que sigue al cursor** (`.glow-card`), encabezado que pasa a claro sobre los paneles profundos (`[data-deep]`) y transición entre páginas en los navegadores que la soportan.

## Video del asistente

El encabezado de la página de IA muestra un video de 32 segundos del asistente respondiendo tres preguntas (ventas de ayer, clientes que dejaron de comprar y productos por quedarse sin stock), sin sonido y en bucle, con datos ficticios. No es una grabación: se renderiza cuadro a cuadro desde `tools/video/escena.html` (un guion determinista en el que cada instante se calcula a partir del tiempo) con `tools/video/render.cjs`, y `tools/video/codificar.sh` lo convierte a `src/assets/video/asistente-{es,en}.{mp4,webm}` más el cuadro de portada `.webp`. Para cambiar textos o cifras, editá `escena.html` y volvé a correr el script. Para reemplazarlo por una grabación real del asistente, exportala en 1280 × 800 (16:10), sin sonido, y guardala con los mismos nombres.

## Animaciones al hacer scroll

Inspiradas en apple.com y hechas sin librerías (`src/assets/js/motion.js` y `site.js`):

- Todo elemento con la clase `reveal` sube y aparece al entrar en pantalla; los hermanos entran en cascada. Los títulos de esos bloques entran palabra por palabra y el encabezado de cada página interior se anima al cargar.
- Un título con `data-scroll-lit` (y la clase `statement` para el tamaño grande) se ilumina palabra por palabra a medida que se avanza: la frase del problema en el inicio y la misión en Nosotros.
- La cadena de cuatro pasos del inicio (`.chain`) va en horizontal: al entrar en pantalla la línea se dibuja, los nodos se encienden en orden y un paquete de datos la recorre; en pantallas angostas se desliza de lado.
- Las cifras del inicio y de los casos cuentan desde cero al aparecer.

Con «reducir movimiento» activado en el sistema, o sin JavaScript, no hay animaciones y todo se ve desde el principio. Si `site.js` no llegara a cargar, el contenido aparece igual a los pocos segundos.

## Testimonios

Los testimonios están en `testimonios.py` y la guía para pedirlos a los clientes (mensaje, preguntas, autorización y consejos para grabar un video de 30 segundos) en `contenido/testimonios.md`. Tienen que ser reales: el texto lo escribe o lo aprueba el cliente.

1. Completá el borrador (texto, nombre, cargo y empresa; foto y video opcionales) y en `consent` anotá cómo y cuándo autorizó la publicación.
2. Revisalo con `python build.py --borradores`.
3. Cambiá `'publicado'` a `True` y ejecutá `python build.py`.

Cada testimonio publicado aparece en la sección «Lo que dicen nuestros clientes» del inicio, dentro de su caso de éxito (`case`) y en la página de su industria (`industry`). `build.py` no deja publicar un testimonio al que le falte alguno de los datos obligatorios —texto, nombre, cargo, empresa y autorización— y la compilación se detiene diciendo cuál falta.

**La traducción al inglés es opcional.** Un testimonio completo en español se publica igual: en la versión en inglés se muestra la cita en su idioma original, marcada como «Traducida del español» cuando sí hay traducción y con `lang="es"` cuando no la hay. Se puede traducir solo una parte (por ejemplo el cargo y la empresa, pero no la cita): lo que quede en `[completar]` cuenta como «todavía no traducido» y no se muestra.

Ese camino solo corre el día que se publica algo, así que puede romperse sin que nadie lo note. `python tools/probar_publicacion.py` lo ejercita con datos de mentira en memoria —sin tocar los reales ni escribir nada— y controla que la puerta de publicación, la traducción opcional y el aviso de qué falta sigan funcionando. Conviene correrlo después de tocar `testimonios.py` o `casos.py`.

## Industrias

Las páginas de `/industrias/` (consumo masivo, distribuidoras mayoristas, pymes, retail, materiales eléctricos y construcción, autopartes y repuestos, industria y manufactura y agro; en inglés, en `/en/industries/…`) se generan con la plantilla `src/pages/industria.html` a partir de `industrias.py`: desafíos, soluciones, indicadores, preguntas frecuentes, y qué casos, tablero de ejemplo, logos y notas del blog mostrar. Las rutas están en `i18n.py` (`ind-<id>`). Para sumar una industria, agregala en `industrias.py` (textos en los dos idiomas, datos comunes y `ORDER`) y su ruta en `i18n.py`; aparece sola en el inicio, en el pie y en el sitemap. Para quitar una, hacé lo inverso y agregá en `src/staticwebapp.config.json` una redirección de su dirección vieja (en los dos idiomas) a `/#industrias`, así los enlaces guardados no caen en un error. Solo se muestran los casos publicados; no sumes resultados que no estén en un caso real.

## Analítica de visitas

El sitio está preparado para [Microsoft Clarity](https://clarity.microsoft.com) (gratuito): visitas, origen del tráfico, mapas de calor y grabaciones de sesión. Mientras `CLARITY_ID` esté vacío en `build.py`, no se carga nada externo.

1. Creá un proyecto en Clarity para `deepdatas.com` y copiá su identificador (Settings > Overview > Project ID).
2. Recomendado: en Settings > Setup, desactivá las cookies y dejá el enmascarado de datos en modo estricto.
3. Pegá el identificador en `CLARITY_ID` y ejecutá `python build.py`: se agrega el script y la política de seguridad habilita solo los dominios de Clarity.

Además de las visitas, se registran estos eventos (Clarity > Filtros > Eventos personalizados):

- Contacto: `agendar_reunion`, `whatsapp`, `email`, `telefono`, `formulario_enviado` (con la etiqueta `interes`) y `autoevaluacion_completada` (con la etiqueta `autoevaluacion_nivel`).
- Interés: `ver_diagnostico`, `ver_autoevaluacion`, `ver_ia`, `ver_servicios`, `ver_casos` y `ver_industria`.

Para saber qué botón convierte, cada acción de contacto y las dos de interés principales se registran también con el lugar de la página desde donde se hizo el clic, como `agendar_reunion:inicio-portada` o `whatsapp:boton-flotante`. Los lugares son `encabezado`, `inicio-portada`, `inicio-pasos`, `inicio-asistente`, `inicio-industrias`, `planes`, `cierre`, `pie`, `encabezado-pagina` (las páginas interiores), `contacto-otros-medios`, `boton-flotante` y `contenido` (cualquier otro). La etiqueta `origen_<evento>` guarda el último lugar de cada acción en la sesión, y `idioma` permite comparar las visitas en español e inglés. Para comparar botones, en Clarity filtrá por evento y mirá la página (URL) y la etiqueta de origen.

## Contenido a revisar

- **Valores del tablero del inicio**: son ilustrativos (el gráfico lo aclara como "Ejemplo de tablero").
- **Ejemplos de tableros**: todos los datos son ficticios y están en `dashboards.py`. Para cambiar un valor, editalo ahí y volvé a ejecutar `build.py`.
- **Formas de trabajo y tecnologías**: son una propuesta basada en los servicios actuales.
