import aiohttp
import os
import re
from urllib.parse import quote_plus

from PyroUbot import *

__MODULE__ = "sᴘᴏᴛɪғʏ"
__HELP__ = """
<blockquote><b>Bantuan Spotify</b>

Perintah:
<code>{0}spotify</code> judul lagu
→ Download lagu dari Spotify</blockquote>
"""

API_KEY = "_@PutraGanaReal55"
SEARCH_ENDPOINT = "https://api.botcahx.eu.org/api/search/spotify"
DL_ENDPOINT = "https://api.botcahx.eu.org/api/download/spotify"


def clean_filename(text: str) -> str:
    # Buang karakter ilegal + rapikan spasi
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "spotify_audio"


@PY.UBOT("spotify")
@PY.TOP_CMD
async def spotify_handler(client, message):
    parts = message.text.split(None, 1)
    if len(parts) < 2:
        return await message.reply(
            "<blockquote><b>📖 Cara pakai:</b>\n"
            "<code>spotify judul lagu</code></blockquote>"
        )

    query = parts[1].strip()
    msg = await message.reply("<blockquote><b>🔍 Mencari lagu...</b></blockquote>")

    filename = None
    try:
        timeout = aiohttp.ClientTimeout(total=45)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            # --- SEARCH ---
            q = quote_plus(query)
            search_url = f"{SEARCH_ENDPOINT}?query={q}&apikey={API_KEY}"

            async with session.get(search_url) as r:
                if r.status != 200:
                    return await msg.edit(f"<blockquote><b>❌ Search HTTP {r.status}</b></blockquote>")
                data = await r.json(content_type=None)

            if not data.get("status"):
                return await msg.edit("<blockquote><b>❌ Lagu tidak ditemukan</b></blockquote>")

            items = (((data.get("result") or {}).get("data")) or [])
            if not items:
                return await msg.edit("<blockquote><b>❌ Data lagu kosong</b></blockquote>")

            track_url = items[0].get("url")
            if not track_url:
                return await msg.edit("<blockquote><b>❌ URL track tidak ada</b></blockquote>")

            await msg.edit("<blockquote><b>📥 Mengunduh audio...</b></blockquote>")

            # --- DOWNLOAD INFO ---
            dl_url = f"{DL_ENDPOINT}?url={quote_plus(track_url)}&apikey={API_KEY}"

            async with session.get(dl_url) as r:
                if r.status != 200:
                    return await msg.edit(f"<blockquote><b>❌ DownloadInfo HTTP {r.status}</b></blockquote>")
                dl = await r.json(content_type=None)

            if not dl.get("status"):
                return await msg.edit("<blockquote><b>❌ Gagal ambil link download</b></blockquote>")

            res = ((dl.get("result") or {}).get("data")) or {}
            audio_url = res.get("url")
            if not audio_url:
                return await msg.edit("<blockquote><b>❌ URL audio tidak ada</b></blockquote>")

            title = clean_filename(res.get("title", "spotify_audio"))
            filename = f"{title}.mp3"

            # --- STREAM DOWNLOAD ---
            async with session.get(audio_url) as audio:
                if audio.status != 200:
                    return await msg.edit(f"<blockquote><b>❌ Audio HTTP {audio.status}</b></blockquote>")

                with open(filename, "wb") as f:
                    async for chunk in audio.content.iter_chunked(64 * 1024):
                        f.write(chunk)

        caption = (
            "<blockquote><b>🎵 SPOTIFY DOWNLOADER</b>\n\n"
            f"<b>Judul:</b> <code>{res.get('title','-')}</code>\n"
            f"<b>Artis:</b> <code>{((res.get('artist') or {}).get('name')) or '-'}</code>\n"
            f"<b>Durasi:</b> <code>{res.get('duration','-')}</code></blockquote>"
        )

        await client.send_audio(
            message.chat.id,
            audio=filename,
            caption=caption,
        )

        await msg.delete()

    except aiohttp.ClientError as e:
        await msg.edit(f"<blockquote><b>⚠️ Network error:</b>\n<code>{e}</code></blockquote>")
    except Exception as e:
        await msg.edit(f"<blockquote><b>⚠️ Error:</b>\n<code>{e}</code></blockquote>")
    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass
                