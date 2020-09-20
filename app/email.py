from threading import Thread
from flask_mail import Message
from flask import render_template
from app import appl, mail


def send_async_email(appl, msg):
    with appl.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(appl, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email("[Microblog app] Reset Your Password",
               sender=appl.config["ADMINS"][0],
               recipients=[user.email],
               text_body=render_template("email/reset_password.txt",
                                         user=user, token=token),
               html_body=render_template("email/reset_password.html",
                                         user=user, token=token))



"""
set MAIL_SERVER=smtp.googlemail.com
set MAIL_PORT=587
set MAIL_USE_TLS=1
set MAIL_USERNAME=<your-gmail-username>
set MAIL_PASSWORD=<your-gmail-password>

"""