"""Formulario de contacto de deepdatas.com.

Recibe el POST de /api/contacto (Azure Static Web Apps lo publica en esa
ruta) y envía la consulta por correo usando Microsoft Graph con la cuenta
de Microsoft 365 de la empresa.

Variables de entorno (Static Web App > Configuración / Environment variables):
  GRAPH_TENANT_ID      Id. del directorio (tenant) de Microsoft Entra ID
  GRAPH_CLIENT_ID      Id. de la aplicación registrada
  GRAPH_CLIENT_SECRET  Secreto de cliente de esa aplicación
  MAIL_SENDER          Buzón que envía los mensajes (default: fbloise@deepdatas.com)
  CONTACT_RECIPIENTS   Destinatarios separados por coma (default: MAIL_SENDER)
"""
import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

import azure.functions as func


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
FIELDS = {
    # campo: (obligatorio, largo máximo)
    'name': (True, 120),
    'email': (True, 254),
    'company': (False, 120),
    'phone': (False, 40),
    'interest': (False, 80),
    'message': (True, 5000),
}
# Mensajes al visitante, según el idioma de la página («lang» en el formulario)
MESSAGES = {
    'es': {
        'required': 'Completá los campos obligatorios.',
        'too_long': 'Uno de los campos es demasiado largo.',
        'email': 'Ingresá un email válido.',
        'rate': 'Recibimos varios mensajes seguidos. Probá de nuevo en unos minutos o escribinos a fbloise@deepdatas.com.',
        'fallback': 'No pudimos enviar tu mensaje en este momento. Escribinos a fbloise@deepdatas.com.',
        'thanks': '/gracias/',
    },
    'en': {
        'required': 'Please fill in the required fields.',
        'too_long': 'One of the fields is too long.',
        'email': 'Please enter a valid email address.',
        'rate': 'We received several messages in a row. Please try again in a few minutes or email us at fbloise@deepdatas.com.',
        'fallback': 'We couldn’t send your message right now. Please email us at fbloise@deepdatas.com.',
        'thanks': '/en/thank-you/',
    },
}
TIMEOUT = 10
MAX_BODY = 20_000  # bytes; los campos suman menos de 6.000 caracteres
# Límite de envíos por IP. Vive en la memoria de cada instancia de la función:
# frena ráfagas de un mismo origen, no reemplaza un firewall.
RATE_LIMIT = 5
RATE_WINDOW = 600  # segundos
_recent = {}


def main(req: func.HttpRequest) -> func.HttpResponse:
    wants_json = req.headers.get('X-Requested-With') == 'XMLHttpRequest'
    body = req.get_body()
    form = parse_form(body[:MAX_BODY])
    lang = 'en' if form.get('lang') == 'en' else 'es'
    text = MESSAGES[lang]

    # Campo trampa: los humanos no lo ven, los bots suelen completarlo.
    if form.get('website'):
        return respond(wants_json, True, lang=lang)

    if len(body) > MAX_BODY:
        return respond(wants_json, False, text['too_long'], 413, lang)

    data = {field: form.get(field, '').strip() for field in FIELDS}
    error = validate(data)
    if error:
        return respond(wants_json, False, text[error], 400, lang)

    if too_many(client_ip(req)):
        logging.warning('Formulario de contacto: límite de envíos alcanzado.')
        return respond(wants_json, False, text['rate'], 429, lang)

    config = {key: os.environ.get(key, '').strip() for key in ('GRAPH_TENANT_ID', 'GRAPH_CLIENT_ID', 'GRAPH_CLIENT_SECRET')}
    if not all(config.values()):
        logging.error('Formulario de contacto: faltan las variables GRAPH_TENANT_ID/GRAPH_CLIENT_ID/GRAPH_CLIENT_SECRET.')
        return respond(wants_json, False, text['fallback'], 503, lang)

    try:
        send_mail(data, lang, **config)
    except Exception:
        # El detalle (paso, estado HTTP y respuesta de Microsoft) queda en los registros de Azure.
        logging.exception('Formulario de contacto: error al enviar el correo.')
        return respond(wants_json, False, text['fallback'], 502, lang)

    return respond(wants_json, True, lang=lang)


def parse_form(body):
    parsed = urllib.parse.parse_qs(body.decode('utf-8', errors='replace'), keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


def client_ip(req):
    # Azure agrega la IP del visitante en X-Forwarded-For, a veces con el puerto.
    forwarded = req.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    if forwarded.count(':') == 1:
        forwarded = forwarded.split(':')[0]
    return forwarded or 'desconocida'


def too_many(ip, now=None):
    """Registra el envío y devuelve True si la IP superó RATE_LIMIT en RATE_WINDOW."""
    now = time.monotonic() if now is None else now
    for key in [k for k, times in _recent.items() if times[-1] < now - RATE_WINDOW]:
        del _recent[key]
    times = [t for t in _recent.get(ip, []) if t >= now - RATE_WINDOW]
    if len(times) >= RATE_LIMIT:
        _recent[ip] = times
        return True
    _recent[ip] = times + [now]
    return False


def validate(data):
    """Devuelve la clave del mensaje de error (ver MESSAGES) o None si los datos son válidos."""
    for field, (required, max_length) in FIELDS.items():
        if required and not data[field]:
            return 'required'
        if len(data[field]) > max_length:
            return 'too_long'
    if not EMAIL_RE.match(data['email']):
        return 'email'
    return None


def send_mail(data, lang, GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET):
    sender = os.environ.get('MAIL_SENDER', 'fbloise@deepdatas.com').strip()
    recipients = [r.strip() for r in os.environ.get('CONTACT_RECIPIENTS', sender).split(',') if r.strip()]
    topic = data['interest'] or 'Consulta general'
    subject = ' '.join(f"{topic} - {data['company'] or data['name']}".split())
    if lang == 'en':
        subject = f'[EN] {subject}'

    token = request_json(
        f'https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token',
        urllib.parse.urlencode({
            'client_id': GRAPH_CLIENT_ID,
            'client_secret': GRAPH_CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials',
        }).encode(),
        {'Content-Type': 'application/x-www-form-urlencoded'},
    )['access_token']

    message = {
        'message': {
            'subject': f'[deepdatas.com] {subject}',
            'body': {
                'contentType': 'Text',
                'content': (
                    'Nueva consulta desde el formulario de contacto del sitio web.\n\n'
                    f"Nombre: {data['name']}\n"
                    f"Email: {data['email']}\n"
                    f"Empresa: {data['company'] or '-'}\n"
                    f"Teléfono: {data['phone'] or '-'}\n"
                    f'Interés: {topic}\n'
                    f"Idioma del sitio: {'inglés' if lang == 'en' else 'español'}\n\n"
                    f"{data['message']}\n"
                ),
            },
            'toRecipients': [{'emailAddress': {'address': r}} for r in recipients],
            'replyTo': [{'emailAddress': {'address': data['email'], 'name': data['name']}}],
        },
        'saveToSentItems': False,
    }
    request_json(
        f'https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(sender)}/sendMail',
        json.dumps(message).encode(),
        {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
    )


class GraphError(Exception):
    def __init__(self, step, status, detail):
        super().__init__(f'{step} respondió {status}: {detail}')


def request_json(url, body, headers):
    request = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace')[:500]
        step = 'token' if 'login.microsoftonline.com' in url else 'envio'
        raise GraphError(step, error.code, detail) from None
    return json.loads(payload) if payload else {}


def respond(wants_json, ok, error=None, status=200, lang='es'):
    if wants_json:
        return func.HttpResponse(json.dumps({'ok': ok, 'error': error}), status_code=status, mimetype='application/json')
    # Sin JavaScript: el navegador envió el formulario de forma tradicional.
    thanks = MESSAGES[lang]['thanks']
    return func.HttpResponse(status_code=303, headers={'Location': thanks if ok else f'{thanks}#error'})
