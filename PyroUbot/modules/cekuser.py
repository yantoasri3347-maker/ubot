from pyrogram import Client
from pyrogram.enums import UserStatus
from pyrogram.errors import UsernameNotOccupied
from PyroUbot import *

MODULE = "ᴄᴇᴋ ᴜsᴇʀ"
HELP = """
<b>📌 CEK USER</b>

<blockquote><b>Perintah untuk melihat informasi lengkap akun Telegram.</b>

**Perintah:**
<code>• `{0}py @username`<code>
<code>• `{0}py reply pesan dia`</code>

<b>Fungsi:</b>
<b>• Melihat ID, username, status</b>
<b>• Deteksi bot / verified</b>
<b>• Estimasi umur akun</b>
<b>• Cek online / offline</b>

<b>Contoh:</b>
• `{0}why @telegram`</blockquote>
"""

def status_text(status):
    return {
        UserStatus.ONLINE: "🟢 Online",
        UserStatus.OFFLINE: "⚫ Offline",
        UserStatus.RECENTLY: "🕓 Recently",
        UserStatus.LAST_WEEK: "📅 Last Week",
        UserStatus.LAST_MONTH: "🗓 Last Month",
    }.get(status, "❓ Unknown")

@PY.UBOT("why")
async def whois_plus(client: Client, message):
    prefix = message.command[0][0]

    if len(message.command) > 1 and message.command[1].lower() == "help":
        return await edit_or_reply(
            message,
            HELP.format(prefix)
        )

    target = None

    if message.reply_to_message:
        if message.reply_to_message.from_user:
            target = message.reply_to_message.from_user
        elif message.reply_to_message.sender_chat:
            target = message.reply_to_message.sender_chat

    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except UsernameNotOccupied:
            return await edit_or_reply(
                message,
                "❌ **User tidak ditemukan**"
            )
        except Exception as e:
            return await edit_or_reply(message, f"⚠️ `{e}`")

    else:
        target = message.from_user

    if not target:
        return await edit_or_reply(message, "❌ Target tidak valid")

    text = (
        f"🔍 **{MODULE}**\n"
        "━━━━━━━━━━━━━━\n"
        f"👤 **Nama** : {target.first_name or '-'}\n"
        f"🆔 **ID** : `{target.id}`\n"
        f"🔗 **Username** : @{target.username}\n" if target.username else
        f"🔍 **{MODULE}**\n━━━━━━━━━━━━━━\n"
        f"👤 **Nama** : {target.first_name or '-'}\n"
        f"🆔 **ID** : `{target.id}`\n"
        f"🔗 **Username** : -\n"
    )

    text += (
        f"🤖 **Bot** : {'Ya' if target.is_bot else 'Tidak'}\n"
        f"🏷 **Verified** : {'Ya' if target.is_verified else 'Tidak'}\n"
    )

    if hasattr(target, "status"):
        text += f"📡 **Status** : {status_text(target.status)}\n"

    text += (
        "━━━━━━━━━━━━━━\n"
        f"✨ **{MODULE}**"
    )

    try:
        if target.photo:
            await message.reply_photo(
                target.photo.big_file_id,
                caption=text
            )
        else:
            await edit_or_reply(message, text)
    except Exception:
        await edit_or_reply(message, text)