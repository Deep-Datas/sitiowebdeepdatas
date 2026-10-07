# Cómo conseguir testimonios de clientes

Un testimonio con nombre, cargo y empresa es una de las pruebas que más confianza genera en un sitio. Pero tiene que ser **real**: el texto lo escribe o lo aprueba el cliente y se publica solo con su autorización por escrito. Nunca se redacta ni se "mejora" un testimonio en su nombre sin que lo apruebe.

El sitio ya está preparado: cuando cargues un testimonio en `testimonios.py` aparece en el inicio, dentro de su caso de éxito y en la página de su industria (en español y en inglés).

---

## 1. A quién pedírselo y cuándo

- A la persona que **usa** la solución todos los días o la impulsó: gerente comercial, de planeamiento, de compras, de sistemas o la dirección.
- En el mejor momento: cuando el cliente acaba de ver un resultado (un cierre de mes más rápido, menos quiebres, un tablero que usa toda la empresa). Si te agradece por email o en una reunión, es la oportunidad.
- Empezá por los casos ya publicados: **Red de distribuidores** (consumo masivo) y **Pronóstico de demanda** (distribución). Ya tienen un testimonio en borrador esperando el texto.
- Con uno o dos testimonios buenos alcanza para empezar. Es mejor uno real que tres genéricos.

## 2. Mensaje para pedirlo

Por email o WhatsApp, adaptado a cada persona:

> Hola, [nombre]. ¿Cómo estás?
>
> Estamos renovando el sitio de DeepDatas y nos gustaría contar el proyecto de [nombre del proyecto] con la voz de quienes lo usan. ¿Te animarías a dejarnos un breve comentario sobre cómo fue trabajar juntos y qué cambió en tu equipo?
>
> Son dos o tres oraciones. Si te resulta más cómodo, te paso unas preguntas, lo conversamos 10 minutos y te mando el texto armado con tus palabras para que lo corrijas y lo apruebes.
>
> Lo publicaríamos con tu nombre, tu cargo y [el nombre de la empresa / una descripción como "empresa de consumo masivo"], y solo con tu aprobación. Si además querés grabar un video corto (30 segundos, con el celular), sería genial, pero es opcional.
>
> ¡Gracias!

Si la empresa no permite usar su nombre, se publica con una descripción ("Distribuidora mayorista") y el nombre y cargo de la persona, si ella lo autoriza.

## 3. Preguntas para guiar el testimonio

Un buen testimonio cuenta un antes, un después y un resultado concreto. Elegí dos o tres:

1. ¿Qué problema tenían antes de empezar el proyecto?
2. ¿Qué cambió en el día a día de tu equipo?
3. ¿Hay algún número o ejemplo concreto que lo muestre? (horas ahorradas, días de cierre, quiebres, ventas)
4. ¿Cómo fue trabajar con DeepDatas?
5. ¿Se lo recomendarías a otra empresa? ¿Por qué?

Ejemplo de **estructura** (no es un texto para usar, el contenido tiene que salir del cliente):
"Antes, [problema]. Ahora, [cambio en el día a día]. [Resultado concreto]."

Si el cliente menciona un número, tiene que coincidir con el del caso de éxito. Si no lo puede compartir, se publica sin el número.

## 4. Autorización

Antes de publicar, pedí la aprobación por escrito (un email alcanza) con un texto como este:

> Autorizo a DeepDatas a publicar en su sitio web y en sus redes sociales el siguiente testimonio, junto con mi nombre, mi cargo, [el nombre de mi empresa / la descripción "…"] [y mi foto / y el video que grabé]:
>
> «[texto final del testimonio]»
>
> Puedo pedir que lo retiren en cualquier momento escribiendo a fbloise@deepdatas.com.

Guardá ese email. En `testimonios.py`, el campo `consent` registra cómo y cuándo se autorizó (por ejemplo, `'Email del 12/11/2026'`): **sin ese dato el sitio no se genera**, para evitar publicar algo sin autorización. Si el cliente pide retirarlo, poné `'publicado': False` y volvé a publicar el sitio.

Para la versión en inglés podés traducir el testimonio (se muestra con la aclaración "Translated from Spanish"). Conviene que el cliente también apruebe la traducción. Si no hay traducción, en inglés se muestra el texto original en español.

## 5. Video de 30 segundos (opcional)

El video es lo que más confianza genera, pero no es obligatorio. Para que se vea profesional sin un equipo de filmación:

- **Duración:** 20 a 40 segundos. Una idea: el antes, el después y una recomendación.
- **Celular en horizontal**, a la altura de los ojos, apoyado o en un trípode. Nada de selfie con el brazo estirado.
- **Luz de frente** (una ventana delante de la persona, nunca detrás).
- **Lugar silencioso.** Si es posible, un micrófono corbatero de celular o auriculares con micrófono mejoran mucho el audio.
- **Fondo prolijo**, idealmente la oficina del cliente.
- Que hable **con sus palabras**, sin leer. Dos o tres tomas y se elige la mejor.
- También sirve una videollamada grabada (Teams o Zoom), recortada a los mejores 30 segundos.

Para subirlo al sitio:

- Exportalo en **MP4 (H.264), 1280 × 720, menos de 8 MB** (con HandBrake, gratuito, o el editor del celular).
- Guardalo en `src/assets/video/testimonios/` (por ejemplo `nombre-apellido.mp4`).
- Sacá una **imagen de portada** (un cuadro del video donde se vea bien a la persona, JPG de 1280 × 720) y guardala en `src/assets/img/testimonios/`.
- Agregá **subtítulos** (`.vtt`, en la misma carpeta del video): mucha gente mira los videos sin sonido y además el sitio sigue siendo accesible. Se pueden generar automáticamente con la transcripción de Teams, YouTube o CapCut y corregir a mano.
- Si el video ya está publicado en LinkedIn o YouTube, podés poner ese enlace en lugar del archivo: el sitio muestra un botón "Ver el video".

## 6. Foto

Opcional: una foto de la persona, cuadrada, de al menos 240 × 240 px, con el rostro bien iluminado (la foto de LinkedIn suele servir, con su permiso). Guardala en `src/assets/img/testimonios/nombre-apellido.jpg`.

## 7. Cargarlo en el sitio

En `testimonios.py`, completá el borrador del caso (o agregá uno nuevo):

```python
{
    'id': 'distribuidores',
    'publicado': True,
    'case': 'distribuidores',          # caso de éxito relacionado
    'industry': 'consumo',             # id de la industria en industrias.py (consumo, distribucion, pymes, retail, ...)
    'quote': 'Texto aprobado por el cliente.',
    'name': 'Nombre Apellido',
    'role': 'Gerente comercial',
    'company': 'Empresa de consumo masivo',
    'photo': 'testimonios/nombre-apellido.jpg',        # o None
    'video': 'testimonios/nombre-apellido.mp4',        # o un enlace https://..., o None
    'poster': 'testimonios/nombre-apellido-portada.jpg',  # portada del video, o None
    'captions': 'testimonios/nombre-apellido.vtt',     # subtítulos, o None
    'consent': 'Email del 12/11/2026',
    'en': {'quote': 'Approved translation.', 'role': 'Head of Sales', 'company': 'Consumer goods company'},
},
```

Después revisalo con `python build.py --borradores` (vista previa en `vista-previa/`) y, si está todo bien, publicá con el procedimiento habitual.
