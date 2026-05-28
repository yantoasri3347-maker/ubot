import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴛᴇʙᴀᴋ ᴀɴɪᴍᴇ"

ANIME_QUESTIONS = [
    {"hint": "Anime tentang ninja dengan jurus bayangan", "answer": "naruto"},
    {"hint": "Anime bajak laut dengan topi jerami", "answer": "one piece"},
    {"hint": "Anime pembasmi iblis dengan pedang nichirin", "answer": "demon slayer"},
    {"hint": "Anime titan vs manusia", "answer": "attack on titan"},
    {"hint": "Anime catatan kematian", "answer": "death note"},
]

TEBAK_SESSION = {}
TEBAK_TIMER = {}
TIME_LIMIT = 30


def clear_game(chat_id):
    # hapus session
    TEBAK_SESSION.pop(chat_id, None)

    # stop timer kalau ada
    timer = TEBAK_TIMER.pop(chat_id, None)
    if timer:
        timer.cancel()


@PY.UBOT("tebakanime")
async def tebak_anime_cmd(client, message):
    chat_id = message.chat.id

    if chat_id in TEBAK_SESSION:
        return await message.reply("⏳ Game masih berjalan!")

    soal = random.choice(ANIME_QUESTIONS)
    TEBAK_SESSION[chat_id] = soal["answer"]

    await message.reply(
        f"🎌 TEBAK ANIME\n\n"
        f"🧩 Petunjuk:\n"
        f"{soal['hint']}\n\n"
        f"⏱️ Waktu: {TIME_LIMIT} detik\n"
        f"Jawab dengan .jawab <jawaban>"
    )

    async def timeout():
        await asyncio.sleep(TIME_LIMIT)
        if chat_id in TEBAK_SESSION:
            jawaban = TEBAK_SESSION[chat_id]
            clear_game(chat_id)
            await client.send_message(
                chat_id,
                f"⏰ WAKTU HABIS!\nJawaban: {jawaban.title()}"
            )

    TEBAK_TIMER[chat_id] = asyncio.create_task(timeout())


@PY.UBOT("jawab")
async def jawab_cmd(client, message):
    chat_id = message.chat.id

    if chat_id not in TEBAK_SESSION:
        return await message.reply("❌ Tidak ada game aktif")

    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("❌ Gunakan: .jawab <jawaban>")

    jawaban_user = args[1].lower()
    jawaban_benar = TEBAK_SESSION[chat_id]

    if jawaban_user == jawaban_benar:
        clear_game(chat_id)
        await message.reply("✅ BENAR! 🎉")
    else:
        await message.reply("❌ Salah! Coba lagi ⏳")