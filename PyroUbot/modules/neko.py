import requests
from PyroUbot import *

__MODULE__ = "ɴᴇᴋᴏ"
__HELP__ = """
<blockquote><b>Bantuan Neko

perintah :
<code>{0}neko</code>
- Kirim foto neko random (safe)</b></blockquote>
"""

NEKO_API = "https://api.waifu.pics/sfw/neko"


@PY.UBOT("neko")
async def neko_cmd(client, message):
    try:
        res = requests.get(NEKO_API, timeout=10).json()
        img = res.get("url")

        if not img:
            return await message.reply("❌ Gagal mengambil neko")

        await client.send_photo(
            message.chat.id,
            photo=img,
            caption="🐱 Neko random buat kamu~",
            reply_to_message_id=message.id
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}")