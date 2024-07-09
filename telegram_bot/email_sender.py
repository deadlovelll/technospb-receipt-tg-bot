import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    
    def __init__(self) -> None:
        
        self.email_sender = 'technospb-noreply@mail.ru'
        self.smtp_server = 'smtp.mail.ru'
        self.smtp_port = 465 
        self.email_password = 'A44cX5yvuhcN7ZREr0yF'
        
    async def send_email(self, to_address):
        
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = to_address
        msg['Subject'] = "Привет от питона"
        
        body = "Это пробное сообщение"
        msg.attach(MIMEText(body, 'plain'))
        
        await aiosmtplib.send(
            message=msg,
            hostname=self.smtp_server,
            port=self.smtp_port,
            username=self.email_sender,
            password=self.email_password,
            use_tls=True
        )