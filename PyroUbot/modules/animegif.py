import random
import requests
from PyroUbot import *

__MODULE__ = "ᴀɴɪᴍᴇ ɢɪғ"
__HELP__ = """
<blockquote><b>Bantuan Anime GIF

perintah :
<code>{0}animegif</code>
- Kirim GIF anime random (safe)</b></blockquote>
"""

GIF_API = [
    "https://api.waifu.pics/sfw/hug",
    "https://api.waifu.pics/sfw/pat",
    "https://api.waifu.pics/sfw/dance",
    "https://api.waifu.pics/sfw/wave",
    "https://api.waifu.pics/sfw/smile"
]


@PY.UBOT("animegif")
async def animegif_cmd(client, message):
    try:
        api = random.choice(GIF_API)
        res = requests.get(api, timeout=10).json()
        gif = res.get("url")

        if not gif:
            return await message.reply("❌ Gagal mengambil GIF anime")

        await client.send_animation(
            message.chat.id,
            animation=gif,
            caption="✨ Anime GIF random buat kamu~",
            reply_to_message_id=message.id
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}")