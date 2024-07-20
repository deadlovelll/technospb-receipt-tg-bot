import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class EmailSender:
    
    def __init__(self) -> None:
        self.email_sender = 'technospb-noreply@mail.ru'
        self.smtp_server = 'smtp.mail.ru'
        self.smtp_port = 465 
        self.email_password = 'A44cX5yvuhcN7ZREr0yF'
        
    async def send_email(self, to_address, order_number, items, total_amount, discount, final_total, file_path) -> bool:
        
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = to_address
        msg['Subject'] = f"Чек по заказу {order_number}"
        
        body = self.generate_html_body(order_number, items, total_amount, discount, final_total, to_address)
        msg.attach(MIMEText(body, 'html'))

        # Attach the file
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_path[2:]}",
        )
        msg.attach(part)

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.email_sender,
                password=self.email_password,
                use_tls=True
            )

            return True
            
        except Exception:
            
            return False
            
    def generate_html_body(self, order_number, items, total_amount, discount, final_total, to_address):
        
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb; text-align: center;">{item['Nº']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb;">{item['Товар']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb; text-align: center;">{item['Кол-во']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb;">{item['Ед.']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb;">{item['Цена']:.2f}₽</td>
                <td style="padding: 8px; border-bottom: 1px solid #ebebeb;">{item['Сумма']:.2f}₽</td>
            </tr>
            """
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 20px;
                    color: #1a1a1a;
                    background-color: #e3e8ee;
                }}
                .container {{
                    width: 100%;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    padding: 10px;
                    position: relative; /* Добавляем позиционирование */
                }}
                .header {{
                    padding-bottom: 10px;
                    border-bottom: 1px solid #ebebeb;
                    display: flex; /* Используем flexbox для выравнивания элементов */
                    justify-content: space-between; /* Выравниваем элементы по горизонтали */
                    align-items: center; /* Выравниваем элементы по вертикали */
                    position: relative; /* Добавляем позиционирование */
                }}
                .header-text {{
                    font-size: 14px;
                    color: #7a7a7a;
                }}
                .header img {{
                    margin-left: auto;
                    margin-right: -20px;
                }}
                @media (max-width: 600px) {{
                .header img {{
                        max-width: 30%; 
                        margin-right: -10px; 
                    }}
                }}
                .amount {{
                    font-size: 36px;
                    line-height: 40px;
                    font-weight: 600;
                    color: #1a1a1a;
                    text-align: center;
                }}
                .details {{
                    text-align: left;
                    margin-top: 10px;
                    color: #7a7a7a;
                    font-size: 14px;
                    line-height: 24px;
                    font-weight: 500;
                }}
                .items-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .items-table th {{
                    padding: 8px;
                    border-bottom: 2px solid #ebebeb;
                    text-align: center;
                    background-color: #f5f5f5;
                }}
                .items-table td {{
                    padding: 8px;
                    border-bottom: 1px solid #ebebeb;
                }}
                
                @media (min-width: 601px) {{
                .items-table td:nth-child(2),
                .items-table td:nth-child(3) {{
                    text-align: left; /* Выравниваем кол-во и ед. по левому краю на широких экранах */
                }}
                }}
                
                .summary-table {{
                    width: 100%;
                    margin-top: 20px;
                    border-top: 2px solid #ebebeb;
                    padding-top: 10px;
                }}
                .summary-table td {{
                    padding: 8px;
                    text-align: right;
                    font-weight: 600;
                }}
                .summary-table .label {{
                    color: #7a7a7a;
                    font-weight: 500;
                }}
                .receipt-info {{
                    margin-top: 20px;
                    border-top: 1px solid #ebebeb;
                    padding-top: 10px;
                    font-size: 14px;
                    color: #7a7a7a;
                    line-height: 1.5;
                    text-align: center; /* Выравниваем текст по центру */
                }}
                
                .receipt-info span {{
                    white-space: nowrap;
                }}
                
                .receipt-info img {{
                    vertical-align: text-bottom;
                    margin-right: 4px;
                }}

                @media (min-width: 601px) {{
                    .receipt-info {{
                        text-align: right; /* Выравниваем текст по правому краю на широких экранах */
                    }}
                }}
                .footer {{
                    font-size: 12px;
                    color: #7a7a7a;
                    text-align: center;
                    margin-top: 20px;
                }}
                .logo-container {{
                    text-align: center; /* Центрируем содержимое */
                    margin-bottom: 20px; /* Пространство между логотипом и заголовком */
                }}
                .logo {{
                    max-width: 300px; /* Максимальная ширина логотипа */
                    height: auto; /* Автоматическая высота, чтобы сохранить пропорции */
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo-container">
                    <img src="https://s3.timeweb.cloud/6860a950-6597618a-3711-43c6-a77f-ebe0447d21b7/IMG_2201-removebg-preview.png" alt="Logo" class="logo">
                </div>
                <div class="header">
                    <div class="header-text">
                        <p>Покупка в TechnoSpb</p>
                        <p>Номер Заказа: #{order_number}</p>
                        <p>Почта Покупателя: {to_address}</p>
                        <p>Дата Покупки: {current_date}</p>
                        <p>Сумма: {final_total:.2f}₽</p>
                    </div>
                    <img src="https://ci3.googleusercontent.com/meips/ADKq_Nb0PIKp4BW7Q9dGZWAbhhehqH1C7jSJqPrktJ2lzqT_ZKhZb3k_OE2EHw4d-X52LFFEkrtG1wxOZCHxAtGyrjX1yDzocuLEuaTPZySKYYjONkOVyakKaNjTutQUWWCz6ZcbCwWN=s0-d-e1-ft#https://stripe-images.s3.amazonaws.com/emails/invoices_invoice_illustration.png" alt="invoice illustration">
                </div>
                <div class="amount">Детали Заказа</div>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Номер</th>
                            <th>Товар</th>
                            <th>Количество</th>
                            <th>Ед.</th>
                            <th>Цена</th>
                            <th>Сумма</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                <table class="summary-table">
                    <tr>
                        <td class="label">Общая сумма:</td>
                        <td>{total_amount:.2f}₽</td>
                    </tr>
                    <tr>
                        <td class="label">Скидка:</td>
                        <td>-{discount:.2f}₽</td>
                    </tr>
                    <tr>
                        <td class="label">Итоговая сумма:</td>
                        <td>{final_total:.2f}₽</td>
                    </tr>
                </table>
                <div class="receipt-info desktop-right-align">
                    <div><span>Номер квитанции</span> &nbsp;&nbsp; #{order_number}</div>
                </div>
                <br>
                <div class="amount">Спасибо за покупку<br>И проявленное Доверие!</div>
                <div class="footer">
                    <br>
                    <br>
                    <div style="font-size: 14px; color: #7a7a7a;">
                        <span style="white-space: nowrap;">
                            Остались вопросы? Задайте его на <a href="https://avito.ru/brands/i183525050" style="color: #007bff; text-decoration: none; outline: none;">Авито</a><br>
                            или свяжитесь с Нами по адресу <a href="mailto:technoospb@mail.ru" style="color: #007bff; text-decoration: none; outline: none;">technoospb@mail.ru</a>.
                        </span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
