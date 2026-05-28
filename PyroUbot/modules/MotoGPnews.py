import requests
from PyroUbot import *

__MODULE__ = "ᴍᴏᴛᴏɢᴘ"
__HELP__ = """
<blockquote><b>Bantuan MotoGP

perintah :
<code>{0}motogpnews</code>
- Berita MotoGP terbaru (ringkas)</b></blockquote>
"""

NEWS_API = "https://newsapi.org/v2/everything"
API_KEY = "051636cacda14734867eac9956e12ffc"  # 🔑 wajib isi


@PY.UBOT("motogpnews")
async def motogp_news_cmd(client, message):
    msg = await message.reply("🏍️ Mengambil berita MotoGP...")

    params = {
        "q": "MotoGP",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY
    }

    try:
        r = requests.get(NEWS_API, params=params, timeout=15)
        data = r.json()

        if data.get("status") != "ok":
            return await msg.edit("❌ Gagal mengambil berita")

        teks = "🏁 MOTO GP NEWS TERBARU\n\n"
        for i, news in enumerate(data["articles"], start=1):
            teks += (
                f"{i}. {news['title']}\n"
                f"🗞️ {news['source']['name']}\n\n"
            )

        await msg.edit(teks)

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")