import requests
import xml.etree.ElementTree as ET
import json
import os
from PyroUbot import *
import asyncio

__MODULE__ = "BeritaAnime"
__HELP__ = """
<blockquote><b>Berita Anime Terbaru Stabil</b>

Perintah:
<code>.animeberita</code> - Menampilkan berita anime terbaru (fallback otomatis & backup offline)
</blockquote>
"""

RSS_URL = "https://www.animenewsnetwork.com/encyclopedia/rss.xml"
JIKAN_API = "https://api.jikan.moe/v4/news"
BACKUP_FILE = "anime_news_backup.json"  # simpan berita terakhir di sini

@PY.UBOT("animeberita")
@PY.TOP_CMD
async def anime_berita(client, message):
    try:
        processing_msg = await message.reply_text("🔄 Mengambil berita anime terbaru...")

        # ==== TRY RSS ANN ====
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            res = requests.get(RSS_URL, headers=headers, timeout=10)
            res.raise_for_status()
            root = ET.fromstring(res.content)
            items = root.findall(".//item")
            if items:
                teks = "<b>📰 Berita Anime Terbaru (RSS ANN):</b>\n\n"
                news_list = []
                for i, item in enumerate(items[:5], start=1):
                    title = item.find("title").text if item.find("title") else "No Title"
                    link = item.find("link").text if item.find("link") else ""
                    pubDate = item.find("pubDate").text if item.find("pubDate") else "No Date"
                    teks += f"{i}. <b>{title}</b>\n📅 {pubDate}\n🔗 {link}\n\n"
                    news_list.append({"title": title, "date": pubDate, "link": link})

                # Simpan backup
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(news_list, f, ensure_ascii=False, indent=2)

                await processing_msg.edit_text(teks)
                return
        except Exception:
            pass  # RSS gagal, lanjut ke fallback

        # ==== TRY JIKAN API ====
        try:
            res = requests.get(JIKAN_API, timeout=10)
            res.raise_for_status()
            data = res.json().get("data", [])
            if data:
                teks = "<b>📰 Berita Anime Terbaru (Jikan API):</b>\n\n"
                news_list = []
                for i, item in enumerate(data[:5], start=1):
                    title = item.get("title", "No Title")
                    url = item.get("url", "")
                    date = item.get("date", "").split("T")[0] if item.get("date") else "No Date"
                    teks += f"{i}. <b>{title}</b>\n📅 {date}\n🔗 {url}\n\n"
                    news_list.append({"title": title, "date": date, "link": url})

                # Simpan backup
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(news_list, f, ensure_ascii=False, indent=2)

                await processing_msg.edit_text(teks)
                return
        except Exception:
            pass  # Jikan API gagal, lanjut ke backup

        # ==== Fallback: Backup Offline ====
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            teks = "<b>📰 Berita Anime (Backup Offline):</b>\n\n"
            for i, item in enumerate(data[:5], start=1):
                teks += f"{i}. <b>{item['title']}</b>\n📅 {item['date']}\n🔗 {item['link']}\n\n"
            await processing_msg.edit_text(teks)
            return

        # Jika semua gagal dan backup tidak ada
        await processing_msg.edit_text("❌ Tidak ada berita anime terbaru. Coba lagi nanti.")

    except Exception as e:
        print("[ANIMEBERITA ERROR]", e)
        await message.reply_text("❌ Terjadi kesalahan saat mengambil berita anime.")
        