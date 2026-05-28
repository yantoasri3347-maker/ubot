import random
from PyroUbot import *
from pyrogram import *
from pyrogram.types import *

__MODULE__ = "Tebak Angka"
__HELP__ = """
<blockquote><b>『 TEBak ANGKA 』</b>

<b>Perintah:</b>
• <code>.angka</code> → mulai game
• <code>.jawab</code> [angka] → jawab
• <code>.angkaskor</code> → lihat skor

<b>Catatan:</b>
• Angka 1–10
• Semua prefix bisa
</blockquote>
"""

GAME = {}
SCORE = {}

# ===== START GAME =====
@PY.UBOT("angka")
@PY.BOT("angka")
async def angka(_, message):
    chat_id = message.chat.id
    nomor = random.randint(1, 10)
    GAME[chat_id] = nomor

    await message.reply_text(
        f"""🎲 <b>TEBAK ANGKA</b>

Aku nyimpen angka dari <b>1–10</b>
Siapa cepat dia dapet poin 😈

Jawab:
<code>.jawab angka</code>
"""
    )

# ===== JAWAB =====
@PY.UBOT("jawab")
@PY.BOT("jawab")
async def jawab(_, message):
    chat_id = message.chat.id

    if chat_id not in GAME:
        return await message.reply_text("❌ Belum ada game. Ketik <code>.angka</code>")

    try:
        tebak = int(message.text.split(" ", 1)[1])
    except:
        return await message.reply_text("❗ Contoh: <code>.jawab 5</code>")

    angka = GAME[chat_id]

    if tebak == angka:
        user = message.from_user
        uid = user.id

        SCORE[uid] = SCORE.get(uid, 0) + 1
        del GAME[chat_id]

        await message.reply_text(
            f"""✅ <b>BENAR!</b>

🎯 Angkanya: <b>{angka}</b>
🏆 <b>{user.first_name}</b> sekarang punya <b>{SCORE[uid]}</b> poin
"""
        )
    else:
        await message.reply_text("❌ Salah 😆 coba lagi")

# ===== SCORE =====
@PY.UBOT("angkaskor")
@PY.BOT("angkaskor")
async def skor(_, message):
    if not SCORE:
        return await message.reply_text("📭 Belum ada skor")

    text = "🏆 <b>SKOR TEBAK ANGKA</b>\n\n"
    for uid, sc in SCORE.items():
        text += f"• <code>{uid}</code> : <b>{sc}</b> poin\n"

    await message.reply_text(text)