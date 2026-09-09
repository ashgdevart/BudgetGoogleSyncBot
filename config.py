import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

@dataclass(frozen=True)
class Config:
    bot_token: str
    spreadsheet_id: str
    allowed_user_ids: frozenset[int]
    currency: str = "€"

def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value

def get_config() -> Config:
    ids = {int(x.strip()) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()}
    if not ids:
        raise RuntimeError("ALLOWED_USER_IDS is empty")
    return Config(required("BOT_TOKEN"), required("SPREADSHEET_ID"), frozenset(ids),
                  os.getenv("CURRENCY", "€"))

def google_credentials() -> Credentials:
    return Credentials.from_service_account_info(
        json.loads(required("GOOGLE_CREDENTIALS_JSON")), scopes=SCOPES
    )
