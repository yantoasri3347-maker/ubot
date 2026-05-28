import requests
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from PyroUbot import *

__MODULE__ = "ᴛᴇᴍᴘ ᴍᴀɪʟ"
__HELP__ = """
<b>⦪ ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ ᴛᴇᴍᴘ ᴍᴀɪʟ ⦫</b>
<blockquote>⎆ perintah :
ᚗ <code>{0}tempmail</code>
⊶ untuk untuk membuat email gratis

ᚗ <code>{0}cekmail</code>
⊶ untuk mengecek pesan masuk email

ᚗ <code>{0}resetmail</code>
⊶ untuk mereset email</blockquote>
"""

sessions_mail = {}

DOMAINS = [
    "1secmail.com",
    "1secmail.net",
    "1secmail.org"
]

def generate_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    domain = random.choice(DOMAINS)
    return name, domain

def fetch_messages(login, domain):
    url = (
        "https://www.1secmail.com/api/v1/"
        f"?action=getMessages&login={login}&domain={domain}"
    )
    return requests.get(url, timeout=15).json()

def read_message(login, domain, msg_id):
    url = (
        "https://www.1secmail.com/api/v1/"
        f"?action=readMessage&login={login}&domain={domain}&id={msg_id}"
    )
    return requests.get(url, timeout=15).json()

@PY.UBOT("tempmail")
async def tempmail(client: Client, message):
    prefix = message.command[0][0]
    user_id = message.from_user.id

    if len(message.command) > 1 and message.command[1].lower() == "help":
        return await edit_or_reply(message, HELP.format(prefix))

    # Bersihkan session expired
    expired = [
        uid for uid, data in sessions_mail.items()
        if datetime.utcnow() - data["created_at"] > timedelta(minutes=30)
    ]
    for uid in expired:
        del sessions_mail[uid]

    if user_id in sessions_mail:
        email = sessions_mail[user_id]["email"]
        return await edit_or_reply(
            message,
            f"✅ **TempMail Aktif**\n\n"
            f"📩 Email: `{email}`\n"
            f"⏳ Berlaku ±30 menit\n\n"
            f"➡ `{prefix}cekmail` untuk cek inbox\n"
            f"➡ `{prefix}resetmail` untuk email baru"
        )

    login, domain = generate_email()
    email = f"{login}@{domain}"

    sessions_mail[user_id] = {
        "login": login,
        "domain": domain,
        "email": email,
        "created_at": datetime.utcnow(),
    }

    await edit_or_reply(
        message,
        f"✅ **TempMail Berhasil Dibuat**\n\n"
        f"📩 Email: `{email}`\n"
        f"⏳ Berlaku ±30 menit\n\n"
        f"➡ `{prefix}cekmail` untuk cek inbox\n"
        f"➡ `{prefix}resetmail` untuk email baru"
    )

@PY.UBOT("cekmail")
async def cekmail(client: Client, message):
    user_id = message.from_user.id

    if user_id not in sessions_mail:
        return await edit_or_reply(
            message,
            "⚠️ Anda belum punya TempMail.\n"
            "Gunakan `.tempmail` terlebih dahulu."
        )

    data = sessions_mail[user_id]
    msgs = fetch_messages(data["login"], data["domain"])

    if not msgs:
        return await edit_or_reply(
            message,
            f"📭 Inbox `{data['email']}` masih kosong.\n"
            f"Coba cek lagi beberapa menit."
        )

    hasil = []
    for msg in msgs:
        detail = read_message(data["login"], data["domain"], msg["id"])
        hasil.append(
            f"📬 **Email Masuk**\n"
            f"👤 Dari : `{detail.get('from')}`\n"
            f"📚 Subjek : `{detail.get('subject')}`\n"
            f"🕒 Waktu : `{detail.get('date')}`\n\n"
            f"📜 **Isi:**\n{detail.get('textBody') or detail.get('htmlBody') or '-'}"
        )

    await edit_or_reply(
        message,
        "\n\n━━━━━━━━━━━━━━\n\n".join(hasil),
        disable_web_page_preview=True
    )

@PY.UBOT("resetmail")
async def resetmail(client: Client, message):
    user_id = message.from_user.id
    sessions_mail.pop(user_id, None)
    await tempmail(client, message)