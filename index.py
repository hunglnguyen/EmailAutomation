# %%
## Jinja Template
import email
from typing import List
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import datetime
import pandas as pd


# Load csv data from the same directory:
def get_data() -> pd.DataFrame:
    data = pd.read_csv('data.csv')
    splitted_data = eval(data.to_json(orient='split'))
    return splitted_data


# Set current working direction as searchpath
def load_template():
    loader = FileSystemLoader(searchpath='.')
    env = Environment(loader=loader)
    template = env.get_template('report_template.html')
    current_year = datetime.datetime.today().strftime('%Y')
    splitted_data = get_data()
    template_vars = {'current_year': current_year, 'table': splitted_data}
    report = template.render(template_vars)

    with open('report.html', 'w') as f:
        f.write(report)
        f.close()


from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


def create_email(subject: 'str', sender: 'str', receivers: List[str], cc: List[str]) -> str:
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart('alternative')
    message['Subject'] = f'{subject}'
    message['From'] = sender_email
    message['To'] = ', '.join(receivers)
    message['Cc'] = ', '.join(cc)
    body_html = '''
    <html>
        <body>
            <p>Hi,</p>
            <p>This is an automatic email from stmplib.</p>
            <p>Regards,<br />-User</p>
        </body>
    </html>
    '''
    with open('report.html', 'r') as f:
        content = f.read()
        f.close()
    html_attachment = MIMEApplication(content)
    html_attachment.add_header('Content-Disposition', f'attachment; filename=Report.html')
    body = MIMEText(body_html, 'html')
    message.attach(body)
    message.attach(html_attachment)
    email_content = message.as_string()
    return email_content


from email import message
import smtplib, ssl


def send_email(sender, receivers, message) -> None:
    context = ssl.create_default_context()
    mail_server = 'smtp.gmail.com'
    port = 587
    try:
        server = smtplib.SMTP(host=mail_server, port=port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, sender_pwd)
        server.sendmail(from_addr=sender, to_addrs=receivers, msg=message)
    except Exception as e:
        print(e)
    finally:
        server.close()


#%%
if __name__ == '__main__':
    sender_email = 'useremail@gmail.com'
    sender_pwd = 'password'
    receivers = ['user1@icloud.com', 'user2@icloud.com']
    Cc = ['user3@icloud.com', 'user4@gmail.com']
    subject = 'List of FinTech Companies in Seattle'
    # Process data and inject jinja template variables into pre-defined template
    load_template()
    message_content = create_email(subject=subject, sender=sender_email, receivers=receivers, cc=Cc)
    send_email(sender=sender_email, receivers=receivers + Cc, message=message_content)
