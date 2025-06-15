from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_rating_keyboard():
    """Создает клавиатуру с оценками от 1 до 5."""
    keyboard = []
    for i in range(1, 6):
        keyboard.append([InlineKeyboardButton(str(i), callback_data=f"rate_{i}")])
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

def create_confirmation_keyboard():
    """Создает клавиатуру подтверждения."""
    keyboard = [
        [InlineKeyboardButton("Да, отправить", callback_data="confirm_yes")],
        [InlineKeyboardButton("Нет, заполнить заново", callback_data="confirm_no")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_start_keyboard():
    """Создает начальную клавиатуру."""
    keyboard = [[InlineKeyboardButton("Начать опрос", callback_data="start_survey")]]
    return InlineKeyboardMarkup(keyboard) 