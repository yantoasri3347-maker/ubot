from pyrogram import Client, filters
import requests
from PyroUbot import *

__MODULE__ = "ᴛɪᴋᴛᴏᴋ sᴇᴀʀᴄʜ"
__HELP__ = """
<blockquote><b>ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ ᴛɪᴋᴛᴏᴋ sᴇᴀʀᴄʜ</b>

  <b>➢ ᴘᴇʀɪɴᴛᴀʜ:</b> <code>{0}ttsearch</code> 
   <i>penjelasan:</b> untuk mencari vt yang di perintahkan.</i></blockquote>
"""

API_KEY = "_@PutraGanaReal55"

@PY.UBOT("tiktoksearch|tts|ttsearch")
async def tiktok_search(client, message):
    if len(message.command) < 2:
        return await message.reply("<blockquote><b>Gunakan: `.tiktoksearch query`</b></blockquote>")

    query = " ".join(message.command[1:])
    proses_msg = await message.reply("<blockquote><b>🔍 **Sedang mencari video TikTok...**</b></blockquote>")

    url = f"https://api.botcahx.eu.org/api/search/tiktoks?query={query}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return await proses_msg.edit("<blockquote><b>❌ **Gagal mengambil data dari API.**</b></blockquote>")

    data = response.json()
    if not data.get("status") or not data.get("result", {}).get("data"):
        return await proses_msg.edit("<blockquote><b>❌ **Tidak ditemukan video untuk query tersebut.**</b></blockquote>")

    video = data["result"]["data"][0]
    caption = (
        f"<blockquote><b>🎬 **Judul:** {video['title']}\n</b></blockquote>"
        f"<blockquote><b>🌍 **Wilayah:** {video['region']}\n</b></blockquote>"
        f"<blockquote><b>🎵 **Musik:** {video['music_info']['title']} - {video['music_info']['author']}\n</b></blockquote>"
        f"<blockquote><b>▶ **Jumlah Putar:** {video['play_count']}\n</b></blockquote>"
        f"<blockquote><b>❤️ **Like:** {video['digg_count']}\n</b></blockquote>"
        f"<blockquote><b>💬 **Komentar:** {video['comment_count']}\n</b></blockquote>"
        f"<blockquote><b>🔗 [Tonton di TikTok]({video['play']})</b></blockquote>"
    )

    await proses_msg.edit("<blockquote><b>📥 **Mengunduh video...**</b></blockquote>")

    await message.reply_video(video["play"], caption=caption)

    await proses_msg.delete()
