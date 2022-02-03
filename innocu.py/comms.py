import smtplib

from datetime import datetime, date
import smtplib
import pathlib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.mime.base import MIMEBase

import codecs

from vars import _email_user, _email_pass, _main_receiver_email, _email_server, _email_port

def send_email_with_image(path_plot, dir, smtp_server, smtp_port, from_mail, from_password, to_mail, filename):

    COMMASPACE = ', '

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = 'innocu.py: consumo electrico'
    msg['From'] = from_mail
    msg['To'] = COMMASPACE.join([to_mail])
    msg.preamble = 'innocu.py: consumo electrico'

    # Open the files in binary mode.  Let the MIMEImage class automatically
    # guess the specific image type.
    with open(path_plot, 'rb') as fp:
        #fp = open(path, 'rb')
        img = MIMEImage(fp.read())
        img.add_header('Content-Disposition', 'attachment', filename = filename)
        img.add_header('X-Attachment-Id', '0')
        img.add_header('Content-ID', '<0>')
        fp.close()
        msg.attach(img)

#    with open(path_img, 'rb') as fp:
#        #fp = open(path, 'rb')
#        img = MIMEImage(fp.read())
#        img.add_header('Content-Disposition', 'attachment', filename='header.png')
#        img.add_header('X-Attachment-Id', '1')
#        img.add_header('Content-ID', '<1>')
#        fp.close()
#        msg.attach(img)

    # Attach the HTML email
    f = codecs.open("{0}/{1}/{2}".format(dir, "templates/daily", "report.html"), 'r')
    string = f.read()

    # Replace the relative path to images with ContentID
    html_string = string.replace("./report.png", "cid:0")
    #html_string = html_string.replace("./img/header.png", "cid:1")

    msg.attach(MIMEText(html_string, 'html', 'utf-8'))

    # Send the email via our own SMTP server
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.ehlo()
    server.login(from_mail, from_password)

    server.sendmail(from_mail, [from_mail, to_mail], msg.as_string())
    server.quit()

#send_email_with_image(path_plot, smtp_server, smtp_port, from_mail, from_password, to_mail, "report")