from aiogram.fsm.state import State, StatesGroup

class ExpenseStates(StatesGroup):
    waiting_category = State()
    waiting_amount = State()
    waiting_note = State()

class IncomeStates(StatesGroup):
    waiting_amount = State()
    waiting_note = State()
