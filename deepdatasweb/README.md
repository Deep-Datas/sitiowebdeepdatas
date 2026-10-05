# deepdatas.com

Sitio institucional de DeepDatas. Es un sitio estático publicado en **Azure Static Web Apps**, con una pequeña API (Azure Functions, Python) para el formulario de contacto.

## Estructura

```
index.html                  Página principal (todo el contenido del sitio)
gracias.html                Confirmación del formulario cuando el navegador no tiene JavaScript
404.html                    Página de error para direcciones inexistentes
assets/css/deepdatas.css    Estilos del sitio
assets/js/deepdatas.js      Menú móvil, animaciones, galería y envío del formulario
assets/img/                 Logos, fotos del equipo, capturas de casos de éxito
assets/vendor/              Librerías de terceros (Bootstrap, Bootstrap Icons, AOS, GLightbox)
api/contacto/               Función que recibe el formulario y envía el correo
staticwebapp.config.json    Encabezados de seguridad, página 404, redirecciones y runtime de la API
robots.txt / sitemap.xml    Indexación en buscadores
azure-static-web-apps-*.yml Pipeline de Azure DevOps que publica el sitio
```

## Editar contenido

Todo el texto está en `index.html`, dividido en secciones con comentarios (`<!-- ======= SERVICIOS ======= -->`, etc.). Para cambiar colores o tipografías, las variables están al inicio de `assets/css/deepdatas.css`.

## Ver el sitio en tu computadora

```
python -m http.server 8000
```

y abrir http://localhost:8000. El formulario de contacto necesita la API; para probarla localmente se puede usar la [CLI de Static Web Apps](https://learn.microsoft.com/azure/static-web-apps/local-development) (`swa start . --api-location api`).

## Publicación

El pipeline publica automáticamente al hacer push a `main` (producción) y crea entornos de prueba para `dev`, `release` y los pull requests.

## Formulario de contacto (configuración única)

La función `api/contacto` envía los mensajes con **Microsoft Graph** desde el buzón de Microsoft 365 (Office 365 dejó de aceptar el envío por SMTP con usuario y contraseña).

1. En el [portal de Azure](https://portal.azure.com) > **Microsoft Entra ID** > **Registros de aplicaciones** > **Nuevo registro** (por ejemplo, "deepdatas-web-contacto").
2. En **Permisos de API** > **Agregar un permiso** > **Microsoft Graph** > **Permisos de aplicación** > `Mail.Send`, y luego **Conceder consentimiento de administrador**.
3. En **Certificados y secretos** > **Nuevo secreto de cliente**. Copiar el valor (solo se muestra una vez) y anotar su vencimiento.
4. Recomendado: limitar la aplicación para que solo pueda enviar desde `contacto@deepdatas.com` ([RBAC para aplicaciones en Exchange Online](https://learn.microsoft.com/exchange/permissions-exo/application-rbac)).
5. En la Static Web App > **Configuración** > **Variables de entorno**, agregar:

| Variable | Valor |
| --- | --- |
| `GRAPH_TENANT_ID` | Id. de directorio (inquilino) del registro de la aplicación |
| `GRAPH_CLIENT_ID` | Id. de aplicación (cliente) |
| `GRAPH_CLIENT_SECRET` | Valor del secreto creado en el paso 3 |
| `MAIL_SENDER` | Opcional. Buzón que envía. Por defecto `contacto@deepdatas.com` |
| `CONTACT_RECIPIENTS` | Opcional. Destinatarios separados por coma. Por defecto, el mismo buzón |

Mientras estas variables no estén configuradas, el formulario muestra un aviso con el email de contacto en lugar de fallar en silencio.
