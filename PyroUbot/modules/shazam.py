import aiohttp
from PyroUbot import *

__MODULE__ = "sʜᴀᴢᴀᴍ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Shazam</b>

Perintah:
<code>{0}find</code> [reply audio/video] → Cari judul lagu dari suara.</blockquote></b>
"""

@PY.UBOT("find")
@PY.TOP_CMD
async def _(client, message):
    # Validasi reply
    if not message.reply_to_message or not (message.reply_to_message.audio or message.reply_to_message.voice or message.reply_to_message.video):
        return await message.reply_text("<blockquote><b>❌ GAGAL</b>\nBalas ke audio, voice note, atau video yang ada suaranya!</blockquote>")

    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang mendengarkan dan menganalisis...</b></blockquote>")
    
    # Download file ke VPS sementara
    file_path = await message.reply_to_message.download()

    async with aiohttp.ClientSession() as session:
        try:
            # Menggunakan API Tools Shazam yang stabil
            data = aiohttp.FormData()
            data.add_field('file', open(file_path, 'rb'))
            
            api_url = f"https://api.botcahx.eu.org/api/tools/shazam?apikey=@31Moire_mor"
            async with session.post(api_url, data=data) as resp:
                result_data = await resp.json()

            # Proteksi error 'result'
            if not result_data.get("status") or "result" not in result_data:
                return await status_msg.edit("<blockquote><b>❌ TIDAK DIKENALI</b>\nMaaf, judul lagu tidak ditemukan dalam database.</blockquote>")

            res = result_data["result"]
            
            # Tampilan rapi ala ubot premium
            text = (
                f"<blockquote><b>🎵 LAGU DITEMUKAN!</b>\n\n"
                f"<b>🎶 Judul:</b> <code>{res.get('title', 'Unknown')}</code>\n"
                f"<b>👤 Artis:</b> <code>{res.get('artists', 'Unknown')}</code>\n"
                f"<b>💿 Album:</b> <code>{res.get('album', '-')}</code>\n\n"
                f"<i>Gunakan .spotify untuk download lagunya!</i></blockquote>"
            )
            await status_msg.edit(text)

        except Exception as e:
            await status_msg.edit(f"<blockquote><b>⚠️ TERJADI KESALAHAN:</b>\n<code>{str(e)}</code></blockquote>")
        
        finally:
            # Hapus file sampah agar VPS tidak penuh
            if os.path.exists(file_path):
                os.remove(file_path)