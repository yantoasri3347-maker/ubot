from PyroUbot import *

__MODULE__ = "sʜᴏʀᴛᴇɴᴇʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Shortener</b>

Perintah:
<code>{0}short</code> [link] → Memendekkan link yang panjang.</blockquote></b>
"""

@PY.UBOT("short")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote>Ketik <code>.short [link]</code></blockquote>")

    link = message.text.split(None, 1)[1]
    status = await message.reply_text("<blockquote><b>🔗 Sedang memendekkan link...</b></blockquote>")

    async with aiohttp.ClientSession() as session:
        # Menggunakan API TinyURL (Tanpa Key)
        async with session.get(f"http://tinyurl.com/api-create.php?url={link}") as resp:
            short_link = await resp.text()

    if "http" in short_link:
        await status.edit(
            f"<blockquote><b>✅ LINK BERHASIL DIPENDEK</b>\n\n"
            f"<code>{short_link}</code></blockquote>"
        )
    else:
        await status.edit("<blockquote><b>❌ Gagal!</b> Pastikan link yang kamu masukkan benar.</blockquote>")