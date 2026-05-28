import requests
from PyroUbot import *

__MODULE__ = "ᴠᴏɪᴄᴇ ᴀɴɪᴍᴇ"
__HELP__ = """
<blockquote><b>Bantuan Voice Anime

perintah :
<code>{0}voiceanime</code> <teks>
- Ubah teks jadi voice anime (JP, SFW)</b></blockquote>
"""

# Google TTS (JP) – simple & stabil
TTS_API = "https://translate.google.com/translate_tts"


@PY.UBOT("voiceanime")
async def voiceanime_cmd(client, message):
    try:
        text = message.text.split(None, 1)
        if len(text) < 2:
            return await message.reply("❌ Contoh: .voiceanime konnichiwa senpai~")

        query = text[1]

        params = {
            "ie": "UTF-8",
            "q": query,
            "tl": "ja",      # Japanese
            "client": "tw-ob"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(TTS_API, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            return await message.reply("❌ Gagal membuat voice")

        voice_file = "voiceanime.mp3"
        with open(voice_file, "wb") as f:
            f.write(r.content)

        await client.send_voice(
            message.chat.id,
            voice=voice_file,
            caption="🎌 Voice anime untuk kamu~",
            reply_to_message_id=message.id
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}")