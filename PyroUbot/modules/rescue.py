import os
import time
import subprocess
from PyroUbot import *
from pyrogram import *
from pyrogram.types import *

__MODULE__ = "ʀᴇsᴄᴜᴇ"
__HELP__ = """
<blockquote><b>『 Bantuan Rescue 』</b>

• Perintah:
<code>.rescue</code>

• Fungsi:
Auto restart ubot saat error / lag.</blockquote>
"""


@PY.UBOT("rescue")
async def rescue_ubot(client, message):
    await message.reply_text("🛟 Rescue mode aktif...")

    log = subprocess.getoutput("tail -n 20 logs.txt")

    if "Traceback" in log or "Error" in log:
        subprocess.Popen(
            "pkill -f PyroUbot && python3 -m PyroUbot",
            shell=True
        )
        await message.reply_text("♻️ Error terdeteksi, ubot direstart.")
    else:
        await message.reply_text("✅ UBot aman, tidak ada error.")