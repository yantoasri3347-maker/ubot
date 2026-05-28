import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_BOT = int(os.getenv("MAX_BOT", "9999"))

DEVS = list(map(int, os.getenv("DEVS", "1680896327").split()))

API_ID = int(os.getenv("API_ID", "31959871"))

API_HASH = os.getenv("API_HASH", "e1538576951f878bb05f1532e3a4327e")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8762638804:AAHn77UtSAZht3G28mEn10BisbwoiAm4CWc")

OWNER_ID = int(os.getenv("OWNER_ID", "1680896327"))

BLACKLIST_CHAT = list(map(int, os.getenv("BLACKLIST_CHAT", "-1003878688914").split()))

RMBG_API = os.getenv("RMBG_API", "Y8mKMpDEsaZsvRikj4xk8xRR")

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://raditaldino0_db_user:HxKshNm5TYDVMVjS@cluster0.iawv6y2.mongodb.net/?appName=Cluster0")

LOGS_MAKER_UBOT = int(os.getenv("LOGS_MAKER_UBOT", "-1003937308381"))
