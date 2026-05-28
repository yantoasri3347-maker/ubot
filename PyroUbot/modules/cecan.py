from PyroUbot import *
import random
import requests
from pyrogram.enums import *
from pyrogram import *
from pyrogram.types import *
from io import BytesIO

__MODULE__ = "ᴄᴇᴄᴀɴ"
__HELP__ = """
<b>⦪ ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ ᴄᴇᴄᴀɴ ⦫</b>
<blockquote>
⎆ perintah :
ᚗ <code>{0}cecan</code> Query

<b>ᚗ Query:</b>
    <i>⊶ Indonesia</i>,
    <i>⊶ china</i>,
    <i>⊶ thailand</i>,
    <i>⊶ vietnam</i>,
    <i>⊶ hijaber</i>,
    <i>⊶ rose</i>,
    <i>⊶ ryujin</i>,
    <i>⊶ jiso</i>,
    <i>⊶ jeni</i>,
    <i>⊶ justinaxie</i>,
    <i>⊶ malaysia</i>,
    <i>⊶ japan</i>,
    <i>⊶ korea</i></blockquote>
"""

URLS = {
    "indonesia": "https://api.botcahx.eu.org/api/cecan/indonesia?apikey=_@PutraGanaReal55",
    "china": "https://api.botcahx.eu.org/api/cecan/china?apikey=_@PutraGanaReal55",
    "thailand": "https://api.botcahx.eu.org/api/cecan/thailand?apikey=_@PutraGanaReal55",
    "vietnam": "https://api.botcahx.eu.org/api/cecan/vietnam?apikey=_@PutraGanaReal55",
    "hijaber": "https://api.botcahx.eu.org/api/cecan/hijaber?apikey=_@PutraGanaReal55",
    "rose": "https://api.botcahx.eu.org/api/cecan/rose?apikey=_@PutraGanaReal55",
    "ryujin": "https://api.botcahx.eu.org/api/cecan/ryujin?apikey=_@PutraGanaReal55",
    "jiso": "https://api.botcahx.eu.org/api/cecan/jiso?apikey=_@PutraGanaReal55",
    "jeni": "https://api.botcahx.eu.org/api/cecan/jeni?apikey=_@PutraGanaReal55",
    "justinaxie": "https://api.botcahx.eu.org/api/cecan/justinaxie?apikey=_@PutraGanaReal55",
    "malaysia": "https://api.botcahx.eu.org/api/cecan/malaysia?apikey=_@PutraGanaReal55",
    "japan": "https://api.botcahx.eu.org/api/cecan/japan?apikey=_@PutraGanaReal55",
    "korea": "https://api.botcahx.eu.org/api/cecan/korea?apikey=_@PutraGanaReal55"
}

@PY.UBOT("cecan")
@PY.TOP_CMD
async def _(client, message):
    # Extract query from message
    query = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if query not in URLS:
        valid_queries = ", ".join(URLS.keys())
        await message.reply(f"Query tidak valid. Gunakan salah satu dari: {valid_queries}.")
        return

    processing_msg = await message.reply("<emoji id=5316770651720137011>🔘</emoji> Processing.....")
    
    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        response = requests.get(URLS[query])
        response.raise_for_status()
        
        photo = BytesIO(response.content)
        photo.name = 'image.jpg'
        
        await client.send_photo(message.chat.id, photo)
        await processing_msg.delete()
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(f"Gagal mengambil gambar cecan Error: {e}")