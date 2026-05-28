import asyncio
import requests
from pyrogram import Client, filters
from PyroUbot import *

__MODULE__ = "ꜱᴜʙᴅᴏᴍᴀɪɴ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Subdomain</b>

Perintah:
<code>{0}sd [subdomain] [ip]</code> → Membuat subdomain baru.</blockquote></b>
"""

# --- KONFIGURASI CLOUDFLARE ---
# Sebaiknya isi data ini agar pemula tidak perlu setting manual di database
CF_EMAIL = "ISI_EMAIL_CLOUDFLARE"
CF_KEY = "ISI_GLOBAL_API_KEY"
ZONE_ID = "ISI_ZONE_ID"
DOMAIN = "domainkamu.com" 

@PY.UBOT("sd")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 3:
        # Teks arahan detail untuk pemula
        arahan = (
            "<blockquote><b>📖 PANDUAN CREATE SUBDOMAIN</b>\n\n"
            "Gunakan perintah ini untuk menghubungkan IP VPS Anda ke sebuah nama (Subdomain).\n\n"
            "<b>Cara Pakai:</b>\n"
            "<code>.sd [nama_sub] [ip_vps]</code>\n\n"
            "<b>Contoh:</b>\n"
            "<code>.sd vps01 192.168.1.1</code>\n"
            "<i>Maka akan menjadi: vps01.domainkamu.com</i>\n\n"
            "⚠️ <b>Catatan:</b> Pastikan API Cloudflare sudah terkonfigurasi di dalam script!</blockquote>"
        )
        return await message.reply_text(arahan)

    sub = message.command[1]
    ip = message.command[2]
    full_domain = f"{sub}.{DOMAIN}"

    status_msg = await message.reply_text("<blockquote><b>⏳ Sedang memproses ke Cloudflare...</b></blockquote>")

    url = f"https://api.cloudflare.org/client/v4/zones/{ZONE_ID}/dns_records"
    headers = {
        "X-Auth-Email": CF_EMAIL,
        "X-Auth-Key": CF_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": full_domain,
        "content": ip,
        "ttl": 1,
        "proxied": False # DNS Only (Bagus untuk VPN/SSH)
    }

    try:
        response = requests.post(url, headers=headers, json=data).json()

        if response.get("success"):
            res_text = (
                f"<blockquote><b>✅ SUBDOMAIN BERHASIL DIBUAT</b>\n\n"
                f"<b>🌐 Host:</b> <code>{full_domain}</code>\n"
                f"<b>📍 IP:</b> <code>{ip}</code>\n"
                f"<b>⚡ Status:</b> 🟢 Active / DNS Only\n\n"
                f"<i>Silakan tunggu 1-3 menit untuk proses propagasi DNS.</i></blockquote>"
            )
        else:
            error_msg = response["errors"][0]["message"]
            res_text = (
                f"<blockquote><b>❌ GAGAL MEMBUAT SUBDOMAIN</b>\n\n"
                f"<b>Alasan:</b> <code>{error_msg}</code>\n\n"
                f"<b>💡 Solusi:</b> Cek kembali apakah nama subdomain sudah dipakai atau API Key Anda salah.</blockquote>"
            )
        await status_msg.edit(res_text)

    except Exception as e:
        await status_msg.edit(f"<blockquote><b>⚠️ Terjadi Kesalahan:</b>\n<code>{str(e)}</code></blockquote>")

# --- NOTIFIKASI OTOMATIS KE CHANNEL ---
async def auto_notif_subdomain():
    await asyncio.sleep(7) # Jeda agar tidak tabrakan dengan module lain
    ID_LOG_CHANNEL = -1003438253199 # ID Channel sesuai gambar kamu
    
    if ubot._ubot:
        try:
            from PyroUbot import bot
            msg_modul = (
                f"<b>my ubot premium</b>\n"
                f"📦 <b>SUKSES ADD MODULE</b>\n\n"
                f"🛠 <b>Module:</b> <code>{__MODULE__}</code>\n"
                f"✨ <b>Status:</b> <code>File Terdeteksi</code>\n"
                f"💡 <i>Silakan restart bot untuk mengaktifkan module ini.</i> 💡"
            )
            await bot.send_message(ID_LOG_CHANNEL, msg_modul)
        except:
            pass

loop = asyncio.get_event_loop()
loop.create_task(auto_notif_subdomain())
