from pyrogram import Client, filters
from pyrogram import *
from PyroUbot import PY

__MODULE__ = "sᴇᴀʀᴄʜɪɴɢ ᴜsᴇʀɴᴀᴍᴇ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Searching username</b>

Perintah: <code>{0}searchname</code> [nama]
Penjelasan: untuk mencari nama dari berbagai sosial media</blockquote></b>
"""

@PY.UBOT("searchname")
@PY.TOP_CMD
async def cek_user_command(client, message):
    # Ambil argumen dari pesan
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply_text(
            "<blockquote><b>⚠️ Gunakan format: searchname [nama]</b></blockquote>"
        )
        return

    username = args[1]
    platforms = {
        "✮ GitHub": f"https://github.com/{username}",
        "✮ Instagram": f"https://www.instagram.com/{username}",
        "✮ Facebook": f"https://www.facebook.com/{username}",
        "✮ Twitter/X": f"https://x.com/{username}",
        "✮ TikTok": f"https://www.tiktok.com/@{username}",
        "✮ Telegram": f"https://t.me/{username}",
        "✮ Medium": f"https://medium.com/@{username}",
        "✮ Twitch": f"https://www.twitch.tv/@{username}",
        "✮ Pinterest": f"https://www.pinterest.com/@{username}",
        "✮ Youtube": f"https://youtube.com/@{username}"
    }

    result_text = f"<blockquote><b><emoji id=5231012545799666522>🔍</emoji> HASIL PENCARIAN USERNAME `{username}` DARI SEMUA SOSMED\n\n</blockquote></b>"
    result_text += "\n".join([f"<blockquote><b>{platform}: [Klik disini]({link}) 𝐛𝐲𝑷𝒖𝒕𝒓𝒂𝑮𝒂𝒏𝒂𝐔𝐬𝐞𝐫𝐛𝐨𝐭</blockquote></b>" for platform, link in platforms.items()])

    await message.reply_text(result_text, disable_web_page_preview=True)
