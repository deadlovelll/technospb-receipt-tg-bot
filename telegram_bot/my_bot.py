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
START, ADDING_ITEMS, CHOOSING_NEXT, EDITING_ITEMS, FINISHED = range(5)

# Inline keyboard buttons
keyboard = [
    [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
]

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data['items'] = []
    context.user_data['state'] = START
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
        
async def restart(update: Update, context: CallbackContext) -> None:
    # Clear user_data to reset bot state for this user
    context.user_data.clear()
    
    # Determine the message to edit based on update type
    if update.callback_query:
        # If the update is a callback query, edit the message associated with it
        query = update.callback_query
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=reply_markup
        )
    elif update.message:
        # If the update is a regular message, reply with the restart message and keyboard
        await update.message.reply_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def button_handler(update: Update, context: CallbackContext) -> None:
    
    query = update.callback_query
    await query.answer()

    if query.data == 'new_order':
        
        await NewOrderHandler.new_order(update, context, query, ADDING_ITEMS)
        
    elif query.data == 'edit_item':
        
        await ItemEdition.item_edit(update, context, EDITING_ITEMS)
        
    elif query.data == 'edit_name':
        
        await ItemEdition.edit_name(update, context)

    elif query.data == 'add_next_item':
        
        await AddNextItemHandler.add_next_item(context, query, update, ADDING_ITEMS)
        
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
        
        context.user_data['state'] = CHOOSING_NEXT
        
        try:
            
            parts = update.message.text.split(', ')
            index = len(context.user_data.get('items', [])) + 1
            
            item = {
                "Nº": index,
                "Товар": parts[0],
                "Кол-во": int(parts[1]),
                "Ед.": 'Шт.',
                "Цена": float(parts[2]),
                "Сумма": float(parts[1])*float(parts[2])
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
            
    elif context.user_data.get('state') == START:
        
        await update.message.reply_text('Пожалуйста, нажмите на кнопку "Новый Заказ" 🙏')
        
    elif context.user_data.get('state') == CHOOSING_NEXT:
        
        await update.message.reply_text('Пожалуйста, выберите одно из предложенных действий 🙏')
        
    # Обработка измененного названия товара
    elif context.user_data.get('state') == EDITING_ITEMS:
            
        await update.message.reply_text('Пожалуйста, выберите данные для изменения или нажмите "Готово" ')
        
    else:
                
        await update.message.reply_text("Используйте команду /start для начала добавления позиций.")

if __name__ == '__main__':
    application = ApplicationBuilder().token("7398191583:AAF2xkBbwcH0hsrBHsF0iEDgMt703u0ocO4").build()

    start_handler = CommandHandler('start', start)
    restart_handler = CommandHandler('restart', restart)
    order_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order)
    button_handler = CallbackQueryHandler(button_handler)

    application.add_handler(start_handler)
    application.add_handler(restart_handler)
    application.add_handler(order_handler)
    application.add_handler(button_handler)

    application.run_polling()

