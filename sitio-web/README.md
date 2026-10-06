# Sitio web de DeepDatas

Sitio institucional renovado de [deepdatas.com](https://deepdatas.com): un sitio estático de varias páginas, pensado para publicarse en **Azure Static Web Apps**. Incluye una pequeña API (Azure Functions, Python) para el formulario de contacto.

## Páginas

| Ruta | Contenido |
| --- | --- |
| `/` | Propuesta de valor, clientes, desafíos que resolvemos, recorrido de los datos hasta un agente de IA, servicios, caso destacado, proceso, industrias |
| `/diagnostico/` | Oferta de diagnóstico de datos: entregables, ejemplo de informe (datos ficticios), proceso, preguntas frecuentes y formulario |
| `/servicios/` | Detalle de los cuatro servicios, niveles de analítica, formas de trabajo y tecnología |
| `/ejemplos/` | Tres tableros interactivos de ejemplo (datos ficticios) con el desafío, la solución y el beneficio |
| `/nosotros/` | Misión, pilares, especialidades del equipo y ubicación |
| `/contacto/` | Formulario, medios de contacto, mapa y preguntas frecuentes |
| `/gracias/` | Confirmación del formulario cuando el navegador no tiene JavaScript |
| `/404.html` | Página de error |

## Estructura

```
build.py                 Genera el sitio en public/ a partir de src/
dashboards.py            Datos ficticios de los tableros de ejemplo
pipeline.py              Textos y geometría del gráfico «Del dato disperso al agente de IA»
requirements.txt         Dependencias para generar el sitio (Jinja2)
src/layout.html          Estructura común: encabezado, menú, pie y metadatos
src/forms.html           Formulario de contacto (se usa en Contacto y en Diagnóstico)
src/charts.html          Componentes de los gráficos de los tableros de ejemplo
src/pipeline.html        Gráfico interactivo de orígenes de datos, curado y agente de IA
src/pages/               Contenido de cada página
src/icons/               Íconos SVG (Bootstrap Icons, licencia MIT)
src/assets/              CSS, JavaScript, tipografías e imágenes
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

## Contenido a revisar

- **Valores del tablero del inicio**: son ilustrativos (el gráfico lo aclara como "Ejemplo de tablero").
- **Ejemplos de tableros**: todos los datos son ficticios y están en `dashboards.py`. Para cambiar un valor, editalo ahí y volvé a ejecutar `build.py`.
- **Formas de trabajo y tecnologías**: son una propuesta basada en los servicios actuales.
