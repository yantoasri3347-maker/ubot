import re
import asyncio
from PyroUbot import *
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import UserAlreadyParticipant, InviteHashInvalid, FloodWait

__MODULE__ = "ᴀᴜᴛᴏᴊᴏɪɴ"
__HELP__ = """
<blockquote><b>『 Bantuan Auto Join 』</b>

• Perintah:
<code>.join</code>

• Cara Pakai:
Reply pesan yang berisi link grup/channel,
lalu ketik <code>.join</code>

• Fungsi:
Join semua link Telegram sekaligus.</blockquote>
"""


LINK_REGEX = r"(https?://t\.me/[^\s]+)"


@PY.UBOT("join")
async def auto_join(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply pesan yang berisi link grup.")

    text = message.reply_to_message.text or ""
    links = re.findall(LINK_REGEX, text)

    if not links:
        return await message.reply_text("❌ Tidak ada link Telegram ditemukan.")

    done = 0
    fail = 0

    msg = await message.reply_text("⏳ Memproses join grup...")

    for link in links:
        try:
            await client.join_chat(link)
            done += 1
            await asyncio.sleep(2)
        except UserAlreadyParticipant:
            done += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except (InviteHashInvalid, Exception):
            fail += 1

    await msg.edit_text(
        f"""<b>✅ AUTO JOIN SELESAI</b>

• Berhasil: <code>{done}</code>
• Gagal: <code>{fail}</code>
• Total Link: <code>{len(links)}</code>
"""
    )