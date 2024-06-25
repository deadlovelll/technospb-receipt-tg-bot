import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define constants for command states
ADDING_ITEMS, FINISHED = range(2)

# Inline keyboard buttons
keyboard = [
    [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
    [InlineKeyboardButton("Список заказов", callback_data='order_list')]
]

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data['items'] = []
    context.user_data['state'] = ADDING_ITEMS
    keyboard = [
        [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
        [InlineKeyboardButton("Список заказов", callback_data='order_list')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=reply_markup
        )
    else:
        logger.warning("Пустое обновление в функции start")

async def button_handler(update: Update, context: CallbackContext) -> None:
    
    query = update.callback_query
    await query.answer()

    if query.data == 'new_order':
        
        context.user_data['items'] = []
        context.user_data['state'] = ADDING_ITEMS
        keyboard = [
            [InlineKeyboardButton("Отменить заказ", callback_data='cancel_order')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Введите данные о позиции в формате:\n"
            "Nº, Товар, Кол-во, Ед., Цена, Сумма\n"
            "Например:\n"
            "1, Asus ROG Strix, 1, Шт., 1200.00, 1200.00\n",
            reply_markup=reply_markup
        )

    elif query.data == 'add_next_item':
        context.user_data['state'] = ADDING_ITEMS

        await query.edit_message_text(
            "Позиция Успешно Добавлена ✅\n\n"
            "Введите данные о следующей позиции в формате:\n"
            "Nº, Товар, Кол-во, Ед., Цена, Сумма\n"
            "Например:\n"
            "1, Asus ROG Strix, 1, Шт., 1200.00, 1200.00\n"
        )

    elif query.data == 'finish_receipt':
        if context.user_data.get('state') == ADDING_ITEMS:
        
            context.user_data['state'] = FINISHED
            items = context.user_data.get('items', [])
            if not items:
                await update.callback_query.edit_message_text("Вы не добавили ни одной позиции.")
                return

            total_amount = sum(item['Сумма'] for item in items)
            discount = 66.90  # Пример фиксированной скидки
            final_total = total_amount - discount

            # Создание PDF должно происходить здесь
            # ReceiptCreator.create_pdf("check113.pdf", items, total_amount, discount, final_total)

            # Собираем всю информацию в одно сообщение
            order_summary = "Чек создан. Ваш заказ:\n\n"
            for item in items:
                order_summary += f"{item['Nº']}, {item['Товар']}, {item['Кол-во']}, {item['Ед.']}, {item['Цена']}, {item['Сумма']}\n"
            order_summary += f"\nВсего: {total_amount:.2f} ₽\nСкидка: {discount:.2f} ₽\nИтого: {final_total:.2f} ₽"

            await update.callback_query.edit_message_text(order_summary)
        else:
            await update.callback_query.edit_message_text("Используйте команду /start для начала добавления позиций.")

    elif query.data == 'order_list':
        items = context.user_data.get('items', [])
        if not items:
            await query.edit_message_text("Вы не добавили ни одной позиции.")
        else:
            order_summary = "Ваш заказ:\n\n"
            for item in items:
                order_summary += f"{item['Nº']}, {item['Товар']}, {item['Кол-во']}, {item['Ед.']}, {item['Цена']}, {item['Сумма']}\n"
            await query.edit_message_text(order_summary)
            
    elif query.data == 'cancel_order':
        await return_to_main_menu(update, context)

async def return_to_main_menu(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()  # Очищаем пользовательские данные
    await start(update, context)  # Вызываем функцию старта

async def handle_order(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('state') == ADDING_ITEMS:
        try:
            parts = update.message.text.split(', ')
            item = {
                "Nº": int(parts[0]),
                "Товар": parts[1],
                "Кол-во": int(parts[2]),
                "Ед.": parts[3],
                "Цена": float(parts[4]),
                "Сумма": float(parts[5])
            }
            context.user_data['items'].append(item)
            
            # Создаем текст сообщения с информацией о добавленной позиции
            message_text = (
                f"Позиция добавлена:\n"
                f"Nº: {item['Nº']}\n"
                f"Товар: {item['Товар']}\n"
                f"Кол-во: {item['Кол-во']}\n"
                f"Ед.: {item['Ед.']}\n"
                f"Цена: {item['Цена']:.2f}₽\n"
                f"Сумма: {item['Сумма']:.2f}₽\n\n"
                "Чтобы добавить следующую позицию, надмите на соответствующую кнопку."
            )
            
            # Создаем клавиатуру с двумя кнопками
            keyboard = [
                [InlineKeyboardButton("Завершить оформление чека 🧾", callback_data='finish_receipt')],
                [InlineKeyboardButton("Посмотреть Чек 🔎", callback_data='check_receipt')],
                [InlineKeyboardButton("Редактировать Позицию 📝", callback_data='edit_position')],
                [InlineKeyboardButton("Следующая Позиция ⏭️", callback_data='add_next_item')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка при добавлении позиции: {str(e)}")
    else:
        await update.message.reply_text("Используйте команду /start для начала добавления позиций.")

if __name__ == '__main__':
    application = ApplicationBuilder().token("7398191583:AAF2xkBbwcH0hsrBHsF0iEDgMt703u0ocO4").build()

    start_handler = CommandHandler('start', start)
    order_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order)
    button_handler = CallbackQueryHandler(button_handler)

    application.add_handler(start_handler)
    application.add_handler(order_handler)
    application.add_handler(button_handler)

    application.run_polling()

