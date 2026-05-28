from PyroUbot import *

__MODULE__ = "𝙲𝚞𝚜𝚝𝚘𝚖"
__HELP__ = """
<blockquote><b>Bantuan Untuk Custom

perintah : <code>{0}me</code>
    menampilkan informasi profil dan ID akun anda</b></blockquote>
"""

@PY.UBOT("me")
@PY.TOP_CMD
async def _(client, message):
    await message.edit("`Sedang mengambil data...` 🟢")
    
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Tidak ada"
    
    # ID Lu: 530656645
    caption = (
        "✅ **Userbot Profile**\n"
        "--- --- --- --- ---\n"
        f"👤 **Nama:** {full_name}\n"
        f"🆔 **ID:** `{user_id}`\n"
        f"🔗 **Username:** {username}\n"
        "--- --- --- --- ---"
    )
    
    await message.edit(caption)

 #by yowrrama.t.me