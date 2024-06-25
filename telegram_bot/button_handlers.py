from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, CallbackContext


class NewOrderHandler:
    
    @staticmethod
    async def new_order(update: Update, context: CallbackContext, query, ADDING_ITEMS):
        
        context.user_data['items'] = []
        context.user_data['state'] = ADDING_ITEMS
        keyboard = [
            [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Введите данные о позиции в формате:\n"
            "Товар, Кол-во, Цена,\n"
            "Например:\n"
            "Asus ROG Strix, 1, 1200.00\n",
            reply_markup=reply_markup
        )
        
class AddNextItemHandler:
    
    @staticmethod
    async def add_next_item(context: CallbackContext, query, update, ADDING_ITEMS):
        context.user_data['state'] = ADDING_ITEMS
        
        # Удаление всех сообщений с текстом "Пожалуйста, выберите одно из предложенных действий 🙏"
        async for message in context.bot.get_chat_history(chat_id=update.effective_chat.id):
            if message.text == "Пожалуйста, выберите одно из предложенных действий 🙏":
                await message.delete()

        await query.edit_message_text(
            "Позиция Успешно Добавлена ✅\n\n"
            "Введите данные о следующей позиции в формате:\n"
            "Nº, Товар, Кол-во, Ед., Цена, Сумма\n"
            "Например:\n"
            "1, Asus ROG Strix, 1, Шт., 1200.00, 1200.00\n"
        )
        
class FinishReceiptHandler:
    
    @staticmethod
    async def finish_receipt(context: CallbackContext, update: Update, ADDING_ITEMS, FINISHED):
        if context.user_data.get('state') == ADDING_ITEMS:
    
            context.user_data['state'] = FINISHED
            items = context.user_data.get('items', [])
            if not items:
                await update.callback_query.edit_message_text("Вы не добавили ни одной позиции.")
                return

            total_amount = sum(item['Сумма'] for item in items)
            discount = 0.00  # Пример фиксированной скидки
            final_total = total_amount - discount

            # Создание PDF должно происходить здесь
            # ReceiptCreator.create_pdf("check113.pdf", items, total_amount, discount, final_total)

            order_summary = "Чек создан. Ваш заказ:\n\n"
            for item in items:
                order_summary += f"{item['Nº']}, {item['Товар']}, {item['Кол-во']}, {item['Ед.']}, {item['Цена']}, {item['Сумма']}\n"
            order_summary += f"\nВсего: {total_amount:.2f} ₽\nСкидка: {discount:.2f} ₽\nИтого: {final_total:.2f} ₽"
            
            keyboard = [
                [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.callback_query.edit_message_text(order_summary, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text("Используйте команду /start для начала добавления позиций.")
            
            
class CancelOrderHandler:
    
    @staticmethod
    async def return_to_main_menu(update: Update, context: CallbackContext, keyboard) -> None:
        context.user_data.clear() 
        query = update.callback_query
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=reply_markup
        )
        
class CheckReceiptHandler:
    
    @staticmethod
    async def check_receipt(update: Update, context: CallbackContext, ADDING_ITEMS, FINISHED) -> None:
        # Log current state for debugging
        current_state = context.user_data.get('state')
        
        if current_state == ADDING_ITEMS:
            context.user_data['state'] = FINISHED
            items = context.user_data.get('items', [])
            
            if not items:
                await update.callback_query.answer()
                await update.callback_query.message.reply_text("Вы не добавили ни одной позиции.")
                return

            total_amount = sum(item['Сумма'] for item in items)
            discount = 0.00  # Пример фиксированной скидки
            final_total = total_amount - discount

            # Собираем всю информацию в одно сообщение
            order_summary = "Текущий чек по заказу:\n\n"
            for item in items:
                order_summary += f"{item['Nº']}, {item['Товар']}, {item['Кол-во']}, {item['Ед.']}, {item['Цена']}, {item['Сумма']}\n"
            order_summary += f"\nВсего: {total_amount:.2f} ₽\nСкидка: {discount:.2f} ₽\nИтого: {final_total:.2f} ₽"
            
            keyboard = [
                [InlineKeyboardButton("Завершить оформление чека 🧾", callback_data='finish_receipt')],
                [InlineKeyboardButton("Назад ⏪", callback_data='back')],
                [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send the message with the receipt summary
            msg = await update.callback_query.message.reply_text(order_summary, reply_markup=reply_markup)
            
            # Store the sent message's message_id in user_data
            context.user_data['last_message_id'] = msg.message_id
        else:
            print('wtf')

    @staticmethod
    async def back(update: Update, context: CallbackContext, ADDING_ITEMS) -> None:
        # Get the current message_id from user_data
        current_message_id = context.user_data.get('last_message_id')

        if current_message_id:
            try:
                # Delete the current message using the bot's context
                await context.bot.delete_message(
                    chat_id=update.callback_query.message.chat_id,
                    message_id=current_message_id
                )
                # After deleting the message, reset the state to ADDING_ITEMS
                context.user_data['state'] = ADDING_ITEMS
                # Optionally, you can send a confirmation message or perform any other actions here
                await update.callback_query.answer("Возвращение к добавлению позиций.")
            except Exception as e:
                print(f"Error deleting message: {e}")

        else:
            await update.callback_query.answer("Нет текущего сообщения для удаления.")
            
class ItemEdition:
    
    @staticmethod
    async def item_edit(update: Update, context: CallbackContext, EDITING_ITEMS) -> None:
        context.user_data['state'] = EDITING_ITEMS
        query = update.callback_query
        await query.answer()
        
        try:
            # Access the Message object from the CallbackQuery
            message = query.message
            
            # Extract item details from the text of the message
            item_text = message.text
            parts = item_text.split('\n')
            item = {
                'Nº': int(parts[1].split(': ')[1]),
                'Товар': parts[2].split(': ')[1],
                'Кол-во': int(parts[3].split(': ')[1]),
                'Ед.': parts[4].split(': ')[1],
                'Цена': float(parts[5].split(': ')[1].replace('₽', '').strip()),
                'Сумма': float(parts[6].split(': ')[1].replace('₽', '').strip())
            }
            
            # Prepare inline keyboard to edit item details
            keyboard = [
                [InlineKeyboardButton(f"Изменить Товар ({item['Товар']})", callback_data='edit_name')],
                [InlineKeyboardButton(f"Изменить Кол-во ({item['Кол-во']})", callback_data='edit_qty')],
                [InlineKeyboardButton(f"Изменить Цена ({item['Цена']:.2f}₽)", callback_data='edit_price')],
                [InlineKeyboardButton("Готово", callback_data='done_edit')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message with inline keyboard for editing
            await query.message.reply_text(
                "Выберите поле для редактирования:",
                reply_markup=reply_markup
            )
            
            # Store the item data in user_data for further processing
            context.user_data['edit_item'] = item
            
        except Exception as e:
            print(f"Error in item_edit: {e}")
            await query.message.reply_text("Произошла ошибка при редактировании позиции.")
            
    
    @staticmethod
    async def edit_name(update: Update, context: CallbackContext) -> None:
        await update.callback_query.answer()
        # Отправляем сообщение для ввода нового названия товара
        await update.callback_query.message.reply_text("Введите новое название товара:")

        # Устанавливаем состояние редактирования названия товара
        context.user_data['edit_action'] = 'edit_name'
        context.user_data['edit_message_id'] = update.callback_query.message.message_id
    
    
    @staticmethod
    async def edit_qty():
        pass
    
    
    @staticmethod
    async def edit_price():
        pass
    
    @staticmethod
    async def done_edit():
        pass



