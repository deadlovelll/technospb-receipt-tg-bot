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
            "Nº, Товар, Кол-во, Ед., Цена, Сумма\n"
            "Например:\n"
            "1, Asus ROG Strix, 1, Шт., 1200.00, 1200.00\n",
            reply_markup=reply_markup
        )
        
class AddNextItemHandler:
    
    @staticmethod
    async def add_next_item(context: CallbackContext, query, ADDING_ITEMS):
        context.user_data['state'] = ADDING_ITEMS

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
    async def item_edit(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()
        
        print(query)

        try:
            # Extract item index from callback data
            item_index = int(query.data.split('_')[-1])
            items = context.user_data.get('items', [])

            if item_index < len(items):
                item = items[item_index]
                edit_message = (
                    f"Редактирование позиции:\n"
                    f"Товар: {item['Товар']}\n"
                    f"Количество: {item['Кол-во']}\n"
                    f"Единица измерения: {item['Ед.']}\n"
                    f"Цена: {item['Цена']}\n"
                    f"Сумма: {item['Сумма']}\n"
                    "\nВведите новые данные в формате:\n"
                    "Товар, Количество, Единица измерения, Цена"
                )
                context.user_data['editing_item_index'] = item_index
                await query.message.reply_text(edit_message)
            else:
                await query.message.reply_text("Неверный индекс позиции.")
        except (IndexError, ValueError):
            await query.message.reply_text("Ошибка в обработке команды редактирования.")
