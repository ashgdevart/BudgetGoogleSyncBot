import asyncio
import logging
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import get_config
from keyboards import CATEGORIES, main_keyboard, category_keyboard
from sheets import Sheets
from states import ExpenseStates, IncomeStates

logging.basicConfig(level=logging.INFO)
config = get_config()
sheets = Sheets(config.spreadsheet_id)
router = Router()

def allowed(m): return m.from_user and m.from_user.id in config.allowed_user_ids
def name(m): return m.from_user.full_name
def amount(text):
    try:
        x = Decimal(text.strip().replace(" ","").replace(",", "."))
        return x.quantize(Decimal("0.01")) if x > 0 else None
    except (InvalidOperation, ValueError):
        return None

async def denied(m):
    await m.answer("⛔ Доступ запрещён.")

@router.message(Command("start"))
async def start(m: Message):
    if not allowed(m): return await denied(m)
    sheets.register_user(m.from_user.id, name(m))
    await m.answer("Привет! 👋 Семейный бюджет готов.", reply_markup=main_keyboard())

@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cancel(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    await state.clear()
    await m.answer("Отменено.", reply_markup=main_keyboard())

@router.message(F.text == "➕ Расход")
async def expense_start(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    await state.set_state(ExpenseStates.waiting_category)
    await m.answer("Выбери категорию:", reply_markup=category_keyboard())

@router.message(ExpenseStates.waiting_category)
async def expense_category(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    if m.text not in CATEGORIES:
        return await m.answer("Выбери категорию кнопкой.")
    await state.update_data(category=m.text)
    await state.set_state(ExpenseStates.waiting_amount)
    await m.answer("Введи сумму, например 12.50", reply_markup=main_keyboard())

@router.message(ExpenseStates.waiting_amount)
async def expense_amount(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    x = amount(m.text or "")
    if x is None: return await m.answer("Нужна положительная сумма, например 12.50")
    await state.update_data(amount=str(x))
    await state.set_state(ExpenseStates.waiting_note)
    await m.answer("Комментарий? Напиши его или отправь -")

@router.message(ExpenseStates.waiting_note)
async def expense_note(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    d = await state.get_data()
    note = "" if (m.text or "").strip() == "-" else (m.text or "").strip()
    sheets.add_transaction(m.from_user.id, name(m), "expense", d["category"], d["amount"], note)
    await state.clear()
    await m.answer(f"✅ Расход: {d['amount']} {config.currency} — {d['category']}",
                   reply_markup=main_keyboard())
    await send_balances(m)

@router.message(F.text == "💰 Доход")
async def income_start(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    await state.set_state(IncomeStates.waiting_amount)
    await m.answer("Введи сумму дохода:")

@router.message(IncomeStates.waiting_amount)
async def income_amount(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    x = amount(m.text or "")
    if x is None: return await m.answer("Нужна положительная сумма.")
    await state.update_data(amount=str(x))
    await state.set_state(IncomeStates.waiting_note)
    await m.answer("Комментарий? Напиши его или отправь -")

@router.message(IncomeStates.waiting_note)
async def income_note(m: Message, state: FSMContext):
    if not allowed(m): return await denied(m)
    d = await state.get_data()
    note = "" if (m.text or "").strip() == "-" else (m.text or "").strip()
    sheets.add_transaction(m.from_user.id, name(m), "income", "Доход", d["amount"], note)
    await state.clear()
    await m.answer(f"✅ Доход: {d['amount']} {config.currency}", reply_markup=main_keyboard())

@router.message(F.text == "📊 Балансы")
async def balances(m: Message):
    if not allowed(m): return await denied(m)
    await send_balances(m)

async def send_balances(m):
    month = datetime.now().strftime("%Y-%m")
    spent = defaultdict(Decimal)
    income = Decimal("0")
    for r in sheets.transactions_all():
        if not str(r.get("Date","")).startswith(month): continue
        x = Decimal(str(r.get("Amount","0")).replace(",", "."))
        if r.get("Type") == "expense": spent[r.get("Category","Другое")] += x
        elif r.get("Type") == "income": income += x
    budgets = {k: Decimal(str(v)) for k,v in sheets.budgets_all().items()}
    cats = set(budgets) | set(spent)
    lines = ["📊 <b>Бюджет за текущий месяц</b>", ""]
    for cat in sorted(cats):
        left = budgets.get(cat, Decimal("0")) - spent[cat]
        lines.append(f"• {cat}: {left:+.2f} {config.currency} (потрачено {spent[cat]:.2f})")
    lines += ["", f"💰 Доходы: {income:.2f} {config.currency}"]
    await m.answer("\n".join(lines), reply_markup=main_keyboard())

@router.message(F.text == "📜 История")
async def history(m: Message):
    if not allowed(m): return await denied(m)
    rows = sheets.transactions_all()[-10:][::-1]
    if not rows: return await m.answer("История пока пустая.")
    lines = ["📜 <b>Последние операции</b>", ""]
    for r in rows:
        icon = "🔴" if r.get("Type") == "expense" else "🟢"
        note = f" — {r.get('Note')}" if r.get("Note") else ""
        lines.append(f"{icon} {r.get('Date')} | {r.get('Category')} | {r.get('Amount')} {config.currency}{note}")
    await m.answer("\n".join(lines), reply_markup=main_keyboard())

@router.message()
async def unknown(m: Message):
    if not allowed(m): return await denied(m)
    await m.answer("Используй кнопки меню.", reply_markup=main_keyboard())

async def main():
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
