import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация бота
OWNER_CHAT_ID = str(os.getenv("OWNER_CHAT_ID", "-4937658771"))  # ID группы для получения отзывов
BOT_TOKEN = os.getenv("BOT_TOKEN", "7549779158:AAHdDwo1AhMmLz7Oyj0-xKdpAKMxji7pojQ") 