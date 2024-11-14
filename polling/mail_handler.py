import smtplib
from email.mime.text import MIMEText
import datetime

def send_email(sender, key, smtp_url, smtp_port, recipients, subject, body):
    now = datetime.datetime.now()
    msg = MIMEText(f"{body} at {now.hour}:{now.minute}:{now.second}")
    msg['Subject'] = subject
    msg['From'] = sender
    if len(recipients) > 1:
        msg['To'] = ', '.join(recipients)
    else:
        msg['To'] = recipients[0]

    with smtplib.SMTP_SSL(smtp_url, smtp_port) as smtp_server:
        smtp_server.login(sender, key)
        smtp_server.sendmail(sender, recipients, msg.as_string())