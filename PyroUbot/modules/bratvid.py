import requests
import os
from PyroUbot import *

__MODULE__ = "BratVideo"
__HELP__ = """
<b>✮ Fitur Brat Video ✮</b>

Perintah:
<code>.bratvideo [text]</code> - Membuat video teks ala tren TikTok
"""

API_URL = "https://brat.siputzx.my.id/gif?text="  # API baru

async def BratVideo(text: str):
    if not text:
        return "<blockquote><b>❌ Text tidak boleh kosong!</b></blockquote>"
    if len(text) > 250:
        return "<blockquote><b>❌ Text terlalu panjang!</b></blockquote>"

    temp_dir = os.path.join(os.getcwd(), "lib")
    os.makedirs(temp_dir, exist_ok=True)
    output_path = os.path.join(temp_dir, "brat_output.mp4")

    try:
        # panggil API
        res = requests.get(f"{API_URL}{requests.utils.quote(text)}", stream=True)
        if res.status_code != 200:
            raise Exception("Gagal mengambil video dari API")

        # simpan sementara
        with open(output_path, "wb") as f:
            f.write(res.content)

        return output_path

    except Exception as e:
        print(f"[BRATVIDEO ERROR] {e}")
        return "<blockquote><b>❌ Terjadi kesalahan saat membuat video</b></blockquote>"

@PY.UBOT("bratvideo")
@PY.TOP_CMD
async def bratvideo_handler(client, message):
    text = message.text.split(maxsplit=1)[-1] if len(message.text.split()) > 1 else None
    if not text:
        await message.reply_text("<blockquote><b>❌ Textnya mana?</b></blockquote>")
        return

    processing_msg = await message.reply_text("<blockquote><b>🔄 Proses membuat video...</b></blockquote>")
    video_path = await BratVideo(text)

    if isinstance(video_path, str) and video_path.startswith("<blockquote><b>❌"):
        await processing_msg.delete()
        await message.reply_text(video_path)
    else:
        await processing_msg.delete()
        await message.reply_video(video=video_path, caption="<b>✅ Selesai!</b>")
        if os.path.exists(video_path):
            os.remove(video_path)
            