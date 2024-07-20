from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from button_handlers import *
from logger import LoggerConfig
from receipt_creator import PdfCreator
from email_sender import EmailSender

logger_config = LoggerConfig()
logger = logger_config.get_logger()

logger.info('This is an informational message')
logger.warning('This is a warning message')
logger.error('This is an error message')

START, ADDING_ITEMS, CHOOSING_NEXT, EDITING_ITEMS, PRE_FINISHED, WRITING_CREDENTIALS, FINISHED = range(7)

keyboard = [
    [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
]

async def start(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    
    context.user_data['items'] = []
    context.user_data['state'] = START
    keyboard = [
        [InlineKeyboardButton("Новый заказ", callback_data='new_order')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        start_message = await update.message.reply_text(
            "Привет! Я помогу тебе создать PDF с чеком.",
            reply_markup=reply_markup
        )
        context.user_data['edit_message_id'] = start_message.message_id
    else:
        logger.warning("Пустое обновление в функции start")
        
async def restart(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    
    if update.callback_query:
        query = update.callback_query
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=reply_markup
        )
        
    elif update.message:
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
        
        await ItemEdition.edit_name(update, context, EDITING_ITEMS)
        
    elif query.data == 'edit_qty':
        
        await ItemEdition.edit_qty(update, context, EDITING_ITEMS)
        
    elif query.data == 'edit_price':
        
        await ItemEdition.edit_price(update, context, EDITING_ITEMS)
        
    elif query.data == 'done_edit':
        
        await ItemEdition.done_edit(update, context)

    elif query.data == 'add_next_item':
        
        await AddNextItemHandler.add_next_item(context, query, update, ADDING_ITEMS)
        
    elif query.data == 'check_receipt':
        
        await CheckReceiptHandler.check_receipt(update, context, CHOOSING_NEXT)
        
    elif query.data == 'back':
        
        await CheckReceiptHandler.back(update, context, CHOOSING_NEXT)

    elif query.data == 'finish_receipt':
        
        await FinishReceiptHandler.finish_receipt(context, update, ADDING_ITEMS, FINISHED)
        
    elif query.data == 'pre_create_pdf':
        
        await FinishReceiptHandler.get_credentials(context, update, WRITING_CREDENTIALS)
        
    elif query.data == 'create_pdf':
        
        items = context.user_data['items']
        document_number = context.user_data['document_number']
        current_date_formatted = context.user_data['current_date_formatted']
        
        PdfCreator.create_pdf('filename', items, document_number, current_date_formatted)
        
    elif query.data == 'send_receipt':
        
        email_sender = EmailSender()
        if await email_sender.send_email(to_address=context.user_data['customer-email'], order_number=context.user_data['order-number'],
                                    items=context.user_data['items'], total_amount=context.user_data['total_amount'], discount=0, final_total=context.user_data['total_amount'], file_path=context.user_data['receipt-path']):
            
            await query.message.reply_text(
                'Письмо с чеком успешно отправлено покупателю'
            )
            
            await query.message.reply_text(
                'Для оформления нового заказа нажмите /start'
            )
            
        else:
            
            await query.message.reply_text(
                'Произошла ошибка при отправке письма. Попробуйте перезапустить бота или обратитесь к администратору.'
            )
            
            
    elif query.data == 'cancel_order':
        
        await CancelOrderHandler.return_to_main_menu(update, context, keyboard, START)
        
async def handle_order(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('state') == ADDING_ITEMS:
        
        try:
            
            parts = update.message.text.split(', ')
            context.user_data['last_message_id'] = update.message.message_id
            
            index = len(context.user_data.get('items', [])) + 1
            item = {
                "Nº": index,
                "Товар": parts[0],
                "Кол-во": int(parts[1]),
                "Ед.": 'Шт.',
                "Цена": float(parts[2]),
                "Сумма": float(parts[1]) * float(parts[2])
            }
            context.user_data['items'].append(item)
            
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
            
            keyboard = [
                [InlineKeyboardButton("Следующая Позиция ⏭️", callback_data='add_next_item')],
                [InlineKeyboardButton("Редактировать Позицию 📝", callback_data='edit_item')],
                [InlineKeyboardButton("Посмотреть Чек 🔎", callback_data='check_receipt')],
                [InlineKeyboardButton("Завершить оформление чека 🧾", callback_data='finish_receipt')],
                [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            sent_message = await update.message.reply_text(
                message_text,
                reply_markup=reply_markup
            )
            
            start_message_id = context.user_data.get('edit_message_id')
            last_message_id = context.user_data.get('last_message_id')
            
            chat_id = update.message.chat_id
            
            for i in range(int(start_message_id), int(last_message_id)+1):
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
            
            context.user_data['edit_message_id'] = sent_message.message_id
            
        except Exception as e:
            
            context.user_data['state'] = ADDING_ITEMS
            
            last_message = await update.message.reply_text("Пожалуйста добавьте товар в соответствии с шаблоном")
            
            context.user_data['last_message_id'] = last_message.message_id
        
        context.user_data['state'] = CHOOSING_NEXT
            
    elif context.user_data.get('state') == START:
        
        sent_message = await update.message.reply_text('Пожалуйста, нажмите на кнопку "Новый Заказ" 🙏')
        
        context.user_data['last_message_id'] = sent_message.message_id
        
    elif context.user_data.get('state') == CHOOSING_NEXT:
        
        sent_message = await update.message.reply_text('Пожалуйста, выберите одно из предложенных действий 🙏')
        
        context.user_data['last_message_id'] = sent_message.message_id
        
    elif context.user_data.get('state') == EDITING_ITEMS:
        
        if context.user_data['edit_action'] == 'edit_name':
            
            await ItemEdition.edit_name_handler(update, context)
            
        elif context.user_data['edit_action'] == 'edit_qty':
            
            await ItemEdition.edit_qty_handler(update, context)
            
        elif context.user_data['edit_action'] == 'edit_price':
            
            await ItemEdition.edit_price_handler(update, context)
            
        else:
            
            last_message = await update.message.reply_text('Пожалуйста, выберите данные для изменения или нажмите "Готово" ')
            
            context.user_data['last_message_id'] = last_message.message_id
            
    elif context.user_data.get('state') == FINISHED:
        
        sent_message = await update.message.reply_text('Пожалуйста, выберите одно из предложенных действий 🙏')
        
        context.user_data['last_message_id'] = sent_message.message_id        
        
        
    elif context.user_data.get('state') == WRITING_CREDENTIALS:
        
        await FinishReceiptHandler.get_credentials_handler(update, context)
        
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

