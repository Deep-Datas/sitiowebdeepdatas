# Sitio web de DeepDatas

Sitio institucional renovado de [deepdatas.com](https://deepdatas.com): un sitio estático de varias páginas, pensado para publicarse en **Azure Static Web Apps**. Incluye una pequeña API (Azure Functions, Python) para el formulario de contacto.

## Páginas

| Ruta | Contenido |
| --- | --- |
| `/` | Propuesta de valor (datos e IA para distribuidoras, pymes y consumo masivo), clientes, industrias, desafíos que resolvemos, recorrido de los datos hasta un agente de IA, casos, testimonios, formas de empezar |
| `/industrias/…` | Una página por industria (consumo masivo, distribuidoras mayoristas, pymes, retail, materiales eléctricos y construcción, autopartes y repuestos, industria y manufactura y agro): desafíos, soluciones, indicadores, tablero de ejemplo, casos, testimonios, preguntas frecuentes y notas del blog |
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
src/pipeline.html        Gráfico interactivo de orígenes de datos, curado y agente de IA (Servicios e IA)
src/flow.html            Inicio: una pregunta recorre los sistemas, el curado y el agente de IA (textos en los dos idiomas)
src/pages/               Contenido de cada página (en src/pages/en/, la versión en inglés)
src/hero.html            Portada del inicio: la cámara que se acerca al televisor con el scroll, del informe a mano a la respuesta en el momento (textos en los dos idiomas)
src/icons/               Íconos SVG (Bootstrap Icons, licencia MIT)
src/assets/              CSS, JavaScript, tipografías e imágenes
tools/                   Generadores de imágenes y video: íconos de vidrio, la imagen del cierre de cada página (nucleo.cjs), las dos fotos de la portada —revelado y agrandado— (portada_foto.py, a partir de tools/hero/portada-original.webp y tools/hero/portada-tv-original.webp), la foto retocada de otra oficina (hero_foto.py, hoy sin uso) y el video del asistente de la página de IA (video/)
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

## Diseño 2026: «luz sobre los datos»

Las secciones claras (marfil) cuentan la historia del negocio y las «profundas» (azul noche, `section-deep`) muestran dónde viven los datos, con el naranja de la marca y una luz azul como fuentes de luz. Los estilos del rediseño están en `src/assets/css/design.css` (se carga después de `site.css`) y sus interacciones en `src/assets/js/design.js`:

- **Núcleo de datos** (`[data-core]`, inicio, sección clara): una constelación de registros dibujada en vivo en un `canvas` (`design.js`, sin librerías ni imágenes). Cada punto lleva el color del sistema donde vive hoy (ERP, CRM, planillas, WhatsApp, correo); con el scroll los puntos viajan desde cinco nubes hasta una esfera ordenada que se enciende desde el centro, como en apple.com. Mientras están dispersos, el cursor los aparta; una vez ordenados, la esfera lo sigue. Sin animación se dibuja una sola vez el estado final. Los nombres de los sistemas que se ven sobre las nubes salen de `data-labels` (uno por idioma). `poster.webp` (`src/assets/img/core/`, generado con `tools/nucleo.cjs`) ya solo se usa en el cierre de cada página.
- **Pregunta y respuesta** (`src/flow.html`, `[data-flow]`, inicio, debajo del núcleo): una pregunta recorre los cinco sistemas, el curado los convierte en un solo modelo y el agente de IA escribe la respuesta con sus fuentes. Es HTML con líneas SVG (`design.js`): el recorrido se reproduce al entrar en pantalla, cada pregunta de ejemplo lo vuelve a reproducir con su respuesta y, al pasar el cursor por un sistema, se ilumina su camino. Los textos de los dos idiomas están en el mismo archivo (datos ficticios). Sin animación o sin JavaScript se ve el estado final con la primera respuesta. El gráfico detallado del recorrido (`src/pipeline.html`) sigue en Servicios y en la página de IA.
- **Portada del inicio: una cámara que se acerca al televisor** (`src/hero.html`, estilos `.hb*` en `design.css`, movimiento en `design.js`): «Una pregunta. Todos tus sistemas. Una sola respuesta.» Son dos fotos del mismo lugar, encadenadas: la oficina de quien decide (`portada-oficina-{1264,2528}.webp`, medida sobre 1264 × 843 —de esa foto se usa solo la mitad del televisor, no el sector del equipo— ) y, al final del recorrido, el primer plano del televisor de espaldas (`portada-tv-{1024,2048}.webp`, medida sobre 1024 × 559). Las fotos no se mueven: se mueve el recorte. Mientras dura el riel (`.hb-track`, 320 vh) la escena queda fija y a pantalla completa (`.hb-pin`, pegajosa, de borde a borde y del alto de la pantalla menos el encabezado) y el scroll mueve la cámara de derecha a izquierda, en cuatro actos, hasta que en el último la escena gira (`.hb-turn`, `perspective` + `rotateY`) y las dos fotos se cruzan: la oficina sale girando y entra el primer plano, ya casi de frente. De 901 px para arriba la portada se parte al medio: **el texto a la izquierda**, sobre el fondo de la página y alineado con el logo del encabezado, y **la escena a la derecha**, del alto de la pantalla. Ahí el texto se queda quieto todo el recorrido. En celulares no hay mitades: el texto va encima de la escena con un velo (`.hb-veil`, un degradado del color de fondo) y los dos se desvanecen apenas empieza el recorrido. Quién de los dos manda lo decide el CSS con `--fade`; `design.js` solo pasa cuánto se fue. Como el recorte pasa a ser angosto en las dos formas, lo que va encima de la foto se mide con container queries sobre `.hb-crop`, no con media queries: así crece en proporción al recorte y no a la ventana. La cámara no salta al valor del scroll: lo persigue con un retardo chico, que es lo que hace que el movimiento se sienta de cámara y de paso se come los saltos de la rueda del mouse. Sobre el televisor de cada foto va contenido de verdad, escrito en HTML y encajado con una matriz de perspectiva; los dos tableros nunca se ven juntos (el de la primera foto se apaga antes del giro y el de la segunda se enciende después), porque los televisores se ven de ángulos distintos y superpuestos quedarían como una doble imagen.
  **Acto 1**: el pedido que acaba de entrar, con dos o tres días de entrega. **Acto 2**: los sistemas donde hoy vive esa información —WhatsApp y el CRM, en dos tarjetas sobre la escena— y la planilla que se arma pegando filas. **Acto 3**: los sistemas viajan y se unen en un solo modelo. **Acto 4**: la cámara gira hacia el televisor y se le queda encima, con los mismos números ya ordenados, mientras quien decide pregunta en voz alta.
  Sin animación o sin JavaScript no hay riel: se ve el acto final, quieto, con los valores finales en el HTML (el encuadre de ese acto está escrito a mano en `design.css`). **Si se cambian las fotos hay que volver a medir las cuatro esquinas de cada televisor y los encuadres** (`FOTO` y `CERCA`, al inicio del archivo); los encuadres dicen qué tiene que entrar sí o sí en cada acto y `design.js` los adapta a la forma del recorte, y `desde`/`hasta` de `CERCA` dicen en qué tramo del scroll se cruzan las dos fotos. Los textos de los dos idiomas están en el mismo archivo (datos ficticios).
  Las dos fotos las aportó el cliente. `tools/portada_foto.py` las revela y las agranda a partir de `tools/hero/portada-original.webp` y `tools/hero/portada-tv-original.webp`: las aclara (gamma sobre los medios tonos, el velo cálido neutralizado por canal y un poco menos de saturación: la oficina pasa de una tarde a una mañana blanca, sin quemar las ventanas) y las lleva al doble de ancho con **retroproyección** —agrandar, achicar, comparar con el original y devolver la diferencia, doce veces—, que no inventa detalle pero recupera el que el agrandado se come: el error de ida y vuelta baja de 1,57 a 0,06 contra el Lanczos de antes, y los bordes quedan sin los halos que deja un enfoque fuerte. Aun así los originales son chicos y la cámara se acerca, así que arriba van una viñeta (`.hb-grade`) y un grano finito (`.hb-grain`, `grano.png`, una baldosa de 128 px) que les devuelven textura. Conviene reemplazarlas por los originales en mayor resolución: se dejan con esos mismos nombres en `tools/hero/` y se vuelve a correr el script. **Falta anotar acá su licencia de uso comercial**, como está anotada la de las fotos de Unsplash más abajo.
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

Cada testimonio publicado aparece en la sección «Lo que dicen nuestros clientes» del inicio, dentro de su caso de éxito (`case`) y en la página de su industria (`industry`). `build.py` no deja publicar un testimonio con datos `[completar]` o sin autorización.

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
