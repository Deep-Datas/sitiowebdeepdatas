# Sitio web de DeepDatas

Sitio institucional renovado de [deepdatas.com](https://deepdatas.com): un sitio estático de varias páginas, pensado para publicarse en **Azure Static Web Apps**. Incluye una pequeña API (Azure Functions, Python) para el formulario de contacto.

## Páginas

| Ruta | Contenido |
| --- | --- |
| `/` | Propuesta de valor (datos e IA para distribuidoras, pymes y consumo masivo), clientes, industrias, desafíos que resolvemos, recorrido de los datos hasta un agente de IA, casos, testimonios, formas de empezar |
| `/industrias/…` | Una página por industria (consumo masivo, distribuidoras mayoristas, pymes, retail, materiales eléctricos y construcción, autopartes y repuestos, industria y manufactura, agro, laboratorios y salud): desafíos, soluciones, indicadores, tablero de ejemplo, casos, testimonios, preguntas frecuentes y notas del blog |
| `/inteligencia-artificial/` | IA para empresas: casos de uso, conversación de ejemplo con un agente, gráfico de datos para IA, principios de seguridad, proceso y preguntas frecuentes |
| `/blog/` | Artículos (uno por archivo en `blog/`), cada uno en `/blog/<archivo>/` |
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
blog.py                  Lee los artículos de blog/ (Markdown)
blog/                    Artículos del blog, uno por archivo .md
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
src/pipeline.html        Gráfico interactivo de orígenes de datos, curado y agente de IA
src/pages/               Contenido de cada página (en src/pages/en/, la versión en inglés)
src/hero.json            Escena del inicio de cada tema (imagen y esquinas de la pantalla del monitor)
src/icons/               Íconos SVG (Bootstrap Icons, licencia MIT)
src/assets/              CSS, JavaScript, tipografías e imágenes
tools/                   Generadores de imágenes: íconos de vidrio, escena del inicio (hero_foto.py) y captura de la pantalla
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

## Versión en inglés

El sitio se publica en español (raíz) y en inglés (`/en/`). El blog es solo en español.

- Cada página en inglés tiene su plantilla en `src/pages/en/`, con el mismo nombre de archivo que la española. Sus títulos y descripciones están en `PAGES_EN` (`build.py`) y sus rutas en `ROUTES` (`i18n.py`).
- Los textos de los componentes que comparten todas las páginas (menú, pie, formularios, planes, logos, tableros y gráfico de datos) están en `i18n.py`; los de la escena del inicio, en `src/hero.html`; los de los tableros de ejemplo, en `dashboards.py`; los de los casos, en `CASES_EN` (`casos.py`); los de las industrias, en `industrias.py`, y las traducciones de los testimonios, en `testimonios.py`.
- En las plantillas, los enlaces internos se escriben con `{{ url('servicios') }}` para que apunten a la página del mismo idioma.
- Cada página enlaza su versión en el otro idioma desde el encabezado y el pie, y declara las dos versiones con `hreflang` (también en `sitemap.xml`).
- Al cambiar un texto en español, actualizá también la versión en inglés.

## Agenda online

Los botones «Coordinar llamada» abren en otra pestaña la página de reservas de Microsoft Bookings (`BOOKING_URL` en `build.py`). Para cambiarla (por ejemplo, por Calendly), reemplazá el enlace y regenerá el sitio; si lo dejás vacío, los botones vuelven a llevar al formulario de contacto. La política de privacidad menciona Microsoft Bookings mientras haya un enlace configurado. Contacto también ofrece la agenda antes del formulario, y Clarity registra cada clic como `agendar_reunion`.

## Publicación en Azure Static Web Apps

El pipeline `azure-static-web-apps-lemon-water-04480390f.yml` es el mismo que usa hoy el sitio en producción, con dos cambios:

- `app_location: "public"`: publica el sitio generado.
- `api_location: "api"`: publica la función del formulario de contacto.

Para reemplazar el sitio actual, copiá el contenido de esta carpeta a la raíz del repositorio de Azure DevOps y hacé push a `main`. Las ramas `dev` y `release` generan entornos de prueba.

## Formulario de contacto

La función `api/contacto` valida la consulta, descarta spam con un campo trampa y envía el correo con **Microsoft Graph** desde el buzón de Microsoft 365 (Office 365 ya no acepta el envío por SMTP con usuario y contraseña). Configuración única:

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

Mientras no esté configurado, el formulario muestra un aviso con el email de contacto en lugar de fallar en silencio.

Los formularios envían el idioma de la página (`lang`): la función responde en ese idioma, sin JavaScript redirige a `/gracias/` o `/en/thank-you/`, y los correos que llegan desde la versión en inglés tienen el asunto con `[EN]`. Las consultas de la autoevaluación llegan con el interés «Autoevaluación de datos» (o «AI readiness check») y el resultado con todas las respuestas en el mensaje.

## Blog

Para publicar un artículo, creá un archivo `.md` en `blog/` (por ejemplo `blog/mi-articulo.md`, que se publica en `/blog/mi-articulo/`) con este encabezado y el texto en Markdown debajo:

```
---
title: Título del artículo
description: Resumen de unas 25 palabras para Google y LinkedIn
date: 2026-10-20
tags: Power BI, Tableros de gestión
cta: diagnostico
---
```

`cta` define el llamado a la acción del final: `diagnostico`, `casos` o `ia`. Los artículos con fecha futura no se publican hasta que se vuelva a generar el sitio en esa fecha. Cada artículo se suma solo al blog, al inicio, al sitemap y a los artículos relacionados.

## Casos de éxito

Los casos están en `casos.py`. Cada uno tiene `'publicado': False` hasta que se completen sus datos reales:

1. Reemplazá cada `[completar]` por el dato real (resultados, duración) y, si el cliente lo autoriza, agregá su logo. El testimonio del cliente va en `testimonios.py` (ver «Testimonios»).
2. Revisalo con `python build.py --borradores` y abrí la carpeta `vista-previa/` (no se sube al repositorio).
3. Cambiá `'publicado'` a `True` y ejecutá `python build.py`.

Con al menos un caso publicado aparecen la página `/casos/`, el ítem «Casos» del menú y la sección de casos del inicio. `build.py` no deja publicar un caso que todavía tenga datos `[completar]`.

## Testimonios

Los testimonios están en `testimonios.py` y la guía para pedirlos a los clientes (mensaje, preguntas, autorización y consejos para grabar un video de 30 segundos) en `contenido/testimonios.md`. Tienen que ser reales: el texto lo escribe o lo aprueba el cliente.

1. Completá el borrador (texto, nombre, cargo y empresa; foto y video opcionales) y en `consent` anotá cómo y cuándo autorizó la publicación.
2. Revisalo con `python build.py --borradores`.
3. Cambiá `'publicado'` a `True` y ejecutá `python build.py`.

Cada testimonio publicado aparece en la sección «Lo que dicen nuestros clientes» del inicio, dentro de su caso de éxito (`case`) y en la página de su industria (`industry`). `build.py` no deja publicar un testimonio con datos `[completar]` o sin autorización.

## Industrias

Las páginas de `/industrias/` (consumo masivo, distribuidoras mayoristas, pymes, retail, materiales eléctricos y construcción, autopartes y repuestos, industria y manufactura, agro, y laboratorios y salud; en inglés, en `/en/industries/…`) se generan con la plantilla `src/pages/industria.html` a partir de `industrias.py`: desafíos, soluciones, indicadores, preguntas frecuentes, y qué casos, tablero de ejemplo, logos y notas del blog mostrar. Las rutas están en `i18n.py` (`ind-<id>`). Para sumar una industria, agregala en `industrias.py` (textos en los dos idiomas, datos comunes y `ORDER`) y su ruta en `i18n.py`; aparece sola en el inicio, en el pie y en el sitemap. Solo se muestran los casos publicados; no sumes resultados que no estén en un caso real.

## Analítica de visitas

El sitio está preparado para [Microsoft Clarity](https://clarity.microsoft.com) (gratuito): visitas, origen del tráfico, mapas de calor y grabaciones de sesión. Mientras `CLARITY_ID` esté vacío en `build.py`, no se carga nada externo.

1. Creá un proyecto en Clarity para `deepdatas.com` y copiá su identificador (Settings > Overview > Project ID).
2. Recomendado: en Settings > Setup, desactivá las cookies y dejá el enmascarado de datos en modo estricto.
3. Pegá el identificador en `CLARITY_ID` y ejecutá `python build.py`: se agrega el script y la política de seguridad habilita solo los dominios de Clarity.

Además de las visitas, se registran estos eventos (Clarity > Filtros > Eventos personalizados): `whatsapp`, `email`, `telefono`, `agendar_reunion`, `ver_diagnostico`, `ver_autoevaluacion` y `formulario_enviado` (con la etiqueta `interes`). La etiqueta `idioma` permite comparar las visitas en español e inglés.

## Contenido a revisar

- **Valores del tablero del inicio**: son ilustrativos (el gráfico lo aclara como "Ejemplo de tablero").
- **Ejemplos de tableros**: todos los datos son ficticios y están en `dashboards.py`. Para cambiar un valor, editalo ahí y volvé a ejecutar `build.py`.
- **Formas de trabajo y tecnologías**: son una propuesta basada en los servicios actuales.
