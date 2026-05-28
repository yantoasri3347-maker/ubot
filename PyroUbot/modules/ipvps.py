import requests
from PyroUbot import *

__MODULE__ = "ɪᴘ ɪɴꜰᴏ"
__HELP__ = """
<blockquote><b>Bantuan Untuk IP Info</b>

Perintah:
<code>{0}ipinfo [alamat_ip]</code> → Cek informasi detail alamat IP.</blockquote></b>
"""

@PY.UBOT("ipinfo")
@PY.TOP_CMD
async def _(client, message):
    # Teks arahan jika pemula tidak memasukkan IP
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>📖 PANDUAN IP INFO (PEMULA)</b>\n\n"
            "Gunakan ini untuk melacak lokasi atau penyedia internet dari sebuah IP.\n\n"
            "<b>Cara Pakai:</b>\n"
            "<code>.ipinfo 8.8.8.8</code></blockquote>"
        )

    ip_addr = message.command[1]
    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang melacak alamat IP...</b></blockquote>")

    try:
        # Mengambil data dari API eksternal
        response = requests.get(f"http://ip-api.com/json/{ip_addr}").json()
        
        if response.get("status") == "fail":
            return await status_msg.edit(f"<blockquote><b>❌ Gagal:</b> <code>{response.get('message')}</code></blockquote>")

        # Tampilan premium untuk pemula
        hasil = (
            f"<blockquote><b>🌐 INFORMASI ALAMAT IP</b>\n\n"
            f"<b>📍 IP:</b> <code>{response.get('query')}</code>\n"
            f"<b>🌍 Negara:</b> <code>{response.get('country')}</code>\n"
            f"<b>🏙️ Kota:</b> <code>{response.get('city')}</code>\n"
            f"<b>🏢 ISP:</b> <code>{response.get('isp')}</code>\n"
            f"<b>🛰️ Lat/Lon:</b> <code>{response.get('lat')}, {response.get('lon')}</code>\n\n"
            f"<b>💡 ARAHAN PEMULA:</b>\n"
            f"<i>Gunakan data ini untuk memastikan VPS atau Proxy Anda berada di lokasi yang sesuai.</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi kesalahan:</b>\n<code>{str(e)}</code></blockquote>")
        