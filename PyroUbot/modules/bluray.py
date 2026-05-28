import aiohttp
from PyroUbot import *

__MODULE__ = "ʙʟᴜʀᴀʏ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Bluray</b>

Perintah:
<code>{0}bluray [judul film]</code> → Cek ketersediaan film di database.</blockquote></b>
"""

@PY.UBOT("bluray")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>📖 PANDUAN BLURAY (PEMULA)</b>\n\n"
            "Gunakan ini untuk mencari info ketersediaan kualitas film.\n\n"
            "<b>Cara Pakai:</b>\n"
            "<code>.bluray Spider-Man</code></blockquote>"
        )

    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang mencari informasi film...</b></blockquote>")

    try:
        # Menggunakan API publik TVMaze untuk pencarian konten (contoh database gratis)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.tvmaze.com/singlesearch/shows?q={query}") as resp:
                if resp.status != 200:
                    return await status_msg.edit("<blockquote><b>❌ Film tidak ditemukan.</b></blockquote>")
                data = await resp.json()

        name = data.get("name")
        rating = data.get("rating", {}).get("average") or "N/A"
        genres = ", ".join(data.get("genres", []))
        summary = data.get("summary", "").replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "")
        url = data.get("url")

        hasil = (
            f"<blockquote><b>🎬 HASIL PENCARIAN FILM</b>\n\n"
            f"<b>📽️ Judul:</b> <code>{name}</code>\n"
            f"<b>⭐ Rating:</b> <code>{rating}</code>\n"
            f"<b>🎭 Genre:</b> <code>{genres}</code>\n\n"
            f"<b>📝 Sinopsis:</b>\n<i>{summary[:200]}...</i>\n\n"
            f"<b>💡 ARAHAN:</b>\n"
            f"<i>Cek link <a href='{url}'>ini</a> untuk detail lebih lanjut.</i></blockquote>"
        )
        await status_msg.edit(hasil, disable_web_page_preview=True)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi kesalahan:</b>\n<code>{str(e)}</code></blockquote>")
        