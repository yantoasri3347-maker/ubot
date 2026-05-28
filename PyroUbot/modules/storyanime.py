import random
import requests
import os
from PyroUbot import *

__MODULE__ = "sᴛᴏʀʏ ᴀɴɪᴍᴇ+"
__HELP__ = """
<blockquote><b>Bantuan Story Anime Voice

perintah :
<code>{0}storyanime</code>
- Cerita anime + voice anime otomatis (SFW)</b></blockquote>
"""

TOKOH = [
    "Aiko", "Haru", "Ren", "Mika", "Sora", "Yuki", "Akira", "Hina"
]

SETTING = [
    "di sekolah sakura yang tenang",
    "di kota futuristik yang bercahaya",
    "di desa kecil dekat pegunungan",
    "di dunia sihir penuh misteri",
    "di festival musim panas"
]

KONFLIK = [
    "menyimpan rahasia besar",
    "menghadapi ujian yang sulit",
    "bertemu teman lama yang berubah",
    "harus memilih antara mimpi dan kenyataan",
    "tersesat dalam kejadian tak terduga"
]

AKHIR = [
    "dan menemukan arti persahabatan sejati.",
    "yang mengubah hidupnya selamanya.",
    "dan memulai petualangan baru.",
    "dengan senyuman dan harapan baru.",
    "serta janji untuk tidak menyerah."
]

TTS_API = "https://translate.google.com/translate_tts"


@PY.UBOT("storyanime")
async def storyanime_voice_cmd(client, message):
    try:
        t = random.choice(TOKOH)
        s = random.choice(SETTING)
        k = random.choice(KONFLIK)
        a = random.choice(AKHIR)

        story = (
            f"{t} hidup {s}. "
            f"Suatu hari, ia {k}. "
            f"Di tengah semua itu, {t} belajar untuk percaya pada dirinya sendiri {a}"
        )

        # kirim teks ceritanya
        await message.reply(f"📖 Story Anime\n\n{story}")

        # buat voice anime (JP)
        params = {
            "ie": "UTF-8",
            "q": story,
            "tl": "ja",
            "client": "tw-ob"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(TTS_API, params=params, headers=headers, timeout=20)
        if r.status_code != 200:
            return await message.reply("❌ Gagal membuat voice anime")

        voice_file = "storyanime_voice.mp3"
        with open(voice_file, "wb") as f:
            f.write(r.content)

        await client.send_voice(
            message.chat.id,
            voice=voice_file,
            caption="🎧 Voice Anime Story",
            reply_to_message_id=message.id
        )

        if os.path.exists(voice_file):
            os.remove(voice_file)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")