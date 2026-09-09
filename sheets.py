from datetime import datetime
import gspread
from config import google_credentials

TRANSACTION_HEADERS = ["ID","Date","Telegram ID","User","Type","Category","Amount","Note"]

class Sheets:
    def __init__(self, spreadsheet_id):
        gc = gspread.authorize(google_credentials())
        self.book = gc.open_by_key(spreadsheet_id)
        self.transactions = self._sheet("Transactions")
        self.budgets = self._sheet("Budgets")
        self.users = self._sheet("Users")
        self._headers()

    def _sheet(self, name):
        try:
            return self.book.worksheet(name)
        except gspread.WorksheetNotFound:
            return self.book.add_worksheet(title=name, rows=1000, cols=20)

    def _headers(self):
        if not self.transactions.get_all_values():
            self.transactions.append_row(TRANSACTION_HEADERS)
        if not self.budgets.get_all_values():
            self.budgets.append_row(["Category","Monthly Budget"])
        if not self.users.get_all_values():
            self.users.append_row(["Telegram ID","Name"])

    def register_user(self, uid, name):
        rows = self.users.get_all_values()
        for i, row in enumerate(rows[1:], 2):
            if row and row[0] == str(uid):
                self.users.update_cell(i, 2, name)
                return
        self.users.append_row([str(uid), name])

    def add_transaction(self, uid, name, kind, category, amount, note):
        self.transactions.append_row([
            datetime.now().strftime("%Y%m%d%H%M%S%f"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(uid), name, kind, category, str(amount), note
        ])

    def transactions_all(self):
        return self.transactions.get_all_records()

    def budgets_all(self):
        result = {}
        for row in self.budgets.get_all_records():
            cat = str(row.get("Category","")).strip()
            if not cat: continue
            try: result[cat] = float(str(row.get("Monthly Budget","0")).replace(",", "."))
            except ValueError: result[cat] = 0.0
        return result
