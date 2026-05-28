import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from PyroUbot import *

__MODULE__ = "ɢʟᴏʙᴀʟ ʙᴀɴ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Global Ban</b>

Perintah:
<code>{0}gban [user_id/username/reply]</code> → Ban user dari semua grup yang kamu kelola.
<code>{0}ungban [user_id/username/reply]</code> → Menghapus status gban user.</blockquote></b>
"""

@PY.UBOT("gban")
@PY.TOP_CMD
async def _(client, message):
    user_id = await extract_user(message)
    if not user_id:
        # Teks arahan jika pemula bingung cara pakainya
        return await message.reply_text(
            "<blockquote><b>📖 PANDUAN GBAN (PEMULA)</b>\n\n"
            "Fitur ini akan membanned user di <b>SEMUA</b> grup tempat Anda menjadi admin.\n\n"
            "<b>Cara Pakai:</b>\n"
            "1. Balas (Reply) pesan pelaku lalu ketik <code>.gban</code>\n"
            "2. Atau ketik <code>.gban [username/ID]</code></blockquote>"
        )

    status_msg = await message.reply_text("<blockquote><b>⏳ Memulai proses Global Ban...</b></blockquote>")
    
    try:
        user = await client.get_users(user_id)
    except Exception as e:
        return await status_msg.edit(f"<blockquote><b>❌ User tidak ditemukan:</b> {str(e)}</blockquote>")

    done = 0
    failed = 0
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            try:
                await client.ban_chat_member(dialog.chat.id, user.id)
                done += 1
                await asyncio.sleep(0.1) # Delay tipis agar tidak FloodWait
            except:
                failed += 1

    hasil = (
        f"<blockquote><b>🚫 GLOBAL BAN BERHASIL</b>\n\n"
        f"<b>👤 User:</b> {user.mention}\n"
        f"<b>🆔 ID:</b> <code>{user.id}</code>\n\n"
        f"<b>✅ Berhasil Ban:</b> <code>{done} Grup</code>\n"
        f"<b>❌ Gagal/Bukan Admin:</b> <code>{failed} Grup</code>\n\n"
        f"<b>💡 INFO:</b>\n"
        f"<i>User ini sekarang tidak bisa masuk ke grup mana pun yang Anda kelola.</i></blockquote>"
    )
    await status_msg.edit(hasil)

@PY.UBOT("ungban")
@PY.TOP_CMD
async def _(client, message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("<blockquote>Gunakan: <code>.ungban [username/ID/reply]</code></blockquote>")

    status_msg = await message.reply_text("<blockquote><b>⏳ Menghapus status Global Ban...</b></blockquote>")
    
    done = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            try:
                await client.unban_chat_member(dialog.chat.id, user_id)
                done += 1
            except:
                pass

    await status_msg.edit(f"<blockquote><b>✅ UNGBAN BERHASIL</b>\nUser telah di-unban di <code>{done}</code> grup.</blockquote>")
    