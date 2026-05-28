import random
from PyroUbot import *
from pyrogram import *
from pyrogram.types import *

__MODULE__ = "Quick Quiz"
__HELP__ = """
<blockquote><b>『 QUICK QUIZ 』</b>

<b>Perintah:</b>
• <code>.quiz</code> → mulai quiz
• <code>.quizskor</code> → lihat skor

<b>Cara main:</b>
• Jawab LANGSUNG di chat (tanpa command)
• Siapa cepat dia dapet poin
</blockquote>
"""

QUIZ = [
    {"q": "Ibukota Indonesia?", "a": "jakarta"},
    {"q": "Presiden pertama Indonesia?", "a": "soekarno"},
    {"q": "2 + 5 = ?", "a": "7"},
    {"q": "Bahasa pemrograman logo ular?", "a": "python"},
    {"q": "Aplikasi chat warna biru?", "a": "telegram"},
    {"q": "Gunung tertinggi di dunia?", "a": "everest"},
    {"q": "Laut terluas di dunia?", "a": "pasifik"},
    {"q": "Hewan tercepat di darat?", "a": "cheetah"},
]

GAME = {}
SCORE = {}

# ===== START QUIZ =====
@PY.UBOT("quiz")
@PY.BOT("quiz")
async def quiz(_, message):
    chat_id = message.chat.id
    soal = random.choice(QUIZ)
    GAME[chat_id] = soal

    await message.reply_text(
        f"""🎯 <b>QUICK QUIZ</b>

❓ Pertanyaan:
<b>{soal['q']}</b>

⚡ Jawab langsung di chat!
"""
    )

# ===== AUTO CHECK JAWABAN =====
@PY.UBOT("autoquiz")
@PY.BOT("autoquiz")
async def autoquiz(_, message):
    chat_id = message.chat.id

    if chat_id not in GAME:
        return

    jawaban = message.text.lower()
    benar = GAME[chat_id]["a"]

    if jawaban == benar:
        user = message.from_user
        uid = user.id

        SCORE[uid] = SCORE.get(uid, 0) + 1
        del GAME[chat_id]

        await message.reply_text(
            f"""✅ <b>BENAR!</b>

👤 <b>{user.first_name}</b>
🏆 Skor: <b>{SCORE[uid]}</b> poin
"""
        )

# ===== SCORE =====
@PY.UBOT("quizskor")
@PY.BOT("quizskor")
async def skor(_, message):
    if not SCORE:
        return await message.reply_text("📭 Belum ada skor")

    text = "🏆 <b>SKOR QUICK QUIZ</b>\n\n"
    for uid, sc in SCORE.items():
        text += f"• <code>{uid}</code> : <b>{sc}</b> poin\n"

    await message.reply_text(text)