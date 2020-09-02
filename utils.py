import smtplib
import sys
from flask import Flask

# App config
app = Flask(__name__)
app.config.from_object('config.Config')
PROCESS_LOG = app.config.get('PROCESS_LOG')
BASE_FOLDER = app.config.get('BASE_FOLDER')
GMAIL_USER = app.config.get('GMAIL_USER')
GMAIL_PASSWORD = app.config.get('GMAIL_PASSWORD')
SENT_FROM = app.config.get('SENT_FROM')

def log_line(filename, line):
    try:
        with open(filename, 'a+') as file:
            file.write(str(line) + '\n')
            file.close()
    except Exception:
        print(sys.exc_info()[0], line)
        print("Unexpected error:", sys.exc_info()[0], line)

def send_email(address, subject, message):
    message = 'Subject: {}\n\n{}'.format(subject, message)
    try:
        # only works on 'authed' machine?
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(SENT_FROM, address, message)
        server.close()
        print('EMAIL SUCCESS FOR: ' + message)
        log_line(PROCESS_LOG, 'EMAIL SUCCESS FOR: ' + message)
    except Exception:
        # handle all other exceptions
        message = 'EMAIL FAILED FOR: ', message, sys.exc_info()[0]
        print(message)
        log_line(PROCESS_LOG, message)
