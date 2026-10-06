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
FALLBACK_ERROR = 'No pudimos enviar tu mensaje en este momento. Escribinos a fbloise@deepdatas.com.'
TIMEOUT = 10


def main(req: func.HttpRequest) -> func.HttpResponse:
    wants_json = req.headers.get('X-Requested-With') == 'XMLHttpRequest'
    form = parse_form(req)

    # Campo trampa: los humanos no lo ven, los bots suelen completarlo.
    if form.get('website'):
        return respond(wants_json, True)

    data = {field: form.get(field, '').strip() for field in FIELDS}
    error = validate(data)
    if error:
        return respond(wants_json, False, error, 400)

    config = {key: os.environ.get(key, '').strip() for key in ('GRAPH_TENANT_ID', 'GRAPH_CLIENT_ID', 'GRAPH_CLIENT_SECRET')}
    if not all(config.values()):
        logging.error('Formulario de contacto: faltan las variables GRAPH_TENANT_ID/GRAPH_CLIENT_ID/GRAPH_CLIENT_SECRET.')
        return respond(wants_json, False, FALLBACK_ERROR, 503)

    try:
        send_mail(data, **config)
    except Exception:
        logging.exception('Formulario de contacto: error al enviar el correo.')
        return respond(wants_json, False, FALLBACK_ERROR, 502)

    return respond(wants_json, True)


def parse_form(req):
    body = req.get_body().decode('utf-8', errors='replace')
    parsed = urllib.parse.parse_qs(body, keep_blank_values=True)
    return {key: values[0] for key, values in parsed.items()}


def validate(data):
    for field, (required, max_length) in FIELDS.items():
        if required and not data[field]:
            return 'Completá los campos obligatorios.'
        if len(data[field]) > max_length:
            return 'Uno de los campos es demasiado largo.'
    if not EMAIL_RE.match(data['email']):
        return 'Ingresá un email válido.'
    return None


def send_mail(data, GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET):
    sender = os.environ.get('MAIL_SENDER', 'fbloise@deepdatas.com').strip()
    recipients = [r.strip() for r in os.environ.get('CONTACT_RECIPIENTS', sender).split(',') if r.strip()]
    topic = data['interest'] or 'Consulta general'
    subject = ' '.join(f"{topic} - {data['company'] or data['name']}".split())

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
                    f'Interés: {topic}\n\n'
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


def request_json(url, body, headers):
    request = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace')[:500]
        raise RuntimeError(f'{url} respondió {error.code}: {detail}') from None
    return json.loads(payload) if payload else {}


def respond(wants_json, ok, error=None, status=200):
    if wants_json:
        return func.HttpResponse(json.dumps({'ok': ok, 'error': error}), status_code=status, mimetype='application/json')
    # Sin JavaScript: el navegador envió el formulario de forma tradicional.
    if ok:
        return func.HttpResponse(status_code=303, headers={'Location': '/gracias/'})
    return func.HttpResponse(status_code=303, headers={'Location': '/gracias/#error'})
