import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_BOT = int(os.getenv("MAX_BOT", "9999"))

DEVS = list(map(int, os.getenv("DEVS", "1680896327").split()))

API_ID = int(os.getenv("API_ID", "34477150"))

API_HASH = os.getenv("API_HASH", "6569f33895a0ab31f487b17b7ec989b5")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8715319292:AAFsSeibzR6lQD4FaGfub1l-HYeFUFnPCzo")

OWNER_ID = int(os.getenv("OWNER_ID", "1680896327"))

BLACKLIST_CHAT = list(map(int, os.getenv("BLACKLIST_CHAT", "-1003878688914").split()))

RMBG_API = os.getenv("RMBG_API", "Y8mKMpDEsaZsvRikj4xk8xRR")

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://ntr970048_db_user:xwSX7DCfIptQybbw@cluster0.ssw7pj0.mongodb.net/?appName=Cluster0")

LOGS_MAKER_UBOT = int(os.getenv("LOGS_MAKER_UBOT", "-1003878688914"))