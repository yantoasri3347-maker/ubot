import aiohttp
from PyroUbot import *

__MODULE__ = "ǫʀ ᴄᴏᴅᴇ"
__HELP__ = """
<blockquote><b>Bantuan Untuk QR Code</b>

Perintah:
<code>{0}qr</code> [teks/link] → Buat gambar QR Code.</blockquote></b>
"""

@PY.UBOT("qr")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote>Ketik <code>.qr [teks]</code></blockquote>")

    text = message.text.split(None, 1)[1]
    status = await message.reply_text("<blockquote><b>🏁 Membuat QR Code...</b></blockquote>")

    # Pakai API Google Charts (Gratis & Stabil Selamanya)
    qr_url = f"https://chart.googleapis.com/chart?cht=qr&chl={text}&chs=500x500&choe=UTF-8&chld=L|2"
    
    try:
        await client.send_photo(message.chat.id, qr_url, caption=f"<blockquote><b>✅ QR CODE BERHASIL</b>\n\n<code>{text}</code></blockquote>")
        await status.delete()
    except Exception as e:
        await status.edit(f"<blockquote><b>⚠️ Error:</b> <code>{str(e)}</code></blockquote>")