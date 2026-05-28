import aiohttp
from PyroUbot import *

__MODULE__ = "ᴛʟᴅ ᴄʜᴇᴄᴋ"
__HELP__ = """
<blockquote><b>Bantuan Untuk TLD Check</b>

Perintah:
<code>{0}tld</code> [ekstensi] → Cek informasi ekstensi domain (Contoh: .com, .id, .xyz).</blockquote></b>
"""

@PY.UBOT("tld")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote><b>📖 PANDUAN (PEMULA)</b>\n\nKetik <code>.tld com</code> atau <code>.tld id</code> untuk cek info domain.</blockquote>")

    query = message.command[1].replace(".", "")
    status_msg = await message.reply_text("<blockquote><b>🔍 Mencari informasi ekstensi...</b></blockquote>")

    try:
        # Menggunakan API IANA/Public Data untuk info TLD
        url = f"https://rdap.iana.org/domain/{query}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await status_msg.edit(f"<blockquote><b>❌ Ekstensi .{query} tidak ditemukan atau tidak terdaftar secara global.</b></blockquote>")
                data = await resp.json()

        # Mengambil data teknis
        handle = data.get("handle", "N/A")
        status = ", ".join(data.get("status", ["Unknown"]))
        whois = data.get("port43", "N/A")

        hasil = (
            f"<blockquote><b>🌐 INFORMASI TLD (DOMAIN)</b>\n\n"
            f"<b>🌍 Ekstensi:</b> <code>.{query.upper()}</code>\n"
            f"<b>🏢 Registrant:</b> <code>{handle}</code>\n"
            f"<b>🚦 Status:</b> <code>{status}</code>\n"
            f"<b>🖥️ WHOIS Server:</b> <code>{whois}</code>\n\n"
            f"<b>💡 ARAHAN:</b>\n"
            f"<i>Data ini valid berdasarkan catatan IANA (Internet Assigned Numbers Authority).</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi kesalahan:</b>\n<code>{str(e)}</code></blockquote>")
        