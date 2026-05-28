from pyrogram.enums import MessageEntityType
from PyroUbot import *

__MODULE__ = "ɪᴅ ᴇᴍᴏᴊɪ"
__HELP__ = f"""
<blockquote><b>Emoji ID Checker</b>

Perintah:
  • {0}emoji
    └ Reply ke <b>Custom Emoji Telegram</b>

Contoh:
  Reply emoji → {0}emoji</blockquote>
"""

@PY.UBOT("emoji")
async def cek_emoji_id(client, message):
    if not message.reply_to_message:
        return await message.reply(
            "<b>Reply ke custom emoji Telegram</b>"
        )

    msg = message.reply_to_message
    if not msg.entities:
        return await message.reply(
            "<b>Pesan tidak mengandung custom emoji</b>"
        )

    for ent in msg.entities:
        if ent.type == MessageEntityType.CUSTOM_EMOJI:
            return await message.reply(
                f"<b>Emoji ID:</b>\n<code>{ent.custom_emoji_id}</code>"
            )

    return await message.reply(
        "<b>Tidak ditemukan custom emoji Telegram</b>"
    )