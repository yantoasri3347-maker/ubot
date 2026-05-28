import requests
import random
from PyroUbot import *

__MODULE__ = "⚽ Berita Bola"
__HELP__ = """
<blockquote><b>Bantuan Berita Bola</b>

Perintah:
<code>{0}bola</code> → Menampilkan berita bola terbaru.
<code>{0}bola promo</code> → Menampilkan berita bola + promo/marketing</blockquote>
"""

# API berita bola (contoh: newsapi.org atau api bola gratis lainnya)
API_KEY = "051636cacda14734867eac9956e12ffc"
BASE_URL = "https://newsapi.org/v2/everything?q=football&language=id&apiKey=" + API_KEY

MARKETING_PHRASES = [
    "Jangan sampai ketinggalan update terbaru!",
    "Klik link ini untuk info eksklusif ⚡",
    "Baca berita lengkapnya dan dapatkan tips menarik!",
    "Dapatkan info menarik setiap hari bersama kami!"
]

@PY.UBOT("bola")
async def bola_cmd(client, message):
    # cek apakah ada keyword promo
    is_promo = "promo" in message.text.lower()

    try:
        # ambil data berita
        res = requests.get(BASE_URL, timeout=10).json()
        articles = res.get("articles", [])

        if not articles:
            return await message.reply_text("❌ Tidak ada berita bola terbaru saat ini!")

        # ambil 1 berita random
        news = random.choice(articles)
        title = news.get("title", "Berita Tanpa Judul")
        url = news.get("url", "")
        desc = news.get("description", "")

        # buat caption
        caption = f"⚽ *{title}*\n\n{desc}\n\nBaca selengkapnya: {url}"

        # jika promo ditambahkan
        if is_promo:
            promo_text = random.choice(MARKETING_PHRASES)
            caption += f"\n\n💡 {promo_text}"

        await message.reply_text(caption)

    except Exception as e:
        await message.reply_text(f"❌ Gagal mengambil berita bola.\nError: {e}")
        