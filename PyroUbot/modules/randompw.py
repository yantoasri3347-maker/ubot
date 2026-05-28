import secrets
import string
from PyroUbot import *

__MODULE__ = "ʀᴀɴᴅᴏᴍ ᴘᴡ"
__HELP__ = """
<blockquote><b>Random Generator</b>

Perintah:
   <code>{0}pass</code> <panjang>
    └ Generate password random

Contoh:
   <code>{0}pass</code> 16</blockquote>
"""

@PY.UBOT("pass")
async def password_generator(client, message):
    length = 12

    if len(message.command) > 1 and message.command[1].isdigit():
        length = int(message.command[1])

    if length < 6 or length > 64:
        return await message.reply(
            "<b>Panjang password 6–64 karakter</b>"
        )

    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = "".join(secrets.choice(chars) for _ in range(length))

    await message.reply(
        f"<b>🔐 Password Random</b>\n<code>{password}</code>"
    )