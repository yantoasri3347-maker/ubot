import requests
import os
from PyroUbot import *

__MODULE__ = "xɴxx"
__HELP__ = """
<b>♛ ʙᴀɴᴛᴜᴀɴ ᴜɴᴛᴜᴋ xɴxx ♛</b>
<blockquote><b>
Perintah :
<code>{0}xnxx</code> kata pencarian
Mendownload Video Yang Di Inginkan.</b></blockquote>
"""

@PY.UBOT("xnxx")
async def random_bokep(client, message):
    try:
        query = message.text.split()[1:]
        if not query:
            await message.reply("<emoji id=5215204871422093648>❌</emoji> Gunakan format: `.xnxx [kata kunci]`\n\nContoh: `.xnxx japanese teacher` atau `.xnxx bokep`")
            return
        search_query = " ".join(query[:4])
        
        status_msg = await message.reply(f"<emoji id=4967797089971995307>🔍</emoji> Mencari bokep untuk: **{search_query}**...")

        api_url = f"https://api.botcahx.eu.org/api/search/xnxx?query={search_query}&apikey=_@PutraGanaReal55"
        
        response = requests.get(api_url)
        response.raise_for_status()
        api = response.json()

        results = api.get('result', [])
        if not results:
            await status_msg.edit(f"<emoji id=5215204871422093648>❌</emoji> Tidak ditemukan hasil untuk: **{search_query}**")
            return

        data = results[0]

        capt = f"卍 **Hasil Pencarian: {search_query}**\n\n"
        capt += f"  ◦ **Title** : {data.get('title', 'N/A')}\n"
        capt += f"  ◦ **Views** : {data.get('views', 'N/A')}\n"
        capt += f"  ◦ **Quality** : {data.get('quality', 'N/A')}\n"
        capt += f"  ◦ **Duration** : {data.get('duration', 'N/A')}\n"
        capt += f"  ◦ **[🔗 Link ]({data.get('link', 'N/A')})**\n"

        await status_msg.edit(f"📥 Mengunduh video dari: **{data.get('title', 'N/A')}**...")

        dl_url = f"https://api.botcahx.eu.org/api/download/xnxxdl?url={data['link']}&apikey=_@PutraGanaReal55"
        dl_response = requests.get(dl_url)
        dl_response.raise_for_status()
        dl_data = dl_response.json()
        video_url = dl_data.get('result', {}).get('url')

        if not video_url:
            await status_msg.edit("<emoji id=5215204871422093648>❌</emoji> Gagal mendapatkan URL video.")
            return

        video_path = "video.mp4"

        await status_msg.edit("📥 Sedang mengunduh video, harap tunggu...")
        with requests.get(video_url, stream=True) as vid_res:
            vid_res.raise_for_status()
            with open(video_path, "wb") as f:
                for chunk in vid_res.iter_content(chunk_size=8192):
                    f.write(chunk)

        await status_msg.edit("📤 Mengunggah video ke Telegram...")
        
        await client.send_video(message.chat.id, video_path, caption=capt)
        os.remove(video_path)

        await status_msg.delete()

    except requests.exceptions.RequestException as e:
        await message.reply(f"<emoji id=5215204871422093648>❌</emoji> Terjadi Kesalahan Saat Mengakses API: {str(e)}")
    except Exception as e:
        await message.reply(f"<emoji id=5215204871422093648>❌</emoji> Terjadi Kesalahan: {str(e)}")
        
