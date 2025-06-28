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
    handle_visit_rating,
    handle_yandex_review_done,
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
            VISIT_RATING: [
                CallbackQueryHandler(handle_visit_rating, pattern="^visit_rating_[1-5]$"),
                CallbackQueryHandler(handle_yandex_review_done, pattern="^yandex_review_done$")
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