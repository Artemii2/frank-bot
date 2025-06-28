from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def create_start_keyboard():
    """Создает клавиатуру для начала опроса."""
    keyboard = [
        [InlineKeyboardButton("Начать опрос", callback_data="start_survey")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_yes_no_keyboard():
    """Создает клавиатуру с вариантами Да/Нет."""
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="answer_yes"),
            InlineKeyboardButton("Нет", callback_data="answer_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_visit_rating_keyboard():
    """Создает клавиатуру с оценками визита от 1 до 5."""
    keyboard = [
        [
            InlineKeyboardButton(str(i), callback_data=f"visit_rating_{i}")
            for i in range(1, 6)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_confirmation_keyboard():
    """Создает клавиатуру для подтверждения отзыва."""
    keyboard = [
        [
            InlineKeyboardButton("Да, все верно", callback_data="confirm_yes"),
            InlineKeyboardButton("Заполнить заново", callback_data="confirm_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard) 