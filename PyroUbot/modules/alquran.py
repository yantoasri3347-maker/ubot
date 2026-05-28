import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from PyroUbot import *

API_URL = "https://api.quran.gading.dev"

async def fetch_ayat(surah: int, ayat: int):
    url = f"{API_URL}/surah/{surah}/{ayat}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            if res.status != 200:
                raise Exception("Ayat tidak ditemukan")

            data = await res.json()
            ayat_data = data["data"]

            arab = ayat_data["text"]["arab"]
            latin = ayat_data["text"]["transliteration"]["en"]
            arti = ayat_data["translation"]["id"]
            surah_name = ayat_data["surah"]["name"]["transliteration"]["id"]

            audio = ayat_data["audio"]["primary"]

            return surah_name, arab, latin, arti, audio


__MODULE__ = "ᴀʟ ǫᴜʀ'ᴀɴ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Al Qur'an

perintah : <code>{0}alquran 1 2</code>
    Untuk Mencari Ayat Al Qur'an

Contoh: <code>{0}alquran 1 2</code>
Maka hasilnya Surah Al-Fatihah Ayat 2</blockquote></b>
"""

@PY.UBOT("alquran")
async def alquran_handler(client, message):
    args = message.command[1:]

    if len(args) != 2 or not args[0].isdigit() or not args[1].isdigit():
        return await message.reply(
            f"<b>Format salah</b>\n"
            f"Contoh:\n<code>{message.command[0]} 1 2</code>"
        )

    surah = int(args[0])
    ayat = int(args[1])

    try:
        surah_name, arab, latin, arti, audio = await fetch_ayat(surah, ayat)

        text = f"""
{arab}

<b>{latin}</b>

<b>Artinya:</b>
{arti}

<b>({surah_name})</b>
"""
        await message.reply(text.strip())

        await client.send_audio(
            message.chat.id,
            audio=audio,
            caption=f"({surah_name})",
            title="Al-Qur'an",
            file_name="alquran.mp3"
        )

    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{e}</code>")