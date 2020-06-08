import smtplib
from globals import Globals

# logs
process_log = Globals.process_log


def logline(filename, line):
    with open(filename, 'a+') as f:
        f.write(line + '\n')
        f.close()


def logline_pre(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')


def send_email(address, subject, message):
    gmail_user = 'soli@openconcept.ca'
    gmail_password = 'Be8rTr8p!2021'
    sent_from = 'soli@openconcept.ca'

    message = 'Subject: {}\n\n{}'.format(subject, message)

    try:
        # only works on 'authed' machine?
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        # send
        server.sendmail(sent_from, address, message)
        server.close()

        print('EMAIL SUCCESS FOR: ' + message)
        logline(process_log, 'EMAIL SUCCESS FOR: ' + message)

    except Exception as e:
        print('EMAIL FAILED FOR: ' + message + ' ' + e.__str__())
        logline(process_log, 'EMAIL FAILED FOR: ' + message + ' ' + e.__str__())
