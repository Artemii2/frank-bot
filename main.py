import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
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
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем обработчик разговора
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
                CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
            ],
            SERVICE_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
            ],
            ATMOSPHERE_RATING: [
                CallbackQueryHandler(handle_rating, pattern="^rate_[1-5]$")
            ],
            WILL_VISIT_AGAIN: [
                CallbackQueryHandler(handle_will_visit_again, pattern="^answer_(yes|no)$")
            ],
            TEXT_REVIEW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_review)
            ],
            CONTACT_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_info)
            ],
            CONFIRMATION: [
                CallbackQueryHandler(handle_confirmation, pattern="^confirm_(yes|no)$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Добавляем обработчик разговора
    application.add_handler(conv_handler)
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main() 