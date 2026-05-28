import aiohttp
from PyroUbot import *

__MODULE__ = "ᴄʀʏᴘᴛᴏ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Crypto</b>

Perintah:
<code>{0}crypto [simbol]</code> → Cek harga crypto saat ini (Contoh: btc, eth, doge).</blockquote></b>
"""

@PY.UBOT("crypto")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>📖 PANDUAN CRYPTO (PEMULA)</b>\n\n"
            "Gunakan ini untuk mengecek harga koin crypto dalam mata uang USD.\n\n"
            "<b>Cara Pakai:</b>\n"
            "<code>.crypto btc</code>\n"
            "<code>.crypto eth</code></blockquote>"
        )

    coin = message.command[1].lower()
    status_msg = await message.reply_text("<blockquote><b>🔄 Sedang mengambil data pasar...</b></blockquote>")

    try:
        # Mengambil data dari API Binance (Tanpa API Key)
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}USDT"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await status_msg.edit("<blockquote><b>❌ Koin tidak ditemukan.</b>\nPastikan simbol benar (contoh: btc, eth, sol).</blockquote>")
                data = await resp.json()

        price = float(data.get("price"))
        # Format harga agar rapi (pakai koma/titik desimal)
        formatted_price = "{:,.2f}".format(price)

        hasil = (
            f"<blockquote><b>💰 HARGA CRYPTO TERKINI</b>\n\n"
            f"<b>🪙 Koin:</b> <code>{coin.upper()} / USDT</code>\n"
            f"<b>💵 Harga:</b> <code>$ {formatted_price}</code>\n\n"
            f"<b>💡 ARAHAN PEMULA:</b>\n"
            f"<i>Harga diambil langsung dari market Binance. Ingat, investasi crypto berisiko tinggi!</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi kesalahan:</b>\n<code>{str(e)}</code></blockquote>")
        