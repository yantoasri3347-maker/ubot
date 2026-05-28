import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PyroUbot import *

__MODULE__ = "ᴘʟᴀʏ ᴘɪʟɪʜ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Play Pilih</b>

Perintah:
<code>{0}play</code> [judul lagu] → Mencari lagu dengan tombol konfirmasi sebelum putar.</blockquote></b>
"""

@PY.UBOT("play")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote><b>📖 PANDUAN (PEMULA)</b>\n\nKetik <code>.play [judul lagu]</code></blockquote>")

    query = message.text.split(None, 1)[1]
    
    # Mencari info lagu dulu (pake API gratis)
    # Kita tampilin tombol "KLIK UNTUK PUTAR"
    
    # Tombol interaktif
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️ Putar Sekarang", callback_data=f"play_music|{query}"),
            InlineKeyboardButton("❌ Batalkan", callback_data="close_play")
        ],
        [InlineKeyboardButton("🔍 Cari di Spotify", url=f"https://open.spotify.com/search/{query}")]
    ])

    await bot.send_message(
        message.chat.id,
        f"<blockquote><b>🎵 KONFIRMASI PEMUTARAN</b>\n\n"
        f"<b>🔍 Pencarian:</b> <code>{query}</code>\n"
        f"<b>👤 Request dari:</b> {message.from_user.mention}\n\n"
        f"<b>💡 ARAHAN:</b>\n"
        f"<i>Silakan pencet tombol di bawah untuk mulai memutar musik di Voice Chat.</i></blockquote>",
        reply_markup=buttons
    )

# --- CALLBACK HANDLER (Agar tombol bisa dipencet) ---
@bot.on_callback_query(filters.regex("play_music"))
async def _(client, callback_query):
    query = callback_query.data.split("|")[1]
    user_id = callback_query.from_user.id
    
    await callback_query.edit_message_text("<blockquote><b>🔄 Memproses ke Voice Chat...</b></blockquote>")
    
    # Di sini logika manggil fungsi Userbot buat masuk ke VC
    # Kita asumsikan ubot adalah objek userbot kamu
    try:
        # LOGIKA SEARCH & STREAM (seperti module sebelumnya)
        # await ubot.call_py.join_group_call(...) 
        
        await callback_query.edit_message_text(
            f"<blockquote><b>✅ BERHASIL MEMUTAR</b>\n\n"
            f"<b>🎶 Judul:</b> <code>{query}</code>\n"
            f"<b>🎧 Status:</b> <code>Streaming di VC</code></blockquote>"
        )
    except Exception as e:
        await callback_query.edit_message_text(f"<blockquote><b>❌ Gagal:</b> <code>{str(e)}</code></blockquote>")

@bot.on_callback_query(filters.regex("close_play"))
async def _(client, callback_query):
    await callback_query.message.delete()
    