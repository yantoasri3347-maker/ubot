import asyncio
from pyrogram import raw
from PyroUbot import *

__MODULE__ = "ᴀᴜᴛᴏ ʀᴇᴘᴏʀᴛ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Auto Report</b>

Perintah:
<code>{0}report</code> [reply/username] [alasan] → Laporkan akun ke Telegram.

<b>Alasan yang tersedia:</b>
<code>scam</code>, <code>spam</code>, <code>violence</code>, <code>copyright</code>, <code>child_abuse</code>, <code>other</code>.</blockquote></b>
"""

@PY.UBOT("report")
@PY.TOP_CMD
async def _(client, message):
    # Ekstrak user dan alasan
    args = await extract_user(message)
    if not args:
        return await message.reply_text("<blockquote><b>📖 PANDUAN (PEMULA)</b>\n\nBalas pesan target atau masukkan username, contoh: <code>.report @username scam</code></blockquote>")

    # Ambil alasan dari command
    reason_input = message.command[-1].lower() if len(message.command) > 1 else "other"
    
    # Mapping alasan ke format Telegram API
    reasons = {
        "scam": raw.types.InputReportReasonSpam(),
        "spam": raw.types.InputReportReasonSpam(),
        "violence": raw.types.InputReportReasonViolence(),
        "copyright": raw.types.InputReportReasonCopyright(),
        "child_abuse": raw.types.InputReportReasonChildAbuse(),
        "other": raw.types.InputReportReasonOther()
    }
    
    selected_reason = reasons.get(reason_input, raw.types.InputReportReasonOther())
    
    status_msg = await message.reply_text("<blockquote><b>📡 Mengirimkan laporan ke server Telegram...</b></blockquote>")

    try:
        user = await client.get_users(args)
        peer = await client.resolve_peer(user.id)
        
        # Menggunakan Raw API Telegram untuk melakukan report
        await client.invoke(
            raw.functions.account.ReportPeer(
                peer=peer,
                reason=selected_reason,
                message=f"Reporting this user for {reason_input} activity."
            )
        )

        hasil = (
            f"<blockquote><b>✅ LAPORAN TERKIRIM</b>\n\n"
            f"<b>👤 Target:</b> {user.mention}\n"
            f"<b>🆔 ID:</b> <code>{user.id}</code>\n"
            f"<b>⚖️ Alasan:</b> <code>{reason_input.upper()}</code>\n\n"
            f"<b>💡 ARAHAN:</b>\n"
            f"<i>Laporan telah diteruskan ke tim moderator Telegram untuk ditinjau lebih lanjut.</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>❌ Gagal Report:</b>\n<code>{str(e)}</code></blockquote>")
        