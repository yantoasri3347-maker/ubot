import signal
import tornado.ioloop
import tornado.platform.asyncio
from pyrogram import Client
from PyroUbot import *

async def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    print("Cancelling outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

# --- FUNGSI NOTIFIKASI BOT API ---
async def send_log_startup():
    await asyncio.sleep(5) # Jeda agar bot stabil
    ID_LOG_CHANNEL = -1003438253199 # Ganti dengan ID Channel Log kamu
    
    # Ambil modul yang terdaftar
    modul_list = ", ".join(HELP.keys()) if HELP else "𝚃𝚒𝚍𝚊𝚔 𝚊𝚍𝚊 𝚖𝚘𝚍𝚞𝚕"
    
    if ubot._ubot:
        # Menggunakan data dari userbot pertama untuk nama akun
        akun_utama = ubot._ubot[0]
        try:
            # 1. Pesan Userbot Diaktifkan
            text_start = (
                f"<b>𝚖𝚢 𝚞𝚋𝚘𝚝 𝚙𝚛𝚎𝚖𝚒𝚞𝚖</b>\n"
                f"<b>❑ 𝚄𝚂𝙴𝚁𝙱𝙾𝚃 𝙳𝙸𝙰𝙺𝚃𝙸𝙵𝙺𝙰𝙽</b>\n"
                f"<b>├ 𝙰𝙺𝚄𝙽: {akun_utama.me.first_name}</b>\n"
                f"<b>└ 𝙸𝙳: <code>{akun_utama.me.id}</code></b>"
            )
            await bot.send_message(ID_LOG_CHANNEL, text_start)

            # 2. Pesan Module Baru (Sesuai gambar kamu)
            text_module = (
                f"<b>𝚖𝚢 𝚞𝚋𝚘𝚝 𝚙𝚛𝚎𝚖𝚒𝚞𝚖</b>\n"
                f"📦 <b>𝚂𝚄𝙺𝚂𝙴𝚂 𝙰𝙳𝙳 𝙼𝙾𝙳𝚄𝙻𝙴</b>\n\n"
                f"🛠 <b>𝙼𝚘𝚍𝚞𝚕𝚎:</b> <code>{modul_list}</code>\n"
                f"✨ <b>𝚂𝚝𝚊𝚝𝚞𝚜:</b> <code>𝙵𝚒𝚕𝚎 𝚃𝚎𝚛𝚍𝚎𝚝𝚎𝚔𝚜𝚒</code>\n"
                f"💡 <i>𝚂𝚒𝚕𝚊𝚔𝚊𝚗 𝚛𝚎𝚜𝚝𝚊𝚛𝚝 𝚋𝚘𝚝 𝚞𝚗𝚝𝚞𝚔 𝚖𝚎𝚗𝚐𝚊𝚔𝚝𝚒𝚏𝚔𝚊𝚗 𝚖𝚘𝚍𝚞𝚕 𝚒𝚗𝚒.</i> 💡"
            )
            await bot.send_message(ID_LOG_CHANNEL, text_module)
        except Exception as e:
            print(f"Gagal kirim log ke CH: {e}")

async def main():
    await bot.start()
    for _ubot in await get_userbots():
        ubot_ = Ubot(**_ubot)
        try:
            await asyncio.wait_for(ubot_.start(), timeout=10)
        except asyncio.TimeoutError:
            await remove_ubot(int(_ubot["name"]))
            print(f"[ɪɴғᴏ]: {int(_ubot['name'])} ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇʀᴇsᴘᴏɴ")
        except Exception:
            await remove_ubot(int(_ubot["name"]))
            print(f"[ɪɴғᴏ]: {int(_ubot['name'])} ʙᴇʀʜᴀsɪʟ ᴅɪ ʜᴀᴘᴜs")
    
    await bash("rm -rf *session*")
    
    # Memuat plugin dan fungsi lainnya
    await asyncio.gather(loadPlugins(), installPeer(), expiredUserbots())
    
    # --- JALANKAN NOTIFIKASI DI SINI ---
    asyncio.create_task(send_log_startup())
    
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            s, lambda: asyncio.create_task(shutdown(s, loop))
        )

    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        await bot.stop()

if __name__ == "__main__":
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    loop = tornado.ioloop.IOLoop.current().asyncio_loop
    loop.run_until_complete(main())
    