import asyncio
from telegraph import upload_file
from PyroUbot import *

__MODULE__ = "ᴛᴇʟᴇɢʀᴀᴘʜ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Telegraph</b>

Perintah:
<code>{0}tg [reply_media]</code> → Upload gambar/video ke link telegraph.</blockquote></b>
"""

@PY.UBOT("tg")
@PY.TOP_CMD
async def _(client, message):
    # Teks arahan untuk pemula
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply_text(
            "<blockquote><b>📖 PANDUAN TELEGRAPH (PEMULA)</b>\n\n"
            "Gunakan ini untuk mengubah foto/video pendek menjadi link internet.\n\n"
            "<b>Cara Pakai:</b>\n"
            "Balas (Reply) pada foto atau video, lalu ketik <code>.tg</code></blockquote>"
        )

    status_msg = await message.reply_text("<blockquote><b>⏳ Sedang mengupload ke Telegraph...</b></blockquote>")

    try:
        # Mendownload media secara lokal
        local_path = await message.reply_to_message.download()
        
        # Proses upload ke server Telegraph
        loop = asyncio.get_event_loop()
        upload_link = await loop.run_in_executor(None, upload_file, local_path)
        
        # Hasil dalam format premium
        hasil = (
            f"<blockquote><b>✅ BERHASIL DIUPLOAD</b>\n\n"
            f"<b>🌐 Link:</b> <a href='https://telegra.ph{upload_link[0]}'>Klik di Sini</a>\n\n"
            f"<b>💡 ARAHAN:</b>\n"
            f"<i>Link ini bisa kamu gunakan untuk mempercantik tampilan broadcast atau tombol inline.</i></blockquote>"
        )
        await status_msg.edit(hasil)
        
        # Menghapus file sampah di VPS agar tidak penuh
        import os
        if os.path.exists(local_path):
            os.remove(local_path)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>❌ Gagal Upload:</b>\n<code>{str(e)}</code></blockquote>")
        