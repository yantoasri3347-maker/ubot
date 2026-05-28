import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴘᴇʀᴀɴɢ"
__HELP__ = """
<blockquote><b>⚔️ Game War Simulation

Perintah:
<code>{0}rekrut</code>
- Menambah jumlah pasukan kamu.

<code>{0}serang</code>
- Menyerang wilayah musuh untuk menjarah koin.

<code>{0}base</code>
- Cek jumlah pasukan, koin, dan medali perang.

<code>{0}top_war</code>
- Leaderboard jenderal perang terkuat.</b></blockquote>
"""

# --- DATABASE PERANG ---
async def get_war(user_id):
    data = await get_vars(user_id, "WAR_DATA")
    if not data:
        return {"koin": 1000, "pasukan": 10, "medali": 0}
    return data

async def save_war(user_id, data, client):
    await set_vars(user_id, "WAR_DATA", data)
    players = await get_vars(client.me.id, "WAR_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "WAR_PLAYERS", players)

@PY.UBOT("rekrut")
async def rekrut_cmd(client, message):
    user_id = message.from_user.id
    data = await get_war(user_id)
    
    biaya = 500
    if data["koin"] < biaya:
        return await message.reply(f"❌ Koin tidak cukup! Butuh **{biaya} koin** untuk rekrut 5 prajurit.")
    
    data["koin"] -= biaya
    data["pasukan"] += 5
    await save_war(user_id, data, client)
    
    await message.reply(f"🎖️ **Berhasil!** Kamu merekrut 5 prajurit baru.\nTotal Pasukan: `{data['pasukan']}`\nSisa Koin: `{data['koin']}`")

@PY.UBOT("serang")
async def serang_cmd(client, message):
    user_id = message.from_user.id
    data = await get_war(user_id)
    
    if data["pasukan"] < 5:
        return await message.reply("❌ Pasukanmu terlalu lemah! Rekrut lebih banyak prajurit dulu.")

    wilayah = random.choice(["Desa Terpencil", "Benteng Pasir", "Markas Pemberontak", "Kota Baja"])
    msg = await message.reply(f"⚔️ **Mengirim pasukan ke {wilayah}...**")
    await asyncio.sleep(3)
    
    kekuatan_musuh = random.randint(1, 100)
    kekuatan_kamu = data["pasukan"] + random.randint(1, 50)
    
    if kekuatan_kamu > kekuatan_musuh:
        jarah = random.randint(2000, 10000)
        data["koin"] += jarah
        data["medali"] += 1
        res = f"🚩 **VICTORY!**\nKamu menguasai **{wilayah}**.\n💰 Jarahan: `{jarah:,} koin`\n🎖️ Medali: `+1`"
    else:
        mati = random.randint(1, 5)
        data["pasukan"] = max(0, data["pasukan"] - mati)
        res = f"💀 **DEFEAT!**\nPasukanmu terpukul mundur dari **{wilayah}**.\n📉 Prajurit gugur: `{mati}`"
        
    await save_war(user_id, data, client)
    await msg.edit(res)

@PY.UBOT("base")
async def base_cmd(client, message):
    user_id = message.from_user.id
    data = await get_war(user_id)
    
    res = (
        f"🏰 **MARKAS MILITER**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `{data['koin']:,}`\n"
        f"🪖 **Pasukan:** `{data['pasukan']}`\n"
        f"🎖️ **Medali:** `{data['medali']}`\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.reply(res)

@PY.UBOT("top_war")
async def top_war_cmd(client, message):
    msg = await message.reply("📊 **Menyusun Peringkat Jenderal...**")
    user_ids = await get_vars(client.me.id, "WAR_PLAYERS") or []
    
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "WAR_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except:
                name = f"Gen-{uid}"
            lb.append({"name": name, "medali": data.get("medali", 0)})

    if not lb:
        return await msg.edit("📭 Belum ada jenderal terdaftar.")

    lb.sort(key=lambda x: x["medali"], reverse=True)
    
    res = "🏆 **TOP 10 JENDERAL TERKUAT**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `{u['medali']} Medali`\n"
    
    await msg.edit(res)