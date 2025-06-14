# import logging
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     CallbackQueryHandler,
#     ContextTypes,
#     ConversationHandler,
# )
# import asyncio
# import telegram

# # Настройка логирования
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # Конфигурация
# OWNER_CHAT_ID = "575503615"  # Замените на ваш ID
# BOT_TOKEN = "7549779158:AAHdDwo1AhMmLz7Oyj0-xKdpAKMxji7pojQ"  # Замените на токен бота

# # Состояния для разговора
# (
#     MAIN_MENU,
#     FOOD_RATING,
#     SERVICE_RATING,
#     ATMOSPHERE_RATING,
#     TEXT_REVIEW,
#     CONTACT_INFO,
#     CONFIRMATION,
# ) = range(7)

# # Хранение временных данных
# user_data = {}

# def create_rating_keyboard():
#     """Создает корректную клавиатуру для оценки по 5-балльной шкале."""
#     buttons = [[InlineKeyboardButton(str(i), callback_data=f"rate_{i}")] 
#         for i in range(1, 6)
#     ]
#     return InlineKeyboardMarkup(buttons)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Начало взаимодействия с ботом."""
#     try:
#         user = update.message.from_user
#         logger.info(f"Пользователь {user.id} начал опрос.")
        
#         # Очищаем предыдущие данные пользователя
#         user_data[user.id] = {}

#         welcome_text = (
#             "🍽 Добро пожаловать в ресторан FRANK by BASTA!\n\n"
#             "Пожалуйста, поделитесь вашими впечатлениями о посещении.\n"
#             "Это займет не более 2 минут.\n\n"
#             "Начнем?"
#         )
        
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("Начать опрос", callback_data="start_survey")]
#         ])
        
#         await update.message.reply_text(
#             text=welcome_text,
#             reply_markup=keyboard
#         )
#         return MAIN_MENU
        
#     except Exception as e:
#         logger.error(f"Ошибка в start: {e}", exc_info=True)
#         await update.message.reply_text(
#             "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
#         )
#         return -1

# async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Начало опроса."""
#     query = update.callback_query
#     await query.answer()
    
#     try:
#         await asyncio.sleep(0.3)
        
#         # Создаем новую клавиатуру для оценки
#         keyboard = create_rating_keyboard()
        
#         await query.edit_message_text(
#             text="Пожалуйста, оцените качество блюд:",
#             reply_markup=keyboard
#         )
#         return FOOD_RATING
        
#     except Exception as e:
#         logger.error(f"Ошибка в start_survey: {e}", exc_info=True)
#         await query.edit_message_text(
#             "⚠️ Произошла ошибка. Пожалуйста, начните заново /start"
#         )
#         return -1

# async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Обработка оценок."""
#     query = update.callback_query
#     await query.answer()
    
#     user_id = query.from_user.id
#     rating = int(query.data.split("_")[1])
    
#     # Определяем текущее состояние и следующее
#     current_state = context.user_data.get("current_state", FOOD_RATING)
#     if current_state == FOOD_RATING:
#         user_data[user_id]["food_rating"] = rating
#         next_state = SERVICE_RATING
#         next_question = "качество обслуживания"
#     elif current_state == SERVICE_RATING:
#         user_data[user_id]["service_rating"] = rating
#         next_state = ATMOSPHERE_RATING
#         next_question = "атмосферу ресторана"
#     else:
#         user_data[user_id]["atmosphere_rating"] = rating
#         next_state = TEXT_REVIEW
#         next_question = "написать текстовый отзыв"
    
#     context.user_data["current_state"] = next_state
    
#     if next_state == TEXT_REVIEW:
#         await query.edit_message_text(
#             text="Спасибо! Теперь напишите ваш отзыв:"
#         )
#     else:
#         await query.edit_message_text(
#             text=f"Спасибо! Теперь оцените {next_question}:",
#             reply_markup=create_rating_keyboard()
#         )
    
#     return next_state

# async def handle_text_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Обработка текстового отзыва."""
#     try:
#         user = update.message.from_user
#         user_data[user.id]["text_review"] = update.message.text
        
#         await update.message.reply_text(
#             "📝 Хотите оставить свои контактные данные (имя и телефон или email)?\n"
#             "Это необязательно. Напишите их или отправьте 'нет'."
#         )
#         return CONTACT_INFO
        
#     except Exception as e:
#         logger.error(f"Ошибка в text_review: {e}", exc_info=True)
#         await update.message.reply_text(
#             "⚠️ Произошла ошибка. Пожалуйста, попробуйте ещё раз."
#         )
#         return TEXT_REVIEW

# async def handle_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Обработка контактных данных."""
#     try:
#         user = update.message.from_user
#         contact = update.message.text if update.message.text.lower() != "нет" else "не указаны"
#         user_data[user.id]["contact_info"] = contact
        
#         # Формируем подтверждение
#         review_data = user_data[user.id]
#         confirmation_text = (
#             "✅ Проверьте ваш отзыв:\n\n"
#             f"🍴 Оценка блюд: {review_data['food_rating']}/5\n"
#             f"👨‍🍳 Оценка сервиса: {review_data['service_rating']}/5\n"
#             f"🎭 Оценка атмосферы: {review_data['atmosphere_rating']}/5\n"
#             f"📝 Текстовый отзыв: {review_data['text_review']}\n"
#             f"📱 Контактные данные: {review_data.get('contact_info', 'не указаны')}\n\n"
#             "Все верно?"
#         )
        
#         keyboard = InlineKeyboardMarkup([
#             [InlineKeyboardButton("Да, отправить", callback_data="confirm_yes")],
#             [InlineKeyboardButton("Нет, заполнить заново", callback_data="confirm_no")]
#         ])
        
#         await update.message.reply_text(
#             text=confirmation_text,
#             reply_markup=keyboard
#         )
#         return CONFIRMATION
        
#     except Exception as e:
#         logger.error(f"Ошибка в contact_info: {e}", exc_info=True)
#         await update.message.reply_text(
#             "⚠️ Произошла ошибка. Пожалуйста, попробуйте ещё раз."
#         )
#         return CONTACT_INFO

# async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Обработка подтверждения отзыва."""
#     query = update.callback_query
#     await query.answer()
    
#     try:
#         if query.data == "confirm_yes":
#             user = query.from_user
#             review = user_data[user.id]
            
#             # Формируем сообщение для владельца
#             owner_message = (
#                 "📩 Новый отзыв о ресторане:\n\n"
#                 f"👤 От: {user.first_name} {user.last_name or ''} (@{user.username or 'нет'})\n"
#                 f"🆔 ID: {user.id}\n"
#                 f"🍴 Оценка блюд: {review['food_rating']}/5\n"
#                 f"👨‍🍳 Оценка сервиса: {review['service_rating']}/5\n"
#                 f"🎭 Оценка атмосферы: {review['atmosphere_rating']}/5\n"
#                 f"📝 Текстовый отзыв:\n{review['text_review']}\n"
#                 f"📱 Контактные данные: {review['contact_info']}"
#             )
            
#             try:
#                 # Отправляем отзыв владельцу
#                 await context.bot.send_message(
#                     chat_id=OWNER_CHAT_ID,
#                     text=owner_message
#                 )
                
#                 await query.edit_message_text(
#                     text="💖 Спасибо за ваш отзыв! Мы ценим ваше мнение!"
#                 )
#             except Exception as e:
#                 logger.error(f"Ошибка при отправке отзыва владельцу: {e}")
#                 await query.edit_message_text(
#                     text="⚠️ Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже."
#                 )
#         else:
#             await query.edit_message_text(
#                 text="🔁 Давайте начнем опрос заново. Нажмите /start"
#             )
        
#         # Очищаем данные пользователя
#         if user.id in user_data:
#             del user_data[user.id]
#         if "current_state" in context.user_data:
#             del context.user_data["current_state"]
        
#         return ConversationHandler.END
        
#     except Exception as e:
#         logger.error(f"Ошибка в handle_confirmation: {e}")
#         await query.edit_message_text(
#             text="⚠️ Произошла ошибка. Пожалуйста, начните заново /start"
#         )
#         return ConversationHandler.END

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Отмена опроса."""
#     user = update.effective_user
#     if user.id in user_data:
#         del user_data[user.id]
#     if "current_state" in context.user_data:
#         del context.user_data["current_state"]
    
#     await update.message.reply_text(
#         "Опрос отменен. Чтобы начать заново, нажмите /start"
#     )
#     return -1

# async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Глобальный обработчик ошибок."""
#     error = context.error
#     logger.error("Ошибка: %s", error, exc_info=True)
    
#     # Игнорируем ошибку "Message is not modified"
#     if isinstance(error, telegram.error.BadRequest) and "Message is not modified" in str(error):
#         return
    
#     if update and isinstance(update, Update):
#         if update.callback_query:
#             await update.callback_query.message.reply_text(
#                 "⚠️ Произошла ошибка. Пожалуйста, начните заново /start"
#             )
#         elif update.message:
#             await update.message.reply_text(
#                 "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже."
#             )

# def main() -> None:
#     """Запуск бота."""
#     application = Application.builder().token(BOT_TOKEN).build()
    
#     # Создаем обработчик разговора
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", start)],
#         states={
#             MAIN_MENU: [
#                 CallbackQueryHandler(start_survey, pattern="^start_survey$")
#             ],
#             FOOD_RATING: [
#                 CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
#             ],
#             SERVICE_RATING: [
#                 CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
#             ],
#             ATMOSPHERE_RATING: [
#                 CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
#             ],
#             TEXT_REVIEW: [
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_review)
#             ],
#             CONTACT_INFO: [
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_info)
#             ],
#             CONFIRMATION: [
#                 CallbackQueryHandler(handle_confirmation, pattern="^confirm_(yes|no)$")
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )
    
#     # Добавляем обработчик разговора
#     application.add_handler(conv_handler)
    
#     # Обработчик ошибок
#     application.add_error_handler(error_handler)
    
#     # Запускаем бота
#     application.run_polling()

# if __name__ == "__main__":
#     main()