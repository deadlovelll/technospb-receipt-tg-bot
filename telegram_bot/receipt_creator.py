from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from num2words import num2words
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit

def split_text_to_lines(text, max_width, canvas, font_name='PTMono', font_size=8):
    canvas.setFont(font_name, font_size)
    lines = simpleSplit(text, font_name, font_size, max_width)
    return lines

class PdfCreator:
    
    @staticmethod
    def create_pdf(filename, items, document_number, current_date):
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        pdfmetrics.registerFont(TTFont('PTMono', 'static/PTMono-Regular.ttf'))

        logo_path = 'static/IMG_2061.JPG'
        logo_width = 0.7 * inch
        logo_height = 0.7 * inch
        c.drawImage(logo_path, 0.5 * inch, height - 1 * inch, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

        c.setFont('PTMono', 8)

        text_x = 1.5 * inch
        c.drawString(text_x, height - 0.5 * inch, 'ИП ИВАНКОВ ТИМОФЕЙ СЕРГЕЕВИЧ')
        c.drawString(text_x, height - 0.65 * inch, "ИНН: 645408776665, ОГРНИП: 324645700011014")
        c.drawString(text_x, height - 0.8 * inch, "197022, РОССИЯ, Г САНКТ-ПЕТЕРБУРГ, Г САНКТ-ПЕТЕРБУРГ,")
        c.drawString(text_x, height - 0.95 * inch, "КАМЕННООСТРОВСКИЙ ПР-КТ, Д 38/96")

        qr_code_path = 'static/QRtiger.png'
        qr_code_width = 0.7 * inch
        qr_code_height = 0.7 * inch
        c.drawImage(qr_code_path, 7.0 * inch, height - 1 * inch, width=qr_code_width, height=qr_code_height, preserveAspectRatio=True, mask='auto')

        c.setFont('PTMono', 10)
        c.drawString(0.65 * inch, height - 1.5 * inch, f"Товарный Чек Nº {document_number} от {current_date}")

        table_headers = ["Nº", "Товар", "Кол-во", "Ед.", "Цена", "Сумма"]
        col_widths = [0.5, 3.5, 1.0, 0.5, 1.0, 1.0]

        x_start = 0.5 * inch
        y_start = height - 2.0 * inch

        c.setFont('PTMono', 8)

        row_height = 0.25

        for i, header in enumerate(table_headers):
            if i == 1:
                c.drawString(x_start, y_start, header)
            else:
                c.drawCentredString(x_start + col_widths[i] * inch / 2, y_start, header)
            x_start += col_widths[i] * inch

        c.line(0.5 * inch, y_start - 0.1 * inch, width - 0.5 * inch, y_start - 0.1 * inch)

        y_start -= 0.25 * inch
        for item in items:
            x_start = 0.5 * inch

            c.drawCentredString(x_start + col_widths[0] * inch / 2, y_start, str(item["Nº"]))
            x_start += col_widths[0] * inch

            wrapped_lines = split_text_to_lines(item["Товар"], col_widths[1] * inch, c)

            for line in wrapped_lines:
                c.drawString(x_start, y_start, line.strip())
                y_start -= 0.15 * inch

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
        discount = 0.00
        final_total = total_amount - discount

        y_start -= 0.2 * inch
        c.drawString(0.5 * inch, y_start, f"Всего наименований: {len(items)} на сумму {total_amount:,.2f} ₽")

        total_in_words = num2words(str(total_amount).split('.')[0], lang='ru')
        c.drawString(0.5 * inch, y_start - 0.2 * inch, total_in_words.capitalize() + ' Рублей' + ' 00' + ' Копеек')

        c.drawString(6.5 * inch, y_start, f"Сумма: {total_amount:,.2f} ₽")
        c.drawString(6.5 * inch, y_start - 0.2 * inch, f"Скидка: {discount:,.2f} ₽")
        c.drawString(6.5 * inch, y_start - 0.4 * inch, f"Итого: {final_total:,.2f} ₽")

        stamp_path = 'static/2024-06-25 3.41.51 PM.jpg'
        stamp_width = 1.2 * inch
        stamp_height = 1.2 * inch

        c.saveState()
        c.drawImage(stamp_path, 1.05 * inch, y_start - 1.5 * inch, width=stamp_width, height=stamp_height)
        c.restoreState()

        c.setFont('PTMono', 6)
        c.drawString(0.5 * inch, y_start - 1.0 * inch, "М.П.")
        c.line(0.9 * inch, y_start - 1.05 * inch, 2.7 * inch, y_start - 1.05 * inch)
        
        c.showPage()
        
        y_start = letter[1] - 0.0 * inch  

        guarantee_title = "ГАРАНТИЙНЫЙ ТАЛОН"
        c.setFont('PTMono', 9)  
        c.drawString(0.5 * inch, y_start - 0.5 * inch, guarantee_title)

        terms_blocks = [
            [
                "1. Гарантийные условия и возврат товара:",
                "1.1. Гарантийное обслуживание:",
                "Настоящий документ подтверждает, что на приобретенные товары предоставляется гарантийное обслуживание в соответствии с законодательством Российской Федерации. Гарантийный срок предусмотрен документацией производителя. В случае выявления дефектов, возникших по вине производителя в течение гарантийного срока, покупатель вправе обратиться в авторизованный сервисный центр для устранения недостатков.",
            ],
            [
                "1.2. Условия возврата товара:",
                "1.2.1. Возврат товара без признаков повреждений или дефектов возможен с удержанием сервисной комиссии в размере 20% от стоимости товара. Возврат денежных средств осуществляется в течение 10 рабочих дней с момента возврата товара.",
                "1.2.2. В случае обнаружения при получении товара внешних повреждений или отсутствия согласованных комплектующих покупатель обязан немедленно уведомить продавца об этом и отказаться от принятия товара до устранения указанных недостатков.",
                "1.2.3. Распаковка товара должна быть зафиксирована на видео в течение 14 календарных дней с момента получения товара по накладной. На видеозаписи должно быть четко видно, что упаковка не вскрыта и находится в целостности, а также зафиксирован стикер с номером накладной. В случае отсутствия указанной видеозаписи гарантийные обязательства и возврат денежных средств не предоставляются.",
            ],
            [
                "1.3. Ограничения по гарантии:",
                "1.3.1. Гарантийные обязательства распространяются исключительно на дефекты, возникшие по вине производителя, а также на повреждения, произошедшие во время транспортировки товара, при условии, что данные повреждения были зафиксированы в момент получения товара и надлежащим образом задокументированы на видеосъемку. В случае выявления таких повреждений, покупатель обязан немедленно уведомить продавца и предоставить соответствующие доказательства, включая фотоматериалы и видеозаписи.",
                "1.3.2. Гарантия не распространяется на повреждения, вызванные неправильной эксплуатацией, несанкционированным ремонтом или модификацией товара, а также на естественный износ и старение материалов.",
                "1.3.3. Гарантия не покрывает повреждения, возникшие вследствие воздействия внешних факторов, включая, но не ограничиваясь, механические повреждения, воздействие жидкостей, химических веществ и экстремальных температур.",
            ],
            [
                "1.4. Процедура возврата:",
                "1.4.1. Для осуществления возврата товара покупатель обязан предоставить оригинал товарного чека и видеорегистрацию распаковки и тестирования товара.",
                "1.4.2. В случае возврата товара надлежащего качества, все расходы, связанные с доставкой товара до места возврата, несет покупатель.",
            ],
            [
                "1.5. Ограничение ответственности:",
                "1.5.1. Настоящий документ не является закрывающим документом и не предназначен для использования в бухгалтерском учете.",
                "1.5.2. Настоящий документ является подтверждением предоставления гарантийных обязательств и не заменяет собой счет-фактуру, товарную накладную или иной документ, необходимый для бухгалтерской отчетности.",
                "1.5.3. Продавец не несет ответственности за несоответствие технических характеристик товара ожиданиям покупателя, за исключением случаев, предусмотренных действующим законодательством.",
                "1.5.4. Продавец не несет ответственности за возможные несовместимости товара с оборудованием или программным обеспечением покупателя, а также за ущерб, возникший вследствие такой несовместимости.",
            ],
            [
                "Примечание: Для получения дополнительной информации или разъяснений, пожалуйста, свяжитесь с нашим менеджером на Авито или по адресу электронной почты technoospb@mail.ru."
            ]
        ]

        # Ширина текстовой области
        width = letter[0] - 2 * 0.5 * inch

        # Распечатываем условия на новой странице
        line_height = 9  # Интервал между блоками условий

        for block in terms_blocks:
            for line in block:
                words = line.split()
                lines = []
                current_line = ""

                for word in words:
                    if c.stringWidth(current_line + " " + word) < width:
                        current_line += " " + word
                    else:
                        lines.append(current_line.strip())
                        current_line = word

                if current_line:
                    lines.append(current_line.strip())

                for wrapped_line in lines:
                    c.drawString(0.5 * inch, y_start - 1.1 * inch, wrapped_line)
                    y_start -= line_height

                y_start -= line_height  # Добавляем пробел между блоками условий

            y_start -= line_height  # Добавляем большой пробел после каждого пункта

        # Сохраняем и закрываем PDF
        c.showPage()
        c.save()
 