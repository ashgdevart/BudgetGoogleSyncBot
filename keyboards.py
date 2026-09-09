from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

CATEGORIES = ["Продукты", "Кафе", "Транспорт", "Развлечения",
              "Жильё", "Здоровье", "Покупки", "Другое"]

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Расход"), KeyboardButton(text="💰 Доход")],
            [KeyboardButton(text="📊 Балансы"), KeyboardButton(text="📜 История")],
            [KeyboardButton(text="❌ Отмена")],
        ], resize_keyboard=True, is_persistent=True)

def category_keyboard():
    rows = [[KeyboardButton(text=x) for x in CATEGORIES[i:i+2]]
            for i in range(0, len(CATEGORIES), 2)]
    rows.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
