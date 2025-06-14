import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import *
from keyboards import *
from config import OWNER_CHAT_ID

# Настройка логирования
logger = logging.getLogger(__name__)

# Хранение данных пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start."""
    user = update.effective_user
    user_data[user.id] = {}
    
    welcome_text = (
        "🍽 Добро пожаловать в ресторан FRANK by BASTA!\n\n"
        "Пожалуйста, поделитесь вашими впечатлениями о посещении.\n"
        "Это займет не более 2 минут.\n\n"
        "Начнем?"
    )
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=create_start_keyboard()
    )
    return MAIN_MENU

async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало опроса."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text="Пожалуйста, оцените качество блюд:",
        reply_markup=create_rating_keyboard()
    )
    return FOOD_RATING

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка оценок."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    rating = int(query.data.split("_")[1])
    
    # Определяем текущее состояние и следующее
    current_state = context.user_data.get("current_state", FOOD_RATING)
    if current_state == FOOD_RATING:
        user_data[user_id]["food_rating"] = rating
        next_state = SERVICE_RATING
        next_question = "качество обслуживания"
    elif current_state == SERVICE_RATING:
        user_data[user_id]["service_rating"] = rating
        next_state = ATMOSPHERE_RATING
        next_question = "атмосферу ресторана"
    else:
        user_data[user_id]["atmosphere_rating"] = rating
        next_state = TEXT_REVIEW
        next_question = "написать текстовый отзыв"
    
    context.user_data["current_state"] = next_state
    
    if next_state == TEXT_REVIEW:
        await query.edit_message_text(
            text="Спасибо! Теперь напишите ваш отзыв:"
        )
    else:
        await query.edit_message_text(
            text=f"Спасибо! Теперь оцените {next_question}:",
            reply_markup=create_rating_keyboard()
        )
    
    return next_state

async def handle_text_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка текстового отзыва."""
    user_id = update.effective_user.id
    user_data[user_id]["text_review"] = update.message.text
    
    await update.message.reply_text(
        "Хотите оставить свои контактные данные (имя и телефон)?\n"
        "Это необязательно. Напишите их или отправьте 'нет'."
    )
    return CONTACT_INFO

async def handle_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка контактной информации."""
    user_id = update.effective_user.id
    contact = update.message.text if update.message.text.lower() != "нет" else "не указаны"
    user_data[user_id]["contact_info"] = contact
    
    # Формируем подтверждение
    review = user_data[user_id]
    confirmation_text = (
        "✅ Проверьте ваш отзыв:\n\n"
        f"🍴 Оценка блюд: {review['food_rating']}/5\n"
        f"👨‍🍳 Оценка сервиса: {review['service_rating']}/5\n"
        f"🎭 Оценка атмосферы: {review['atmosphere_rating']}/5\n"
        f"📝 Текстовый отзыв: {review['text_review']}\n"
        f"📱 Контактные данные: {review['contact_info']}\n\n"
        "Все верно?"
    )
    
    await update.message.reply_text(
        text=confirmation_text,
        reply_markup=create_confirmation_keyboard()
    )
    return CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка подтверждения отзыва."""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "confirm_yes":
            user = query.from_user
            review = user_data[user.id]
            
            # Формируем сообщение для владельца
            owner_message = (
                "📩 Новый отзыв о ресторане:\n\n"
                f"👤 От: {user.first_name} {user.last_name or ''} (@{user.username or 'нет'})\n"
                f"🆔 ID: {user.id}\n"
                f"🍴 Оценка блюд: {review['food_rating']}/5\n"
                f"👨‍🍳 Оценка сервиса: {review['service_rating']}/5\n"
                f"🎭 Оценка атмосферы: {review['atmosphere_rating']}/5\n"
                f"📝 Текстовый отзыв:\n{review['text_review']}\n"
                f"📱 Контактные данные: {review['contact_info']}"
            )
            
            try:
                # Отправляем отзыв владельцу
                await context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=owner_message
                )
                
                await query.edit_message_text(
                    text="💖 Спасибо за ваш отзыв! Мы ценим ваше мнение!"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке отзыва владельцу: {e}")
                await query.edit_message_text(
                    text="⚠️ Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже."
                )
        else:
            await query.edit_message_text(
                text="🔁 Давайте начнем опрос заново. Нажмите /start"
            )
        
        # Очищаем данные пользователя
        if user.id in user_data:
            del user_data[user.id]
        if "current_state" in context.user_data:
            del context.user_data["current_state"]
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в handle_confirmation: {e}")
        await query.edit_message_text(
            text="⚠️ Произошла ошибка. Пожалуйста, начните заново /start"
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена опроса."""
    user = update.effective_user
    if user.id in user_data:
        del user_data[user.id]
    if "current_state" in context.user_data:
        del context.user_data["current_state"]
    
    await update.message.reply_text(
        "Опрос отменен. Чтобы начать заново, нажмите /start"
    )
    return ConversationHandler.END 