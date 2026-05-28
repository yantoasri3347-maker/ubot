import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴘɪʟᴏᴛ"
__HELP__ = """
<blockquote><b>✈️ Game Sky Warrior

Perintah:
<code>{0}patroli</code>
- Terbang berpatroli untuk mencari koin aman.

<code>{0}dogfight</code>
- Duel udara melawan musuh (Hadiah besar, resiko tinggi).

<code>{0}hangar</code>
- Cek status pesawat, koin, dan rank pilot.

<code>{0}upgrade_pesawat</code>
- Ganti pesawat ke model yang lebih canggih.

<code>{0}top_pilot</code>
- Leaderboard pilot dengan kill terbanyak.</b></blockquote>
"""

# --- DATABASE PILOT ---
async def get_pilot(user_id):
    data = await get_vars(user_id, "PILOT_DATA")
    if not data:
        return {"koin": 1000, "pesawat": "Cessna", "kills": 0, "exp": 0}
    return data

async def save_pilot(user_id, data, client):
    await set_vars(user_id, "PILOT_DATA", data)
    players = await get_vars(client.me.id, "PILOT_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "PILOT_PLAYERS", players)

# Katalog Pesawat
AIRCRAFT_SHOP = {
    "f16": {"nama": "F-16 Fighting Falcon", "harga": 50000, "power": 50},
    "f35": {"nama": "F-35 Lightning II", "harga": 150000, "power": 100},
    "f22": {"nama": "F-22 Raptor", "harga": 500000, "power": 200},
}

@PY.UBOT("patroli")
async def patroli_cmd(client, message):
    user_id = message.from_user.id
    data = await get_pilot(user_id)
    
    msg = await message.reply(f"🛫 **Pesawat {data['pesawat']} sedang lepas landas...**")
    await asyncio.sleep(2)
    await msg.edit("☁️ **Sedang berpatroli di wilayah udara...**")
    await asyncio.sleep(2)
    
    cuan = random.randint(5000, 15000)
    data["koin"] += cuan
    data["exp"] += 10
    
    await save_pilot(user_id, data, client)
    await msg.edit(f"🛬 **Mendarat dengan selamat!**\n💰 Pendapatan: `Rp{cuan:,}`\n✨ EXP: `+10`")

@PY.UBOT("dogfight")
async def dogfight_cmd(client, message):
    user_id = message.from_user.id
    data = await get_pilot(user_id)
    
    msg = await message.reply("🚨 **WARNING! Pesawat musuh terdeteksi!**")
    await asyncio.sleep(2)
    await msg.edit("🚀 **Fox Two! Meluncurkan rudal...**")
    await asyncio.sleep(2)
    
    # Peluang menang (Pesawat lebih mahal = peluang lebih tinggi)
    power_bonus = 0
    for k, v in AIRCRAFT_SHOP.items():
        if v["nama"] == data["pesawat"]:
            power_bonus = v["power"]
            
    win_chance = random.randint(1, 100) + (power_bonus // 5)
    
    if win_chance > 50:
        loot = random.randint(20000, 50000)
        data["koin"] += loot
        data["kills"] += 1
        res = f"💥 **TARGET DESTROYED!**\nKamu menjatuhkan musuh.\n💰 Bonus: `Rp{loot:,}`\n🎯 Total Kills: `{data['kills']}`"
    else:
        rugi = random.randint(5000, 10000)
        data["koin"] = max(0, data["koin"] - rugi)
        res = f"🔥 **MAYDAY!** Pesawatmu terkena tembakan dan harus RTO.\n💸 Biaya perbaikan: `Rp{rugi:,}`"
        
    await save_pilot(user_id, data, client)
    await msg.edit(res)

@PY.UBOT("hangar")
async def hangar_cmd(client, message):
    user_id = message.from_user.id
    data = await get_pilot(user_id)
    
    res = (
        f"👨‍✈️ **FLIGHT HANGAR**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `Rp{data['koin']:,}`\n"
        f"✈️ **Pesawat:** `{data['pesawat']}`\n"
        f"🎯 **Kills:** `{data['kills']}`\n"
        f"📈 **EXP:** `{data['exp']}`\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.reply(res)

@PY.UBOT("upgrade_pesawat")
async def upgrade_fly_cmd(client, message):
    if len(message.command) < 2:
        shop_msg = "🛒 **AIRCRAFT SHOP**\n\n"
        for k, v in AIRCRAFT_SHOP.items():
            shop_msg += f"• `{k}` : {v['nama']} (Rp{v['harga']:,})\n"
        shop_msg += "\nKetik: `.upgrade_pesawat [kode]`"
        return await message.reply(shop_msg)
    
    kode = message.command[1].lower()
    if kode not in AIRCRAFT_SHOP:
        return await message.reply("❌ Kode pesawat salah!")
        
    user_id = message.from_user.id
    data = await get_pilot(user_id)
    item = AIRCRAFT_SHOP[kode]
    
    if data["koin"] < item["harga"]:
        return await message.reply(f"❌ Koin tidak cukup! Kurang `Rp{item['harga'] - data['koin']:,}` lagi.")
        
    data["koin"] -= item["harga"]
    data["pesawat"] = item["nama"]
    
    await save_pilot(user_id, data, client)
    await message.reply(f"🔥 **UPGRADED!** Sekarang kamu menggunakan **{item['nama']}**!")

@PY.UBOT("top_pilot")
async def top_pilot_cmd(client, message):
    msg = await message.reply("📊 **Menyusun Ranking Ace Pilot...**")
    user_ids = await get_vars(client.me.id, "PILOT_PLAYERS") or []
    
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "PILOT_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except: name = f"Pilot-{uid}"
            lb.append({"name": name, "kills": data.get("kills", 0)})

    lb.sort(key=lambda x: x["kills"], reverse=True)
    res = "🏆 **TOP 10 ACE PILOTS**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `{u['kills']} Kills`\n"
    await msg.edit(res)