import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from states import *
from keyboards import *
from config import OWNER_CHAT_ID

# Настройка логирования
logger = logging.getLogger(__name__)

# Хранение данных пользователей
user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    """Обработчик команды /start."""
    user = update.effective_user
    user_data[user.id] = {}
    
    welcome_text = (
        "🍽 Добро пожаловать в ресторан FRANK by BASTA!\n\n"
        "Пожалуйста, поделитесь вашими впечатлениями о посещении.\n"
        "Это займет не более 2 минут.\n\n"
        "Начнем?"
    )
    
    update.message.reply_text(
        text=welcome_text,
        reply_markup=create_start_keyboard()
    )
    return MAIN_MENU

def start_survey(update: Update, context: CallbackContext) -> int:
    """Начало опроса."""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        text="Вы первый раз у нас в гостях?",
        reply_markup=create_yes_no_keyboard()
    )
    return FIRST_VISIT

def handle_first_visit(update: Update, context: CallbackContext) -> int:
    """Обработка ответа о первом посещении."""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    # Инициализируем данные пользователя, если их еще нет
    if user_id not in user_data:
        user_data[user_id] = {}
    
    is_first_visit = query.data == "answer_yes"
    user_data[user_id]["first_visit"] = "Да" if is_first_visit else "Нет"
    
    query.edit_message_text(
        text="Как вам наши блюда?",
        reply_markup=create_rating_keyboard()
    )
    return FOOD_RATING

def handle_rating(update: Update, context: CallbackContext) -> int:
    """Обработка оценок."""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    # Инициализируем данные пользователя, если их еще нет
    if user_id not in user_data:
        user_data[user_id] = {}
    
    rating = int(query.data.split("_")[1])
    
    # Определяем текущее состояние и следующее
    current_state = context.user_data.get("current_state", FOOD_RATING)
    if current_state == FOOD_RATING:
        user_data[user_id]["food_rating"] = rating
        next_state = SERVICE_RATING
        next_question = "наш сервис"
    elif current_state == SERVICE_RATING:
        user_data[user_id]["service_rating"] = rating
        next_state = ATMOSPHERE_RATING
        next_question = "общая атмосфера"
    else:
        user_data[user_id]["atmosphere_rating"] = rating
        next_state = WILL_VISIT_AGAIN
        next_question = "посетите ли вы нас еще раз"
    
    context.user_data["current_state"] = next_state
    
    if next_state == WILL_VISIT_AGAIN:
        query.edit_message_text(
            text="Посетите ли вы нас еще раз?",
            reply_markup=create_yes_no_keyboard()
        )
    else:
        query.edit_message_text(
            text=f"Как вам {next_question}?",
            reply_markup=create_rating_keyboard()
        )
    
    return next_state

def handle_will_visit_again(update: Update, context: CallbackContext) -> int:
    """Обработка ответа о повторном посещении."""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    # Инициализируем данные пользователя, если их еще нет
    if user_id not in user_data:
        user_data[user_id] = {}
    
    will_visit = query.data == "answer_yes"
    user_data[user_id]["will_visit_again"] = "Да" if will_visit else "Нет"
    
    query.edit_message_text(
        text="Пожалуйста, напишите ваш отзыв в свободной форме:"
    )
    return TEXT_REVIEW

def handle_text_review(update: Update, context: CallbackContext) -> int:
    """Обработка текстового отзыва."""
    user_id = update.effective_user.id
    # Инициализируем данные пользователя, если их еще нет
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]["text_review"] = update.message.text
    
    update.message.reply_text(
        "Хотите оставить свои контактные данные (имя и телефон)?\n"
        "Это необязательно. Напишите их или отправьте 'нет'."
    )
    return CONTACT_INFO

def handle_contact_info(update: Update, context: CallbackContext) -> int:
    """Обработка контактной информации."""
    user_id = update.effective_user.id
    # Инициализируем данные пользователя, если их еще нет
    if user_id not in user_data:
        user_data[user_id] = {}
    
    contact = update.message.text.strip()  # Убираем лишние пробелы
    user_data[user_id]["contact_info"] = contact if contact.lower() != "нет" else "не указаны"
    
    # Формируем подтверждение
    review = user_data[user_id]
    confirmation_text = (
        "✅ Проверьте ваш отзыв:\n\n"
        f"👥 Первый визит: {review['first_visit']}\n"
        f"🍴 Оценка блюд: {review['food_rating']}/5\n"
        f"👨‍🍳 Оценка сервиса: {review['service_rating']}/5\n"
        f"🎭 Оценка атмосферы: {review['atmosphere_rating']}/5\n"
        f"🔄 Посещение снова: {review['will_visit_again']}\n"
        f"📝 Текстовый отзыв: {review['text_review']}\n"
        f"📱 Контактные данные: {review['contact_info']}\n\n"
        "Все верно?"
    )
    
    update.message.reply_text(
        text=confirmation_text,
        reply_markup=create_confirmation_keyboard()
    )
    return CONFIRMATION

def handle_confirmation(update: Update, context: CallbackContext) -> int:
    """Обработка подтверждения отзыва."""
    query = update.callback_query
    query.answer()
    
    try:
        if query.data == "confirm_yes":
            user = query.from_user
            review = user_data[user.id]
            
            # Формируем сообщение для группы
            owner_message = (
                "📩 Новый отзыв о ресторане:\n\n"
                f"👤 От: {user.first_name} {user.last_name or ''} (@{user.username or 'нет'})\n"
                f"🆔 ID: {user.id}\n"
                f"👥 Первый визит: {review['first_visit']}\n"
                f"🍴 Оценка блюд: {review['food_rating']}/5\n"
                f"👨‍🍳 Оценка сервиса: {review['service_rating']}/5\n"
                f"🎭 Оценка атмосферы: {review['atmosphere_rating']}/5\n"
                f"🔄 Посещение снова: {review['will_visit_again']}\n"
                f"📝 Текстовый отзыв:\n{review['text_review']}\n"
                f"📱 Контактные данные: {review['contact_info']}"
            )
            
            try:
                # Отправляем отзыв в группу
                logger.info(f"Attempting to send message to group {OWNER_CHAT_ID}")
                context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=owner_message,
                    parse_mode='HTML'
                )
                logger.info("Message successfully sent to group")
                
                query.edit_message_text(
                    text="💖 Спасибо за ваш отзыв! Мы ценим ваше мнение!"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке отзыва в группу: {str(e)}")
                logger.error(f"ID группы: {OWNER_CHAT_ID}")
                query.edit_message_text(
                    text="⚠️ Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже."
                )
        else:
            # Очищаем данные пользователя
            if query.from_user.id in user_data:
                del user_data[query.from_user.id]
            if "current_state" in context.user_data:
                del context.user_data["current_state"]
            
            # Начинаем опрос заново
            query.edit_message_text(
                text="Вы первый раз у нас в гостях?",
                reply_markup=create_yes_no_keyboard()
            )
            return FIRST_VISIT
        
        # Очищаем данные пользователя
        if query.from_user.id in user_data:
            del user_data[query.from_user.id]
        if "current_state" in context.user_data:
            del context.user_data["current_state"]
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_confirmation: {str(e)}")
        query.edit_message_text(
            text="⚠️ Произошла ошибка. Пожалуйста, начните заново /start"
        )
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена опроса."""
    user = update.effective_user
    if user.id in user_data:
        del user_data[user.id]
    if "current_state" in context.user_data:
        del context.user_data["current_state"]
    
    update.message.reply_text(
        "Опрос отменен. Чтобы начать заново, нажмите /start"
    )
    return ConversationHandler.END 