import random
import requests
from PyroUbot import *

__MODULE__ = "ᴀɴɪᴍᴇ ʙᴏʏ"
__HELP__ = """
<blockquote><b>Bantuan Anime Boy

perintah :
<code>{0}animeboy</code>
- Kirim foto anime cowok / husbu random (safe)</b></blockquote>
"""

ANIME_BOY_API = [
    "https://api.waifu.pics/sfw/husbando",
    "https://api.waifu.pics/sfw/smile",
    "https://api.waifu.pics/sfw/awoo"
]


@PY.UBOT("animeboy")
async def animeboy_cmd(client, message):
    try:
        api = random.choice(ANIME_BOY_API)
        res = requests.get(api, timeout=10).json()
        img = res.get("url")

        if not img:
            return await message.reply("❌ Gagal mengambil anime boy")

        await client.send_photo(
            message.chat.id,
            photo=img,
            caption="🖤 Anime boy random buat kamu~",
            reply_to_message_id=message.id
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}")