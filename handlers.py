import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from states import *
from keyboards import *
from config import OWNER_CHAT_ID

YANDEX_REVIEW_URL = "https://yandex.ru/maps/213/moscow/?add-review=true&indoorLevel=0&ll=37.638309%2C55.730340&mode=poi&poi%5Bpoint%5D=37.637890%2C55.730310&poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D223077694891&tab=reviews&z=19.15"

# Настройка логирования
logger = logging.getLogger(__name__)

# Хранение данных пользователей
user_data = {}

def check_group_access(bot, chat_id):
    """Проверяет доступность группы для бота."""
    try:
        chat = bot.get_chat(chat_id)
        logger.info(f"Группа доступна: {chat.title} (ID: {chat_id})")
        return True
    except Exception as e:
        logger.error(f"Ошибка доступа к группе {chat_id}: {str(e)}")
        return False

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
        text="Оцените свой визит по 5-балльной шкале:",
        reply_markup=create_visit_rating_keyboard()
    )
    return VISIT_RATING

def handle_visit_rating(update: Update, context: CallbackContext) -> int:
    """Обработка оценки визита."""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    rating = int(query.data.split("_")[2])
    user_data[user_id]["visit_rating"] = rating
    if rating >= 4:
        user = query.from_user
        # Проверяем доступность группы перед отправкой
        if check_group_access(context.bot, OWNER_CHAT_ID):
            try:
                context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=f"✅ Гость {user.first_name} {user.last_name or ''} (@{user.username or 'нет'}) сообщил, что оставил отзыв на Яндексе!"
                )
                logger.info("Уведомление о яндекс-отзыве отправлено успешно")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления о яндекс-отзыве: {str(e)}")
        else:
            logger.error(f"Группа {OWNER_CHAT_ID} недоступна для бота")
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Оставить отзыв на Яндексе", url=YANDEX_REVIEW_URL)]
        ])
        query.edit_message_text(
            text="Спасибо за высокую оценку! Пожалуйста, оставьте отзыв на Яндексе:",
            reply_markup=keyboard
        )
        if user_id in user_data:
            del user_data[user_id]
        return ConversationHandler.END
    else:
        query.edit_message_text(
            text="Пожалуйста, напишите ваш отзыв в свободной форме:"
        )
        return TEXT_REVIEW

def handle_yandex_review_done(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user = query.from_user
    # Уведомление в группу/админу
    try:
        context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=f"✅ Гость {user.first_name} {user.last_name or ''} (@{user.username or 'нет'}) сообщил, что оставил отзыв на Яндексе!"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления о яндекс-отзыве: {str(e)}")
    query.edit_message_text(
        text="Спасибо, что поделились своим мнением на Яндексе! Нам это очень важно!"
    )
    return ConversationHandler.END

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
        f"⭐️ Оценка визита: {review['visit_rating']}/5\n"
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
                f"⭐️ Оценка визита: {review['visit_rating']}/5\n"
                f"📝 Текстовый отзыв:\n{review['text_review']}\n"
                f"📱 Контактные данные: {review['contact_info']}"
            )
            
            try:
                # Отправляем отзыв в группу
                logger.info(f"Attempting to send message to group {OWNER_CHAT_ID} (type: {type(OWNER_CHAT_ID)})")
                logger.info(f"Message content: {owner_message}")
                
                # Проверяем доступность группы перед отправкой
                if check_group_access(context.bot, OWNER_CHAT_ID):
                    context.bot.send_message(
                        chat_id=OWNER_CHAT_ID,
                        text=owner_message,
                        parse_mode='HTML'
                    )
                    logger.info("Message successfully sent to group")
                    # Отправляем картинку с благодарностью по URL
                    context.bot.send_photo(
                        chat_id=query.from_user.id,
                        photo="https://downloader.disk.yandex.ru/preview/0c87205a937244ea6a8fc5922f23b0509480148a7623eca8d9aa768eaa88d0fe/68635352/DQPz_uzFBQFbC85Azw-c2xGnqlheV9deujryIfiG6pN0Cq-APupSFdcd7maJCLF8H50_LYGaZ0SRIP2e-6HsuA%3D%3D?uid=0&filename=a8d5e7c2-3262-4b5e-b0b2-a2c654b38a89.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=0&tknv=v3&size=2048x2048",
                        caption="💖 Спасибо за ваш отзыв! Мы ценим ваше мнение!"
                    )
                else:
                    logger.error(f"Группа {OWNER_CHAT_ID} недоступна для бота")
                    query.edit_message_text(
                        text="⚠️ Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже."
                    )
            except Exception as e:
                logger.error(f"Ошибка при отправке отзыва в группу: {str(e)}")
                logger.error(f"ID группы: {OWNER_CHAT_ID} (type: {type(OWNER_CHAT_ID)})")
                logger.error(f"Тип ошибки: {type(e).__name__}")
                query.edit_message_text(
                    text="⚠️ Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте позже."
                )
        else:
            # Очищаем данные пользователя
            if query.from_user.id in user_data:
                del user_data[query.from_user.id]
            
            # Начинаем опрос заново
            query.edit_message_text(
                text="Оцените свой визит по 5-балльной шкале:",
                reply_markup=create_visit_rating_keyboard()
            )
            return VISIT_RATING
        
        # Очищаем данные пользователя
        if query.from_user.id in user_data:
            del user_data[query.from_user.id]
        
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
    
    update.message.reply_text(
        "Опрос отменен. Чтобы начать заново, нажмите /start"
    )
    return ConversationHandler.END 