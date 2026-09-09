# Family Budget Bot

Готовый Telegram-бот для двух пользователей с общей Google Sheets базой.

## Возможности
- whitelist из двух Telegram ID;
- расходы по категориям;
- доходы;
- комментарии;
- история последних 10 операций;
- месячные бюджеты;
- автоматический расчёт остатка бюджета;
- Railway/GitHub-ready.

## Google Sheets
Бот автоматически создаёт листы `Transactions`, `Budgets`, `Users`.
В `Budgets` внеси категории и лимиты, например:

Продукты | 500
Кафе | 200
Транспорт | 150
Развлечения | 200
Жильё | 1000
Здоровье | 100
Покупки | 200
Другое | 150

Service Account должен иметь Editor-доступ к таблице.

## Railway Variables
Добавь:
- BOT_TOKEN
- SPREADSHEET_ID
- GOOGLE_CREDENTIALS_JSON
- ALLOWED_USER_IDS
- CURRENCY=€

Start Command: `python bot.py`

Не загружай `.env`, `credentials.json` и токены в GitHub.
