import asyncio
import re
from pyrogram import filters
from pyrogram.errors import FloodWait, RPCError
from PyroUbot import *

# VARIABEL GLOBAL (Wajib buat Button Help & Total Module)
__MODULE__ = "Autojoin"
__HELP__ = """
<blockquote><b>Bantuan Untuk Auto Join

Fitur otomatis join grup PUBLIK & PRIVAT via link di PM.

perintah : <code>{0}autojoin</code> [on/off]
    menyalakan atau mematikan fitur.

perintah : <code>{0}setjoin</code> [teks]
    mengatur teks yang dikirim ke grup.

perintah : <code>{0}cekjoin</code>
    cek status dan teks join saat ini.</b></blockquote>
"""

# Database status (Memory)
aj_config = {"status": False, "text": ""}

# Biar nambah di total modules dan button bisa diklik
class Help:
    def __init__(self):
        self.__MODULE__ = __MODULE__
        self.__HELP__ = __HELP__

HELP_COMMANDS.update({"autojoin": Help()})

@PY.UBOT("autojoin")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.edit(f"<b>Format: {message.text.split()[0]} on/off</b>")
    toggle = message.command[1].lower()
    aj_config["status"] = (toggle == "on")
    await message.edit(f"<b>✅ Auto Join: {'ON' if aj_config['status'] else 'OFF'}</b>")

@PY.UBOT("setjoin")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.edit("<b>Isi teksnya apa?</b>")
    aj_config["text"] = message.text.split(None, 1)[1]
    await message.edit("<b>✅ Teks join berhasil disimpan!</b>")

@PY.UBOT("cekjoin")
@PY.TOP_CMD
async def _(client, message):
    status = "ON ✅" if aj_config["status"] else "OFF ❌"
    teks = aj_config.get("text", "kosong")
    await message.edit(f"<b>Status: {status}</b>\n<b>Teks:</b> <code>{teks}</code>")

# HANDLER OTOMATIS
@ubot.on_message(filters.text & filters.private & ~filters.me, group=1)
async def _(client, message):
    if not aj_config.get("status") or not aj_config.get("text"):
        return

    # Regex untuk menangkap link t.me/+... atau t.me/joinchat/... atau t.me/username
    pattern = r"t\.me/(?:\+|joinchat/|[\w.-]+)"
    links = re.findall(pattern, message.text)
    
    if not links:
        return

    for link in links:
        try:
            # Penanganan khusus link privat (t.me/+ atau t.me/joinchat/)
            if "+" in link or "joinchat/" in link:
                # Ambil kode hash-nya saja (setelah + atau joinchat/)
                invitelink = link.replace("t.me/+", "").replace("t.me/joinchat/", "").replace("https://", "").replace("http://", "")
                # Gunakan import_chat_invite khusus untuk link privat
                target = await client.import_chat_invite(invitelink)
            else:
                # Gunakan join_chat biasa untuk link publik
                target = await client.join_chat(link)
            
            await asyncio.sleep(2)
            
            # Kirim pesan promo ke grup
            await client.send_message(target.id, aj_config["text"])
            
            # Balas orangnya di PM
            await message.reply_text("✅ berhasil masuk ke grub")
            
            # Laporan ke Saved Messages
            await client.send_message("me", f"✅ **Berhasil Join**\n👥 `{target.title}`")
            
        except RPCError as e:
            # Lapor error ke Saved Messages (misal: USER_ALREADY_PARTICIPANT atau INVITE_HASH_EXPIRED)
            if "USER_ALREADY_PARTICIPANT" in str(e):
                await message.reply_text("✅ berhasil masuk ke grub (udah di dalam)")
            else:
                await client.send_message("me", f"❌ **Gagal Join**\n🔗 `{link}`\n⚠️ `{str(e)}` ")
        except Exception:
            pass
