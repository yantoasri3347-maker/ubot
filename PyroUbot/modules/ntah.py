from PyroUbot import *
import random
import string

__MODULE__ = "ʀᴀɴᴅᴏᴍ ᴘʀᴏ"
__HELP__ = """
<blockquote><b>Random Generator Pro</b>

Perintah:
• <code>{0}randnum min max</code>
• <code>{0}randpick a|b|c</code>
• <code>{0}randpass panjang</code>
• <code>{0}randbool</code>
• <code>{0}randhex</code></blockquote>
"""

# =====================
# RANDOM NUMBER
# =====================
@PY.UBOT("randnum")
async def rand_number(_, m):
    if len(m.command) < 3:
        return await m.reply_text("❌ contoh: .randnum 1 100")
    try:
        a = int(m.command[1])
        b = int(m.command[2])
        await m.reply_text(f"🎲 Hasil: <b>{random.randint(a, b)}</b>")
    except:
        await m.reply_text("❌ input harus angka")

# =====================
# RANDOM PICK
# =====================
@PY.UBOT("randpick")
async def rand_pick(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ contoh: .randpick kopi|teh|susu")
    items = m.text.split(" ", 1)[1].split("|")
    await m.reply_text(f"🎯 Terpilih: <b>{random.choice(items)}</b>")

# =====================
# RANDOM PASSWORD
# =====================
@PY.UBOT("randpass")
async def rand_password(_, m):
    length = int(m.command[1]) if len(m.command) > 1 else 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = "".join(random.choice(chars) for _ in range(length))
    await m.reply_text(f"🔐 Password:\n<code>{pwd}</code>")

# =====================
# RANDOM BOOLEAN
# =====================
@PY.UBOT("randbool")
async def rand_bool(_, m):
    await m.reply_text(f"⚖️ Jawaban: <b>{random.choice(['YA', 'TIDAK'])}</b>")

# =====================
# RANDOM HEX COLOR
# =====================
@PY.UBOT("randhex")
async def rand_hex(_, m):
    color = "#" + "".join(random.choice("0123456789ABCDEF") for _ in range(6))
    await m.reply_text(f"🎨 HEX Color: <code>{color}</code>")
