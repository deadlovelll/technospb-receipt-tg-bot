from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
import textwrap

def create_pdf(filename, items):
    # Create Canvas object
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Register PT Mono font (replace 'PTMono-Regular.ttf' with your actual font file path)
    pdfmetrics.registerFont(TTFont('PTMono', 'PTMono-Regular.ttf'))

    logo_path = '/content/IMG_2061.JPG'
    logo_width = 1 * inch
    logo_height = 1 * inch
    c.drawImage(logo_path, 0.5 * inch, height - 1.2 * inch, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

    # Set font for company information
    c.setFont('PTMono', 10)

    # Company information (adjust these to fit your company details)
    text_x = 1.5 * inch
    c.drawString(text_x, height - 0.5 * inch, 'ИП ИВАНКОВ ТИМОФЕЙ СЕРГЕЕВИЧ')
    c.drawString(text_x, height - 0.7 * inch, "ИНН: 645408776665, ОГРНИП: 324645700011014")
    c.drawString(text_x, height - 0.9 * inch, "197022, РОССИЯ, Г САНКТ-ПЕТЕРБУРГ, Г САНКТ-ПЕТЕРБУРГ,")
    c.drawString(text_x, height - 1.1 * inch, "КАМЕННООСТРОВСКИЙ ПР-КТ, Д 38/96")

    # Draw QR code image
    qr_code_path = '/content/QRtiger.png'  # Replace with your QR code image path
    qr_code_width = 1 * inch
    qr_code_height = 1 * inch
    c.drawImage(qr_code_path, 7.0 * inch, height - 1.2 * inch, width=qr_code_width, height=qr_code_height, preserveAspectRatio=True, mask='auto')

    # Title of the invoice
    c.setFont('PTMono', 14)
    c.drawString(0.65 * inch, height - 2.0 * inch, "Чек Nº 00004 от 24.06.2020")

    # Headers of the table
    table_headers = ["Nº", "Товар", "Кол-во", "Ед.", "Цена", "Сумма"]
    col_widths = [0.5, 3.5, 1.0, 0.5, 1.0, 1.0]  # Adjust column widths as needed

    x_start = 0.5 * inch
    y_start = height - 2.5 * inch

    c.setFont('PTMono', 10)

    row_height = 0.3  # Height of each row

    # Draw headers
    for i, header in enumerate(table_headers):
        if i == 1:  # Left-align the "Наименование" header
            c.drawString(x_start, y_start, header)
        else:
            c.drawCentredString(x_start + col_widths[i] * inch / 2, y_start, header)
        x_start += col_widths[i] * inch

    # Draw horizontal line before the first item
    c.line(0.5 * inch, y_start - 0.1 * inch, width - 0.5 * inch, y_start - 0.1 * inch)

    y_start -= 0.3 * inch
    for item in items:
        x_start = 0.5 * inch

        c.drawCentredString(x_start + col_widths[0] * inch / 2, y_start, str(item["Nº"]))
        x_start += col_widths[0] * inch

        # Wrap text for the "Наименование" column if it exceeds 30 characters
        wrapped_lines = textwrap.wrap(item["Товар"], width=30)

        # Draw each line of wrapped text
        for line in wrapped_lines:
            c.drawString(x_start, y_start, line)
            y_start -= 0.2 * inch  # Adjust line spacing as needed

        x_start += col_widths[1] * inch

        # Center-align and position vertically for quantity
        c.drawCentredString(x_start + col_widths[2] * inch / 2, y_start + row_height * inch / 2, str(item["Кол-во"]))
        x_start += col_widths[2] * inch

        # Center-align and position vertically for unit
        c.drawCentredString(x_start + col_widths[3] * inch / 2, y_start + row_height * inch / 2, item["Ед."])
        x_start += col_widths[3] * inch

        # Center-align and position vertically for price
        c.drawCentredString(x_start + col_widths[4] * inch / 2, y_start + row_height * inch / 2, f"{item['Цена']:,.2f}")
        x_start += col_widths[4] * inch

        # Center-align and position vertically for total
        c.drawCentredString(x_start + col_widths[5] * inch / 2, y_start + row_height * inch / 2, f"{item['Сумма']:,.2f}")
        x_start += col_widths[5] * inch

        # Draw a horizontal line after each item
        c.line(0.5 * inch, y_start - 0.1 * inch, width - 0.5 * inch, y_start - 0.1 * inch)

        y_start -= row_height * inch

    # Totals
    total_amount = sum(item["Сумма"] for item in items)
    discount = 66.90
    final_total = total_amount - discount

    y_start -= 0.3 * inch
    c.drawString(0.5 * inch, y_start, f"Всего наименований: {len(items)} на сумму {total_amount:,.2f} ₽")
    c.drawString(0.5 * inch, y_start - 0.3 * inch, "Пять тысяч шестьсот восемьдесят три рубля 10 копеек")

    c.drawString(6.5 * inch, y_start, f"Сумма: {total_amount:,.2f} ₽")
    c.drawString(6.5 * inch, y_start - 0.3 * inch, f"Скидка: {discount:,.2f} ₽")
    c.drawString(6.5 * inch, y_start - 0.6 * inch, f"Итого: {final_total:,.2f} ₽")

    # Draw the stamp image
    stamp_path = '/content/2024-06-25 3.41.51 PM.jpg'
    stamp_width = 1.5 * inch
    stamp_height = 1.5 * inch

    # Save the current state of the canvas
    c.saveState()

    # Draw the image
    c.drawImage(stamp_path, 1.05 * inch, y_start - 2.0 * inch, width=stamp_width, height=stamp_height)

    # Restore the saved state to reset the canvas rotation
    c.restoreState()

    # Draw "М.П." text to the right of the stamp image
    c.setFont('PTMono', 10)
    c.drawString(0.5 * inch, y_start - 1.35 * inch, "М.П.")

    c.line(0.9 * inch, y_start - 1.4 * inch, 2.7 * inch, y_start - 1.4 * inch)

    # Save the PDF file
    c.showPage()
    c.save()
    
# Data about items
items = [
    {"Nº": 1, "Товар": "Asus ROG Strix Scar G16 i9-14900HX / RTX4090 / 64 / 4TB ", "Кол-во": 1, "Ед.": "Шт.", "Цена": 1200.00, "Сумма": 1200.00},
    {"Nº": 2, "Товар": "Lenovo Legion 5i Pro / I9-14900HX / RTX 4070 / 32GB / 2TB / 2.5K / IPS", "Кол-во": 3, "Ед.": "Шт.", "Цена": 2410.00, "Сумма": 2410.00},
    {"Nº": 3, "Товар": "Kuycon G27X", "Кол-во": 1, "Ед.": "Шт.", "Цена": 2140.00, "Сумма": 2140.00}
]

# Generate PDF file
create_pdf("check113.pdf", items)