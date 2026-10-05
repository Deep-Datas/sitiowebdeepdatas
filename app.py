import logging
import os
import re
from datetime import date

from flask import Flask, Response, jsonify, redirect, render_template, request, url_for
from flask_mail import Mail, Message


app = Flask(__name__)
logger = logging.getLogger(__name__)


def env_flag(name, default):
	return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'si')


# Las credenciales de correo se leen de variables de entorno (Azure App Service >
# Configuración > Application settings). Nunca deben quedar escritas en el código.
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.office365.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = env_flag('MAIL_USE_TLS', True)
app.config['MAIL_USE_SSL'] = env_flag('MAIL_USE_SSL', False)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'contacto@deepdatas.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_SENDER', app.config['MAIL_USERNAME'])
app.config['CONTACT_RECIPIENTS'] = [
	r.strip() for r in os.environ.get('CONTACT_RECIPIENTS', 'contacto@deepdatas.com').split(',') if r.strip()
]
app.config['SITE_URL'] = os.environ.get('SITE_URL', 'https://deepdatas.com').rstrip('/')
mail = Mail(app)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
CONTACT_FIELDS = {
	# campo: (obligatorio, largo máximo)
	'name': (True, 120),
	'email': (True, 254),
	'company': (False, 120),
	'subject': (True, 160),
	'message': (True, 5000),
}


@app.context_processor
def inject_globals():
	return {'current_year': date.today().year, 'site_url': app.config['SITE_URL']}


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/contacto", methods=["POST"])
def contacto():
	wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

	# Campo trampa: los humanos no lo ven, los bots suelen completarlo.
	if request.form.get('website'):
		return contact_response(wants_json, True)

	data = {field: (request.form.get(field) or '').strip() for field in CONTACT_FIELDS}
	error = validate_contact(data)
	if error:
		return contact_response(wants_json, False, error, 400)

	if not app.config['MAIL_PASSWORD']:
		logger.error('Formulario de contacto: MAIL_PASSWORD no está configurado.')
		return contact_response(wants_json, False,
			'No pudimos enviar tu mensaje en este momento. Escribinos a contacto@deepdatas.com.', 503)

	try:
		send_contact_email(data)
	except Exception:
		logger.exception('Formulario de contacto: error al enviar el correo.')
		return contact_response(wants_json, False,
			'No pudimos enviar tu mensaje en este momento. Escribinos a contacto@deepdatas.com.', 502)

	return contact_response(wants_json, True)


def validate_contact(data):
	for field, (required, max_length) in CONTACT_FIELDS.items():
		if required and not data[field]:
			return 'Completá todos los campos obligatorios.'
		if len(data[field]) > max_length:
			return 'Uno de los campos es demasiado largo.'
	if not EMAIL_RE.match(data['email']):
		return 'Ingresá un email válido.'
	return None


def send_contact_email(data):
	subject = ' '.join(data['subject'].split())
	msg = Message(
		f'[deepdatas.com] {subject}',
		recipients=app.config['CONTACT_RECIPIENTS'],
		reply_to=data['email'],
	)
	msg.body = (
		'Nueva consulta desde el formulario de contacto del sitio web.\n\n'
		f"Nombre: {data['name']}\n"
		f"Email: {data['email']}\n"
		f"Empresa: {data['company'] or '-'}\n"
		f"Asunto: {subject}\n\n"
		f"{data['message']}\n"
	)
	mail.send(msg)


def contact_response(wants_json, ok, error=None, status=200):
	if wants_json:
		return jsonify(ok=ok, error=error), status
	return redirect(url_for('index', contacto='enviado' if ok else 'error', _anchor='contacto'))


@app.route("/robots.txt")
def robots():
	body = f"User-agent: *\nAllow: /\n\nSitemap: {app.config['SITE_URL']}/sitemap.xml\n"
	return Response(body, mimetype='text/plain')


@app.route("/sitemap.xml")
def sitemap():
	body = (
		'<?xml version="1.0" encoding="UTF-8"?>\n'
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
		f"  <url><loc>{app.config['SITE_URL']}/</loc><changefreq>monthly</changefreq></url>\n"
		'</urlset>\n'
	)
	return Response(body, mimetype='application/xml')
