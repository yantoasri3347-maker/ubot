import aiohttp
from PyroUbot import *

__MODULE__ = "ʙɪɴ ᴄʜᴇᴄᴋᴇʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Bin Checker</b>

Perintah:
<code>{0}bin</code> [6 digit angka] → Cek informasi kartu (BIN).</blockquote></b>
"""

@PY.UBOT("bin")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote><b>📖 PANDUAN (PEMULA)</b>\n\nKetik <code>.bin 451234</code> untuk cek asal kartu.</blockquote>")

    bin_number = message.command[1][:6]
    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang mencari data BIN...</b></blockquote>")

    try:
        # Mengambil data dari API lookup kartu
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://lookup.binlist.net/{bin_number}") as resp:
                if resp.status == 404:
                    return await status_msg.edit("<blockquote><b>❌ Data tidak ditemukan.</b></blockquote>")
                if resp.status != 200:
                    return await status_msg.edit("<blockquote><b>⚠️ Server sedang sibuk.</b></blockquote>")
                data = await resp.json()

        brand = data.get("brand", "Unknown")
        type_card = data.get("type", "Unknown")
        bank = data.get("bank", {}).get("name", "Unknown")
        country = data.get("country", {}).get("name", "Unknown")
        emoji = data.get("country", {}).get("emoji", "🌍")

        hasil = (
            f"<blockquote><b>💳 INFORMASI KARTU (BIN)</b>\n\n"
            f"<b>🔢 BIN:</b> <code>{bin_number}</code>\n"
            f"<b>🏦 Bank:</b> <code>{bank}</code>\n"
            f"<b>💳 Brand/Type:</b> <code>{brand.upper()} / {type_card.upper()}</code>\n"
            f"<b>📍 Negara:</b> <code>{country} {emoji}</code>\n\n"
            f"<b>💡 ARAHAN PEMULA:</b>\n"
            f"<i>Gunakan info ini untuk verifikasi metode pembayaran internasional.</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi kesalahan:</b>\n<code>{str(e)}</code></blockquote>")
        