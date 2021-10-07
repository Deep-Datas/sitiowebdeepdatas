from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message


app = Flask(__name__)
bootstrap = Bootstrap(app)


app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'contacto@deepdatas.com'
app.config['MAIL_PASSWORD'] = 'Kav12067'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/form", methods=["POST"])
def form():
	nombre = request.form.get("name")
	email = request.form.get("email")
	subject = request.form.get("subject")
	mensaje = request.form.get("message")

	msg = Message('Hello from the other side!', sender = 'contacto@deepdatas.com', recipients = ['fbloise@deepdatas.com','mgarcia@deepdatas.com','itorres@deepdatas.com'])
	msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
	mail.send(msg)
	return "Message sent!"


"""
@app.route("/form", methods=["POST"])
def form():
	nombre = request.form.get("name")
	email = request.form.get("email")
	subject = request.form.get("subject")
	mensaje = request.form.get("message")

    msg = mail.send_message(
        mensaje,
        sender='ri******a@gmail.com',
        recipients=['ri*********07@msn.com'],
        body="Congratulations you've succeeded!"
    )
    return 'Mail sent'

"""

