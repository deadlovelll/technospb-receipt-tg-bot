from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters, CallbackContext

    
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class NewOrderHandler:
    
    @staticmethod
    async def new_order(update: Update, context: CallbackContext, query, ADDING_ITEMS):
        
        context.user_data['items'] = []
        context.user_data['state'] = ADDING_ITEMS
        keyboard = [
            [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # # Print the specific message ID from which to start deletion
        # start_message_id = context.user_data.get('edit_message_id')
        
        # # Get the last known message ID
        # last_message_id = context.user_data.get('last_message_id')
        
        # chat_id = update.callback_query.message.chat.id
        
        # if start_message_id and last_message_id:
        
        #     for i in range(int(start_message_id+1), int(last_message_id)+1):
        #         await context.bot.delete_message(chat_id=chat_id, message_id=i)
        
        start_messge = await query.edit_message_text(
            "Введите данные о позиции в формате:\n"
            "Товар, Кол-во, Цена,\n"
            "Например:\n"
            "Asus ROG Strix, 1, 1200.00\n",
            reply_markup=reply_markup
        )
        
        context.user_data['edit_message_id'] = start_messge.message_id
        
class AddNextItemHandler:
    
    @staticmethod
    async def add_next_item(context: CallbackContext, query, update: Update, ADDING_ITEMS):
        context.user_data['state'] = ADDING_ITEMS
                
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        chat_id = update.callback_query.message.chat.id
        
        if start_message_id and last_message_id:
        
            for i in range(int(start_message_id+1), int(last_message_id)+1):
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
        

        await query.edit_message_text(
            "Позиция Успешно Добавлена ✅\n\n"
            "Введите данные о следующей позиции в формате:\n"
            "Nº, Товар, Кол-во, Ед., Цена, Сумма\n"
            "Например:\n"
            "1, Asus ROG Strix, 1, Шт., 1200.00, 1200.00\n"
        )
        
        for i in range(int(context.user_data['edit_message_id']), int(update.callback_query.message.message_id)):
            print(i)
        
class FinishReceiptHandler:
    
    @staticmethod
    async def finish_receipt(context: CallbackContext, update: Update, ADDING_ITEMS, FINISHED):
        
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        chat_id = update.callback_query.message.chat.id
        
        if start_message_id and last_message_id:
        
            for i in range(int(start_message_id+1), int(last_message_id)+1):
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
    
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
            [InlineKeyboardButton("Сформировать PDF 📑", callback_data='create_pdf')],
            [InlineKeyboardButton("Отменить заказ ❌", callback_data='cancel_order')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(order_summary, reply_markup=reply_markup)
        
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
            
            
class CancelOrderHandler:
    
    @staticmethod
    async def return_to_main_menu(update: Update, context: CallbackContext, keyboard) -> None:

        query = update.callback_query
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        print(start_message_id, last_message_id)
        
        chat_id = update.callback_query.message.chat.id
        
        if start_message_id and last_message_id:
        
            for i in range(int(start_message_id+1), int(last_message_id)+1):
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
        
        await query.edit_message_text(
            "Привет! Я помогу тебе создать PDF с чеком. Выберите действие:",
            reply_markup=reply_markup
        )
        
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
        
class CheckReceiptHandler:
    
    @staticmethod
    async def check_receipt(update: Update, context: CallbackContext, CHOOSING_NEXT) -> None:
        
        # Log current state for debugging
        context.user_data['state']
        
        context.user_data['state'] = CHOOSING_NEXT
        items = context.user_data.get('items', [])
        
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        print(start_message_id, last_message_id)
        
        if start_message_id and last_message_id:
            chat_id = update.callback_query.message.chat_id
            
            for i in range(int(start_message_id)+1, int(last_message_id)+1):
                print(i)
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
        
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
        context.user_data['edit_message_id'] = msg.message_id
        context.user_data['last_message_id'] = None

    @staticmethod
    async def back(update: Update, context: CallbackContext, CHOOSING_NEXT) -> None:
        
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        
        if start_message_id and last_message_id:
            try:
                chat_id = update.callback_query.message.chat_id
                
                for i in range(int(start_message_id), int(last_message_id)+1):
                    print(i)
                    await context.bot.delete_message(chat_id=chat_id, message_id=i)
                
                context.user_data['state'] = CHOOSING_NEXT
                await update.callback_query.answer("Возвращение к добавлению позиций.")
                
            except Exception as e:
                print(f"Error deleting messages: {e}")
        else:
            chat_id = update.callback_query.message.chat_id
            await context.bot.delete_message(chat_id=chat_id, message_id=start_message_id)
            
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
            
class ItemEdition:
    
    @staticmethod
    async def item_edit(update: Update, context: CallbackContext, EDITING_ITEMS) -> None:
        
        context.user_data['state'] = EDITING_ITEMS
        query = update.callback_query
        await query.answer()
        
        try:
            
            start_message_id = context.user_data.get('edit_message_id')
            
            # Get the last known message ID
            last_message_id = context.user_data.get('last_message_id')
            
            chat_id = update.callback_query.message.chat.id
            
            if start_message_id and last_message_id:
        
                for i in range(int(start_message_id+1), int(last_message_id)+1):
                    await context.bot.delete_message(chat_id=chat_id, message_id=i)
            
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
            start_message = await query.message.reply_text(
                "Выберите поле для редактирования:",
                reply_markup=reply_markup
            )
            
            context.user_data['edit_message_id'] = start_message.message_id
            
            # Store the item data in user_data for further processing
            context.user_data['edit_item'] = item
            
            context.user_data['edit_item_no'] = int(parts[1].split(': ')[1])
            
            context.user_data['edit_action'] = 'choosing'
            
        except Exception as e:
            print(f"Error in item_edit: {e}")
            await query.message.reply_text("Произошла ошибка при редактировании позиции.")
            
    
    @staticmethod
    async def edit_name(update: Update, context: CallbackContext, EDITING_ITEMS) -> None:
        
        context.user_data['state'] = EDITING_ITEMS
        
        await update.callback_query.answer()
        
        start_message = await update.callback_query.message.reply_text("Введите новое название товара:")
        
        context.user_data['edit_message_id'] = start_message.message_id

        # Устанавливаем состояние редактирования названия товара
        context.user_data['edit_action'] = 'edit_name'
        
    @staticmethod
    async def edit_name_handler(update: Update, context: CallbackContext) -> None:
        
        # Get the new name from the user's message
        new_name = update.message.text

        # Find the item to update in context.user_data['items']
        items = context.user_data.get('items', [])
        for item in items:
            if item['Nº'] == context.user_data.get('edit_item_no'):
                item['Товар'] = new_name
                break

        # Создаем текст сообщения с информацией о добавленной позиции
        message_text = (
            f"Название позиции изменено:\n"
            f"Nº: {item['Nº']}\n"
            f"Товар: {item['Товар'].split(',')[0]}\n"
            f"Кол-во: {item['Кол-во']}\n"
            f"Ед.: {item['Ед.']}\n"
            f"Цена: {item['Цена']:.2f}₽\n"
            f"Сумма: {item['Сумма']:.2f}₽\n\n"
            "Чтобы добавить следующую позицию, нажмите на соответствующую кнопку."
        )
        
        # Удаление сообщения через 1-2 секунды
        await asyncio.sleep(1)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=int(update.message.message_id)-1)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=int(update.message.message_id)-2)
        
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

        # Clear the edit action state
        context.user_data['edit_action'] = None
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
        context.user_data['edit_item_no'] = None
    
    
    @staticmethod
    async def edit_qty(update: Update, context: CallbackContext, EDITING_ITEMS) -> None:
        
        context.user_data['state'] = EDITING_ITEMS
        
        await update.callback_query.answer()
        # Отправляем сообщение для ввода нового названия товара
        start_message = await update.callback_query.message.reply_text("Введите новое количество товара:")
        
        context.user_data['edit_message_id'] = start_message.message_id

        # Устанавливаем состояние редактирования названия товара
        context.user_data['edit_action'] = 'edit_qty'
        
    
    @staticmethod
    async def edit_qty_handler(update: Update, context: CallbackContext) -> None:
        
        # Get the new name from the user's message
        new_qty = update.message.text
        
        if new_qty.isdigit():
            
            # Find the item to update in context.user_data['items']
            items = context.user_data.get('items', [])
            for item in items:
                if item['Nº'] == context.user_data.get('edit_item_no'):
                    item['Кол-во'] = new_qty
                    item['Сумма'] = int(new_qty)*int(item['Цена'])
                    break

            # Создаем текст сообщения с информацией о добавленной позиции
            message_text = (
                f"Количество позиции изменено:\n"
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
            
            for i in range(int(context.user_data['edit_message_id']), int(update.message.message_id)+1):
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=i)
            
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

            # Clear the edit action state
            context.user_data['edit_action'] = None
            context.user_data['edit_item_no'] = None
            
        else:
            
            await update.message.reply_text("Для ввода допустимы только целочисленные значения.")
            
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
            
    @staticmethod
    async def edit_price(update: Update, context: CallbackContext, EDITING_ITEMS) -> None:
        
        context.user_data['state'] = EDITING_ITEMS
        
        await update.callback_query.answer()
        
        # Отправляем сообщение для ввода нового названия товара
        start_message = await update.callback_query.message.reply_text("Введите новую цену товара (Например: 1200.00):")

        # Устанавливаем состояние редактирования названия товара
        context.user_data['edit_action'] = 'edit_price'
        context.user_data['edit_message_id'] = start_message.message_id
    
    @staticmethod
    async def edit_price_handler(update: Update, context: CallbackContext) -> None:
        
        # Get the new name from the user's message
        new_price = update.message.text
        
        if is_float(new_price):
            
            # Find the item to update in context.user_data['items']
            items = context.user_data.get('items', [])
            for item in items:
                if item['Nº'] == context.user_data.get('edit_item_no'):
                    item['Цена'] = float(new_price)
                    item['Сумма'] = float(new_price)*float(item['Кол-во'])
                    break

            # Создаем текст сообщения с информацией о добавленной позиции
            message_text = (
                f"Цена позиции изменена:\n"
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
            for i in range(int(context.user_data['edit_message_id']), int(update.message.message_id)+1):
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=i)
            
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

            # Clear the edit action state
            context.user_data['edit_action'] = None
            context.user_data['edit_item_no'] = None
            
        else:
            
            await update.message.reply_text("Для ввода допустимы только целочисленные значения.")
            
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
            
    @staticmethod
    async def done_edit(update: Update, context: CallbackContext) -> None:
        
        # Print the specific message ID from which to start deletion
        start_message_id = context.user_data.get('edit_message_id')
        
        # Get the last known message ID
        last_message_id = context.user_data.get('last_message_id')
        
        if start_message_id and last_message_id:
            chat_id = update.callback_query.message.chat_id
            
            for i in range(int(start_message_id), int(last_message_id)+1):
                await context.bot.delete_message(chat_id=chat_id, message_id=i)
                
        else:
            chat_id = update.callback_query.message.chat_id
            
            await context.bot.delete_message(chat_id=chat_id, message_id=start_message_id)
            
        context.user_data['edit_message_id'] = None
        context.user_data['last_message_id'] = None
        



