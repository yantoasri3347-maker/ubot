import random
import requests
from PyroUbot import *

__MODULE__ = "ᴡᴀɪғᴜ"
__HELP__ = """
<blockquote><b>Bantuan Waifu

perintah :
<code>{0}waifu</code>
- Kirim foto waifu random (safe)</b></blockquote>
"""

WAIFU_API = [
    "https://api.waifu.pics/sfw/waifu",
    "https://api.waifu.pics/sfw/neko",
    "https://api.waifu.pics/sfw/megumin"
]


@PY.UBOT("waifu")
async def waifu_cmd(client, message):
    try:
        api = random.choice(WAIFU_API)
        res = requests.get(api, timeout=10).json()
        img = res.get("url")

        if not img:
            return await message.reply("❌ Gagal mengambil waifu")

        await client.send_photo(
            message.chat.id,
            photo=img,
            caption="💖 Waifu random buat kamu~",
            reply_to_message_id=message.id
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}")