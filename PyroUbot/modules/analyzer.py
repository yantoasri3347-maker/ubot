import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from PyroUbot import *

__MODULE__ = "ᴀɴᴀʟʏᴢᴇʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Analyzer</b>

Perintah:
<code>{0}analyze</code> → Analisis detail grup/channel ini.</blockquote></b>
"""

@PY.UBOT("analyze")
@PY.TOP_CMD
async def _(client, message):
    # Pesan awal proses agar pengguna tahu bot sedang bekerja
    status_msg = await message.reply_text(
        "<blockquote><b>🔍 Memulai analisis chat...</b>\n"
        "<i>Mohon tunggu, sedang memindai seluruh anggota.</i></blockquote>"
    )
    
    chat_id = message.chat.id
    admins = 0
    bots = 0
    deleted = 0
    total = 0

    try:
        # Melakukan scanning terhadap semua member di chat tersebut
        async for member in client.get_chat_members(chat_id):
            total += 1
            if member.user.is_deleted:
                deleted += 1
            elif member.user.is_bot:
                bots += 1
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                admins += 1

        # Format hasil akhir dengan tampilan premium
        hasil = (
            f"<blockquote><b>📊 HASIL ANALISIS CHAT</b>\n\n"
            f"<b>👥 Total Member:</b> <code>{total}</code>\n"
            f"<b>👮 Admin:</b> <code>{admins}</code>\n"
            f"<b>🤖 Bot:</b> <code>{bots}</code>\n"
            f"<b>👻 Akun Terhapus:</b> <code>{deleted}</code>\n\n"
            f"<b>💡 ARAHAN PEMULA:</b>\n"
            f"<i>Jika akun terhapus (Ghost) terlalu banyak, sebaiknya gunakan fitur clean-ghost agar grup tidak dianggap spam oleh Telegram demi keamanan grup Anda.</i></blockquote>"
        )
        await status_msg.edit(hasil)

    except Exception as e:
        # Penanganan error jika bot tidak memiliki izin scan member
        await status_msg.edit(f"<blockquote><b>❌ Gagal Menganalisis</b>\n<code>{str(e)}</code></blockquote>")
        