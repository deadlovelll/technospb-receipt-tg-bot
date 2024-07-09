from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from num2words import num2words
import textwrap

class PdfCreator:

    def create_pdf(filename, items, document_number, current_date):
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        pdfmetrics.registerFont(TTFont('PTMono', 'static/PTMono-Regular.ttf'))

        logo_path = 'static/IMG_2061.JPG'
        logo_width = 1 * inch
        logo_height = 1 * inch
        c.drawImage(logo_path, 0.5 * inch, height - 1.2 * inch, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

        c.setFont('PTMono', 10)

        text_x = 1.5 * inch
        c.drawString(text_x, height - 0.5 * inch, 'ИП ИВАНКОВ ТИМОФЕЙ СЕРГЕЕВИЧ')
        c.drawString(text_x, height - 0.7 * inch, "ИНН: 645408776665, ОГРНИП: 324645700011014")
        c.drawString(text_x, height - 0.9 * inch, "197022, РОССИЯ, Г САНКТ-ПЕТЕРБУРГ, Г САНКТ-ПЕТЕРБУРГ,")
        c.drawString(text_x, height - 1.1 * inch, "КАМЕННООСТРОВСКИЙ ПР-КТ, Д 38/96")

        qr_code_path = 'static/QRtiger.png' 
        qr_code_width = 1 * inch
        qr_code_height = 1 * inch
        c.drawImage(qr_code_path, 7.0 * inch, height - 1.2 * inch, width=qr_code_width, height=qr_code_height, preserveAspectRatio=True, mask='auto')

        c.setFont('PTMono', 14)
        c.drawString(0.65 * inch, height - 2.0 * inch, f"Чек Nº {document_number} от {current_date}")

        table_headers = ["Nº", "Товар", "Кол-во", "Ед.", "Цена", "Сумма"]
        col_widths = [0.5, 3.5, 1.0, 0.5, 1.0, 1.0]  

        x_start = 0.5 * inch
        y_start = height - 2.5 * inch

        c.setFont('PTMono', 10)

        row_height = 0.3 

        for i, header in enumerate(table_headers):
            if i == 1:  
                c.drawString(x_start, y_start, header)
            else:
                c.drawCentredString(x_start + col_widths[i] * inch / 2, y_start, header)
            x_start += col_widths[i] * inch

        c.line(0.5 * inch, y_start - 0.1 * inch, width - 0.5 * inch, y_start - 0.1 * inch)

        y_start -= 0.3 * inch
        for item in items:
            x_start = 0.5 * inch

            c.drawCentredString(x_start + col_widths[0] * inch / 2, y_start, str(item["Nº"]))
            x_start += col_widths[0] * inch

            wrapped_lines = textwrap.wrap(item["Товар"], width=30)

            for line in wrapped_lines:
                c.drawString(x_start, y_start, line)
                y_start -= 0.2 * inch  

            x_start += col_widths[1] * inch

            c.drawCentredString(x_start + col_widths[2] * inch / 2, y_start + row_height * inch / 2, str(item["Кол-во"]))
            x_start += col_widths[2] * inch

            c.drawCentredString(x_start + col_widths[3] * inch / 2, y_start + row_height * inch / 2, item["Ед."])
            x_start += col_widths[3] * inch

            c.drawCentredString(x_start + col_widths[4] * inch / 2, y_start + row_height * inch / 2, f"{item['Цена']:,.2f}")
            x_start += col_widths[4] * inch

            c.drawCentredString(x_start + col_widths[5] * inch / 2, y_start + row_height * inch / 2, f"{item['Сумма']:,.2f}")
            x_start += col_widths[5] * inch

            c.line(0.5 * inch, y_start - 0.1 * inch, width - 0.5 * inch, y_start - 0.1 * inch)

            y_start -= row_height * inch

        total_amount = sum(item["Сумма"] for item in items)
        discount = 00.00
        final_total = total_amount - discount

        y_start -= 0.3 * inch
        c.drawString(0.5 * inch, y_start, f"Всего наименований: {len(items)} на сумму {total_amount:,.2f} ₽")
        
        total_in_words = num2words(str(total_amount).split('.')[0], lang='ru')
        c.drawString(0.5 * inch, y_start - 0.3 * inch, total_in_words.capitalize() +  ' Рублей' + ' 00' + ' Копеек')

        c.drawString(6.5 * inch, y_start, f"Сумма: {total_amount:,.2f} ₽")
        c.drawString(6.5 * inch, y_start - 0.3 * inch, f"Скидка: {discount:,.2f} ₽")
        c.drawString(6.5 * inch, y_start - 0.6 * inch, f"Итого: {final_total:,.2f} ₽")

        stamp_path = 'static/2024-06-25 3.41.51 PM.jpg'
        stamp_width = 1.5 * inch
        stamp_height = 1.5 * inch

        c.saveState()

        c.drawImage(stamp_path, 1.05 * inch, y_start - 2.0 * inch, width=stamp_width, height=stamp_height)

        c.restoreState()

        c.setFont('PTMono', 10)
        c.drawString(0.5 * inch, y_start - 1.35 * inch, "М.П.")

        c.line(0.9 * inch, y_start - 1.4 * inch, 2.7 * inch, y_start - 1.4 * inch)

        c.showPage()
        c.save()
        
        return c 