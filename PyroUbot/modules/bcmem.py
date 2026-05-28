from PyroUbot import *

__MODULE__ = "ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇᴍʙᴇʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Broadcast</b>

Perintah:
<code>{0}bcmem</code> [reply pesan/media] → Broadcast pesan yang di-reply ke semua member via PM.
<code>{0}stopbc</code> → Berhenti proses broadcast.</blockquote></b>
"""

bc_status = []

@PY.UBOT("bcmem")
@PY.TOP_CMD
async def _(client, message):
    global bc_status
    # Proteksi: Harus reply ke pesan
    if not message.reply_to_message:
        return await message.reply_text("<blockquote><b>❌ GAGAL</b>\nBalas ke pesan atau media yang mau disebar!</blockquote>")

    chat_id = message.chat.id
    status_msg = await message.reply_text("<blockquote><b>📢 Memulai mass-message via PM...</b></blockquote>")
    
    if client.me.id in bc_status:
        bc_status.remove(client.me.id)

    success = 0
    failed = 0
    
    # Ambil daftar member grup
    async for member in client.get_chat_members(chat_id):
        # Cek jika perintah stop dijalankan
        if client.me.id in bc_status:
            break
        
        # Lewati bot dan akun sendiri
        if member.user.is_bot or member.user.is_self:
            continue
            
        try:
            # Menggunakan .copy() agar tidak ada label 'Forwarded'
            await message.reply_to_message.copy(member.user.id)
            success += 1
            # Delay 3 detik agar aman dari ban Telegram
            await asyncio.sleep(3) 
        except Exception:
            failed += 1
            continue

    await status_msg.edit(
        f"<blockquote><b>✅ BROADCAST SELESAI</b>\n\n"
        f"<b>• Target:</b> <code>{success} Member</code>\n"
        f"<b>• Gagal:</b> <code>{failed} Member</code>\n\n"
        f"<i>Pesan telah terkirim satu per satu ke PM.</i></blockquote>"
    )

@PY.UBOT("stopbc")
@PY.TOP_CMD
async def _(client, message):
    bc_status.append(client.me.id)
    await message.reply_text("<blockquote><b>🛑 Broadcast dihentikan oleh user!</b></blockquote>")