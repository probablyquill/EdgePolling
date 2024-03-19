import smtplib
from email.mime.text import MIMEText

def send_email(sender, key, smtp_url, smtp_port, recipients, subject, body):

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    if len(recipients) != 0:
        if len(recipients) > 1:
            msg['To'] = ', '.join(recipients)
        else:
            msg['To'] = recipients[0]

        with smtplib.SMTP_SSL(smtp_url, smtp_port) as smtp_server:
            smtp_server.login(sender, key)
            smtp_server.sendmail(sender, recipients, msg.as_string())