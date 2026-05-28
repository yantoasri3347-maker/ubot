import random
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.types import Message
from pyrogram import Client, filters
import requests
from PyroUbot import *

__MODULE__ = "ᴢᴏᴅɪᴀᴋ"
__HELP__ = """
<b>⦪ ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ ᴢᴏᴅɪᴀᴋ ⦫</b>

<blockquote><b>⎆ ᴘᴇʀɪɴᴛᴀʜ :
ᚗ <code>{0}zodiak</code> taurus

⌭ ᴘᴇɴᴊᴇʟᴀsᴀɴ:
ᚗ meramal zodiak</blockquote>
"""

@PY.UBOT("zodiak")
async def _(client, message):
    if len(message.command) < 2:
        await message.reply_text("<blockquote><b>**Gunakan perintah:** `.cuttly url`\n\nContoh: `.zodiak taurus`<.blockquote></b>")
        return

    a = " ".join(message.command[1:])
    api_url = f"https://api.siputzx.my.id/api/primbon/zodiak?zodiak={a}"

    try:
        response = requests.get(api_url).json()

        if response.get("status"):
            zodiak_res = response["data"]["zodiak"].title()
            nomor_res = response["data"]["nomor_keberuntungan"]
            aroma_res = response["data"]["aroma_keberuntungan"]
            planet_res = response["data"]["planet_yang_mengitari"]
            bunga_res = response["data"]["bunga_keberuntungan"]
            warna_res = response["data"]["warna_keberuntungan"]
            batu_res = response["data"]["batu_keberuntungan"]
            elemen_res = response["data"]["elemen_keberuntungan"]
            pasangan_res = response["data"]["pasangan_zodiak"]
            
            reply_text = (
                f"""
<blockquote><emoji id=5080331039922980916>⚡️</emoji> zodiak :\n {zodiak_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Nomor Keberuntungan :\n {nomor_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Aroma Keberuntungan :\n {aroma_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Planet Keberuntungan :\n {planet_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Bunga Keberuntungan :\n {bunga_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Warna Keberuntungan :\n {warna_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Batu Keberuntungan :\n {batu_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Elemen Keberuntungan :\n {elemen_res}</blockquote>
<blockquote><emoji id=5787363840316411387>🗄</emoji> Pasangan Zodiak :\n {pasangan_res}</blockquote>
                """
            )


            await message.reply_text(reply_text)
        else:
            await message.reply_text(f"<blockquote><b>❌ Maaf, Title dari **{title}** tidak ditemukan.</blockquote></b>")
    except Exception as e:
        await message.reply_text(f"<blockquote><b>⚠️ Terjadi kesalahan saat mengambil data:\n`{str(e)}`</blockquote></b>")
