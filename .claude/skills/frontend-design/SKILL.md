---
name: frontend-design
description: Convenciones de frontend del sitio de DeepDatas y lista de control para revisar diseño. Usala antes de tocar HTML, CSS, JS o cualquier cosa visual de sitio-web/, y también cuando te pidan revisar el diseño de una página o sección.
---

# Frontend del sitio de DeepDatas

Sitio estático: plantillas Jinja2 en `sitio-web/src/` que `build.py` convierte en
`sitio-web/public/`. **`public/` está versionado y es lo que se publica**, así que todo
cambio visual termina con `python3 build.py` y el resultado commiteado junto al fuente.
Si editás solo el fuente, el sitio no cambia.

## Lo que más seguido sale mal

### 1. La política de seguridad no permite estilos en línea

Nada de `style="..."` ni de `<style>`. La CSP del sitio (`src/staticwebapp.config.json`)
los bloquea, y el error aparece recién en producción si no lo probás con la CSP puesta.

- **Valores calculados** (anchos de barras, posiciones): usá el ayudante `pos()` de
  `build.py`, que convierte cada valor en una clase (`pos('w', 42.5)` → `w-42-5`) y la
  escribe en `assets/css/charts.css`. Nunca lo escribas a mano.
- **Desde JavaScript sí se puede**: `el.style.setProperty('--x', …)`. El CSSOM no lo
  bloquea `style-src`. Es el mecanismo que usan las escenas animadas.
- **Recurso externo nuevo** (script, iframe, fuente): además de agregarlo, hay que
  sumar su dominio a la CSP. El patrón está en `build.py`: un diccionario por servicio
  (`CLARITY_CSP`, `TURNSTILE_CSP`) que `swa_config()` inyecta solo si ese servicio está
  activo. Seguilo en vez de editar el JSON a mano.

### 2. Todo texto va en los dos idiomas

Español e inglés, siempre. Nunca escribas texto visible directo en una plantilla.

| Dónde vive | Qué contiene |
| --- | --- |
| `i18n.py` | Menú, pie, formularios, planes, logos, tableros |
| `src/hero.html` | La escena de la portada del inicio |
| `dashboards.py` | Los tableros de ejemplo |
| `casos.py`, `industrias.py`, `testimonios.py` | Casos, industrias, testimonios |

El inglés suele ser más corto y el español más largo: lo que entra justo en un idioma
puede desbordar en el otro. Probá los dos.

### 3. El encabezado flota sobre las escenas pegajosas

`--header-h` (64 px) está en `site.css`. Las etapas pegajosas (`.core-sticky`,
`.hb-pin`) arrancan en `top: 0`, así que **la primera franja de la escena queda tapada**.
Cualquier cosa que tenga que leerse —un rótulo, un número— debe calcular su posición a
partir de `--header-h`, no de un número fijo, para que aguante cualquier alto de ventana.

### 4. Recortes angostos: container queries, no media queries

La portada se parte al medio en escritorio, así que su recorte es angosto **tanto en
celular como en escritorio**. Lo que va encima de una foto se mide con
`@container` sobre el recorte, no con `@media` sobre la ventana: así crece en proporción
a lo que lo contiene. Para el cuerpo de texto, `max(14px, 3.2cqw)`: el porcentaje manda
en pantallas grandes y el piso en píxeles salva al celular.

### 5. Tres estados, no uno

Cada cosa que se anima tiene que funcionar en tres situaciones:

1. **Con animación** — el recorrido completo.
2. **Sin animación** (`prefers-reduced-motion`) — el estado final, quieto, sin saltos.
3. **Sin JavaScript** — el estado final ya escrito en el HTML. Los formularios se envían
   de forma tradicional y redirigen a `/gracias/` o `/en/thank-you/`.

## Cómo trabajar un cambio visual

**Medí antes de tocar.** Cuando algo "se ve mal", averiguá el número exacto antes de
proponer una corrección: dónde cae el elemento, cuánto mide, con qué se superpone, en
qué tamaños pasa. La mitad de las veces el problema es más grande o más chico de lo que
parecía, y la corrección correcta depende de eso.

**Verificá con la CSP de producción.** Servir `public/` con un servidor estático no
alcanza: hay que aplicar la CSP real para que aparezcan los bloqueos. El patrón:

```js
const CSP = JSON.parse(fs.readFileSync('public/staticwebapp.config.json', 'utf8'))
  .globalHeaders['Content-Security-Policy'];
await ctx.route('**/*', async route => {
  const res = await route.fetch();
  route.fulfill({ response: res, headers: { ...res.headers(), 'content-security-policy': CSP } });
});
```

Chromium y Playwright ya están instalados: `require('playwright')` y
`chromium.launch()` andan sin opciones.

**Recorré la matriz**: los dos idiomas × escritorio y celular × con y sin animación.
Un cambio que anda en español y escritorio falla seguido en inglés o en 390 px.

**Mirá las capturas, no solo las aserciones.** Las aserciones confirman lo que se te
ocurrió controlar; la foto muestra lo que no. Varios errores de esta base aparecieron
mirando una captura, no en un control automático.

**Dejá el control escrito** cuando valga la pena repetirlo, y que falle con un mensaje
que diga qué está mal y en qué tamaño.

## Lista de control para revisar diseño

Ordená los hallazgos por gravedad y decí en qué tamaño y en qué idioma pasa cada uno.

**Se rompe**
- [ ] Texto cortado, desbordado o pisado por otro elemento.
- [ ] Algo que tiene que leerse tapado por el encabezado flotante.
- [ ] Scroll horizontal (`documentElement.scrollWidth > innerWidth`).
- [ ] Errores en la consola, sobre todo bloqueos de la CSP.
- [ ] Se rompe en inglés por el largo distinto del texto.
- [ ] Sin animación o sin JavaScript queda inutilizable.

**Accesibilidad**
- [ ] Contraste: 4,5:1 para texto normal, 3:1 para texto grande. Ojo con el texto chico
      de las escenas ilustrativas (el tablero de la portada, el chat, los tableros de
      ejemplo): es decorativo pero se lee igual, y es donde se escapan los grises claros.
      Para naranja sobre fondo claro va `--accent-700`, no `--accent-600`: el de marca da
      3,68:1 y no alcanza para texto.
- [ ] Objetivos táctiles de 44 × 44 px como mínimo, y nunca menos de 24 × 24 (WCAG 2.5.8).
      Donde el cuerpo es chico a propósito —cambio de idioma, enlaces del pie, créditos—
      se agranda la zona para tocar con relleno y se devuelve con margen negativo, así la
      maqueta no cambia de alto.
- [ ] Se puede recorrer con teclado y el foco se ve.
- [ ] Las imágenes decorativas llevan `aria-hidden`; las informativas, texto alternativo.
- [ ] Los estados no se comunican solo con color.

**Oficio**
- [ ] Jerarquía: lo más importante se ve primero.
- [ ] Espaciado consistente con el resto del sitio.
- [ ] Los estados existen: vacío, cargando, error, y el foco.
- [ ] Los números y las unidades están en formato local (`1,28 M`, no `1.28M`).
- [ ] Nada de texto de relleno ni datos inventados sin aclarar que son ficticios.
