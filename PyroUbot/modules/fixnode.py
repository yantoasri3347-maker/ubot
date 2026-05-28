import asyncio
import time
from pyrogram import Client, filters
from PyroUbot import *

__MODULE__ = "ꜰɪx ɴᴏᴅᴇ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Fix Node</b>

Perintah:
<code>{0}fixnode [url/ip]</code> → Cek status koneksi node/server.</blockquote></b>
"""

@PY.UBOT("fixnode")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        # Teks arahan untuk pemula jika perintah salah
        help_text = (
            "<blockquote><b>📖 PANDUAN FIX NODE (PEMULA)</b>\n\n"
            "Gunakan perintah ini untuk mengecek apakah server atau node Anda sedang 'Merah' (Down) atau 'Hijau' (Online).\n\n"
            "<b>Cara Pakai:</b>\n"
            "<code>.fixnode [alamat_ip_atau_url]</code>\n\n"
            "<b>Contoh:</b>\n"
            "<code>.fixnode 127.0.0.1:1880</code>\n"
            "<code>.fixnode google.com</code></blockquote>"
        )
        return await message.reply_text(help_text)

    target = message.command[1]
    url = f"http://{target}" if not target.startswith("http") else target

    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang menganalisa kesehatan node...</b></blockquote>")
    start_time = time.time()

    try:
        # Simulasi pengecekan koneksi
        import requests
        response = requests.get(url, timeout=10)
        ping = round((time.time() - start_time) * 1000, 2)

        if response.status_code == 200:
            res_text = (
                f"<blockquote><b>🟢 NODE SEHAT (ONLINE)</b>\n\n"
                f"<b>📍 Target:</b> <code>{target}</code>\n"
                f"<b>⚡ Respon:</b> <code>{ping}ms</code>\n"
                f"<b>✅ Status:</b> Normal\n\n"
                f"<i>Node Anda berjalan dengan baik, tidak perlu tindakan lebih lanjut.</i></blockquote>"
            )
        else:
            res_text = (
                f"<blockquote><b>🟡 NODE PERLU PERHATIAN</b>\n\n"
                f"<b>📍 Target:</b> <code>{target}</code>\n"
                f"<b>⚠️ Kode:</b> <code>{response.status_code}</code>\n\n"
                f"<b>💡 Saran:</b> Node merespon tapi tidak memberikan akses penuh. Cek firewall atau login dashboard Anda.</blockquote>"
            )
        await status_msg.edit(res_text)

    except Exception as e:
        err_text = (
            f"<blockquote><b>🔴 NODE MERAH (OFFLINE)</b>\n\n"
            f"<b>📍 Target:</b> <code>{target}</code>\n"
            f"<b>❌ Error:</b> <code>Connection Timeout / Refused</code>\n\n"
            f"<b>🛠 ARAHAN PERBAIKAN:</b>\n"
            f"1. Pastikan server VPS Anda dalam keadaan <b>Running</b>.\n"
            f"2. Cek apakah service (misal: Node-RED) sudah dinyalakan.\n"
            f"3. Pastikan port (misal: 1880) sudah di-open di Firewall.\n"
            f"4. Coba restart service melalui terminal SSH.</blockquote>"
        )
        await status_msg.edit(err_text)

# --- NOTIFIKASI OTOMATIS KE CHANNEL (MODIFIKASI MAIN) ---
# Bagian ini akan mengirim pesan ke channel seperti yang ada di foto kamu
async def auto_notif_new_module():
    await asyncio.sleep(5)
    ID_LOG_CHANNEL = -1003438253199 # Sesuaikan dengan ID Channel di foto kamu
    
    if ubot._ubot:
        akun = ubot._ubot[0]
        try:
            msg_modul = (
                f"<b>my ubot premium</b>\n"
                f"📦 <b>SUKSES ADD MODULE</b>\n\n"
                f"🛠 <b>Module:</b> <code>{__MODULE__}</code>\n"
                f"✨ <b>Status:</b> <code>File Terdeteksi</code>\n"
                f"💡 <i>Silakan restart bot untuk mengaktifkan module ini.</i> 💡"
            )
            # Mengirim via Bot API sesuai permintaan sebelumnya
            from PyroUbot import bot
            await bot.send_message(ID_LOG_CHANNEL, msg_modul)
        except:
            pass

# Jalankan task background
loop = asyncio.get_event_loop()
loop.create_task(auto_notif_new_module())
