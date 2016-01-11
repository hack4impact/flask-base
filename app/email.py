import os
from flask import render_template
from flask.ext.mail import Message
from . import mail
from app import create_app


def send_email(recipient, subject, template, **kwargs):
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        msg = Message(app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
                      sender=app.config['EMAIL_SENDER'],
                      recipients=[recipient])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)
