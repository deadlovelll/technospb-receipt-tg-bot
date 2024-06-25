import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from button_handlers import *
import asyncio
from logger import LoggerConfig

# Instantiate LoggerConfig to configure logging
logger_config = LoggerConfig()
logger = logger_config.get_logger()

# Example usage of the logger
logger.info('This is an informational message')
logger.warning('This is a warning message')
logger.error('This is an error message')

# Define constants for command states
ADDING_ITEMS, FINISHED = range(2)

# Inline keyboard buttons
keyboard = [
    [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
]

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data['items'] = []
    context.user_data['state'] = ADDING_ITEMS
    keyboard = [
        [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "Привет! Я помогу тебе создать PDF с чеком.",
            reply_markup=reply_markup
        )
    else:
        logger.warning("Пустое обновление в функции start")

async def button_handler(update: Update, context: CallbackContext) -> None:
    
    query = update.callback_query
    await query.answer()

    if query.data == 'new_order':
        
        await NewOrderHandler.new_order(update, context, query, ADDING_ITEMS)
        
    elif query.data == 'edit_item':
        
        await ItemEdition.item_edit(update, context)

    elif query.data == 'add_next_item':
        
        await AddNextItemHandler.add_next_item(context, query, ADDING_ITEMS)
        
    elif query.data == 'check_receipt':
        
        await CheckReceiptHandler.check_receipt(update, context, ADDING_ITEMS, FINISHED)
        
    elif query.data == 'back':
        
        await CheckReceiptHandler.back(update, context, ADDING_ITEMS)

    elif query.data == 'finish_receipt':
        
        await FinishReceiptHandler.finish_receipt(context, update, ADDING_ITEMS, FINISHED)
            
    elif query.data == 'cancel_order':
        
        await CancelOrderHandler.return_to_main_menu(update, context, keyboard)
        
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
                "Чтобы добавить следующую позицию, нажмите на соответствующую кнопку."
            )
            
            # Удаление сообщения через 1-2 секунды
            await asyncio.sleep(1)
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            
            # Создаем клавиатуру с кнопками
            keyboard = [
                [InlineKeyboardButton("Следующая Позиция ⏭️", callback_data='add_next_item')],
                [InlineKeyboardButton("Редактировать Позицию 📝", callback_data='edit_item')],
                [InlineKeyboardButton("Посмотреть Чек 🔎", callback_data='check_receipt')],
                [InlineKeyboardButton("Завершить оформление чека 🧾", callback_data='finish_receipt')],
                [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем сообщение о добавлении позиции
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

