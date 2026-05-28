from PyroUbot import *

__MODULE__ = "ᴛᴇᴋs sᴛʏʟᴇ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Style</b>

Perintah:
<code>{0}style</code> [teks] → Ubah teks jadi gaya keren.</blockquote></b>
"""

@PY.UBOT("style")
@PY.TOP_CMD
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<blockquote>Masukkan teksnya!</blockquote>")
    
    text = message.text.split(None, 1)[1]
    # Mapping sederhana untuk gaya typewriter/mono
    res = f"<code>{text}</code>" 
    
    # Mapping Small Caps
    low = "abcdefghijklmnopqrstuvwxyz"
    cap = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    small_caps = text.lower().translate(str.maketrans(low, cap))

    await message.reply_text(
        f"<blockquote><b>✨ STYLE HASIL</b>\n\n"
        f"<b>1. Mono:</b> {res}\n"
        f"<b>2. Small Caps:</b> <code>{small_caps}</code></blockquote>"
    )