import re
import asyncio
from PyroUbot import *
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import FloodWait

__MODULE__ = "ᴀᴜᴛᴏʟᴇᴀᴠᴇ"
__HELP__ = """
<blockquote><b>『 Bantuan Auto Leave 』</b>

• Perintah:
<code>.leave</code>

• Cara Pakai:
Reply pesan berisi link grup,
lalu ketik <code>.leave</code>

• Fungsi:
Keluar dari semua grup di list.</blockquote>
"""

LINK_REGEX = r"(https?://t\.me/[^\s]+)"


@PY.UBOT("leave")
async def auto_leave(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply pesan yang berisi link grup.")

    text = message.reply_to_message.text or ""
    links = re.findall(LINK_REGEX, text)

    if not links:
        return await message.reply_text("❌ Tidak ada link ditemukan.")

    done = 0
    fail = 0

    msg = await message.reply_text("⏳ Proses leave grup...")

    for link in links:
        try:
            await client.leave_chat(link)
            done += 1
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            fail += 1

    await msg.edit_text(
        f"""<b>✅ AUTO LEAVE SELESAI</b>

• Berhasil: <code>{done}</code>
• Gagal: <code>{fail}</code>
• Total Link: <code>{len(links)}</code>
"""
    )