from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import smtplib, ssl





app = Flask(__name__)
bootstrap = Bootstrap(app)


app.config['MAIL_SERVER']='smtp.office365.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contacto@deepdatas.com'
app.config['MAIL_PASSWORD'] = 'Kav12067'
#app.config['MAIL_USE_TLS'] = False
mail = Mail(app)




@app.route("/")
def index():
	print('hola1')
	return render_template('index.html')

@app.route("/mail")
def mail():
	send_email()

	return 'enviado'

	

#@app.route("/form", methods=["POST"])
def send_email():
	
	#nombre = request.form.get("name")
	#email = request.form.get("email")
	#subject = request.form.get("subject")
	#mensaje = request.form.get("message")

	msg = Message('Hello from the other side!', 
		sender = 'contacto@deepdatas.com', 
		recipients = ['fbloise@deepdatas.com','mgarcia@deepdatas.com','itorres@deepdatas.com'])
	print('msg')

	msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
	print('body')
	mail.send(msg)
	print('send')

	return "Message sent!"


"""
	port = 587  # For starttls
	smtp_server = "smtp.gmail.com"
	sender_email = "my@gmail.com"
	receiver_email = "your@gmail.com"
	password = input("Type your password and press enter:")
	message = " Subject: Hi there. This message is sent from Python."

	context = ssl.create_default_context()
	with smtplib.SMTP(smtp_server, port) as server:
	    server.ehlo()  # Can be omitted
	    server.starttls(context=context)
	    server.ehlo()  # Can be omitted
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, message)




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

