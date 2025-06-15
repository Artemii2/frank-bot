import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
)
from config import BOT_TOKEN
from states import *
from handlers import (
    start,
    start_survey,
    handle_first_visit,
    handle_rating,
    handle_will_visit_again,
    handle_text_review,
    handle_contact_info,
    handle_confirmation,
    cancel,
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Запуск бота."""
    # Создаем Updater и передаем ему токен бота
    updater = Updater(BOT_TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(start_survey, pattern="^start_survey$")
            ],
            FIRST_VISIT: [
                CallbackQueryHandler(handle_first_visit, pattern="^answer_(yes|no)$")
            ],
            FOOD_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rating_[1-5]$")
            ],
            SERVICE_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rating_[1-5]$")
            ],
            ATMOSPHERE_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rating_[1-5]$")
            ],
            WILL_VISIT_AGAIN: [
                CallbackQueryHandler(handle_will_visit_again, pattern="^answer_(yes|no)$")
            ],
            TEXT_REVIEW: [
                MessageHandler(Filters.text & ~Filters.command, handle_text_review)
            ],
            CONTACT_INFO: [
                MessageHandler(Filters.text & ~Filters.command, handle_contact_info)
            ],
            CONFIRMATION: [
                CallbackQueryHandler(handle_confirmation, pattern="^confirm_(yes|no)$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Добавляем обработчик разговора
    dispatcher.add_handler(conv_handler)
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main() 