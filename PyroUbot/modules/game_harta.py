import random
import asyncio
from PyroUbot import *

__MODULE__ = "ʜᴀʀᴛᴀ"
__HELP__ = """
<blockquote><b>🏴‍☠️ Game Cari Harta Karun

Perintah:
<code>{0}petualang</code>
- Pergi mencari harta karun di lokasi acak.

<code>{0}tas</code>
- Cek isi tas, koin, dan koleksi item langka kamu.

<code>{0}jualpetualang</code>
- Jual item yang kamu temukan untuk mendapatkan koin.

<code>{0}top_harta</code>
- Leaderboard pemburu harta terkaya.</b></blockquote>
"""

# --- DATABASE HARTA ---
async def get_harta(user_id):
    data = await get_vars(user_id, "TREASURE_DATA")
    if not data:
        return {"koin": 0, "exp": 0, "tas": []}
    return data

async def save_harta(user_id, data, client):
    await set_vars(user_id, "TREASURE_DATA", data)
    players = await get_vars(client.me.id, "TREASURE_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "TREASURE_PLAYERS", players)

# Daftar Item & Harga Jual
ITEMS = {
    "💎 Berlian": 50000,
    "👑 Mahkota Tua": 25000,
    "🏺 Guci Antik": 10000,
    "⚔️ Pedang Karatan": 5000,
    "💀 Tengkorak": 1000,
}

@PY.UBOT("petualang")
async def petualang_cmd(client, message):
    user_id = message.from_user.id
    data = await get_harta(user_id)
    
    lokasi = random.choice(["Hutan Amazon", "Goa Gelap", "Pulau Terlarang", "Reruntuhan Kuil"])
    msg = await message.reply(f"🧗 **Sedang menjelajahi {lokasi}...**")
    await asyncio.sleep(3)
    
    # Peluang menemukan sesuatu
    peluang = random.randint(1, 100)
    
    if peluang <= 20: # 20% dapet zonk
        await msg.edit(f"❌ Kamu tersesat di **{lokasi}** dan tidak menemukan apa-apa.")
    elif peluang <= 40: # 20% dapet koin langsung
        koin_temu = random.randint(5000, 15000)
        data["koin"] += koin_temu
        await msg.edit(f"💰 Kamu menemukan kantong berisi **{koin_temu:,} koin** di bawah pohon!")
    else: # 60% dapet item
        item = random.choice(list(ITEMS.keys()))
        data["tas"].append(item)
        await msg.edit(f"🎁 Wow! Kamu menemukan **{item}** di dalam peti tua di **{lokasi}**!")
    
    await save_harta(user_id, data, client)

@PY.UBOT("tas")
async def tas_cmd(client, message):
    user_id = message.from_user.id
    data = await get_harta(user_id)
    
    if not data["tas"]:
        isi_tas = "Kosong"
    else:
        # Menghitung jumlah item unik
        from collections import Counter
        counts = Counter(data["tas"])
        isi_tas = "\n".join([f"- {k} (x{v})" for k, v in counts.items()])
    
    res = (
        f"🎒 **TAS PETUALANG**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `{data['koin']:,}`\n"
        f"📦 **Isi Tas:**\n{isi_tas}\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.reply(res)

@PY.UBOT("jualpetualang")
async def jual_cmd(client, message):
    user_id = message.from_user.id
    data = await get_harta(user_id)
    
    if not data["tas"]:
        return await message.reply("❌ Tas kamu kosong, gak ada yang bisa dijual!")
    
    total_jual = 0
    for item in data["tas"]:
        total_jual += ITEMS.get(item, 0)
    
    data["koin"] += total_jual
    data["tas"] = [] # Kosongkan tas setelah dijual
    
    await save_harta(user_id, data, client)
    await message.reply(f"💸 Semua isi tas telah dijual seharga **{total_jual:,} koin**!")

@PY.UBOT("top_harta")
async def top_harta_cmd(client, message):
    msg = await message.reply("📊 **Menyusun Daftar Orang Terkaya...**")
    user_ids = await get_vars(client.me.id, "TREASURE_PLAYERS") or []
    
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "TREASURE_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except:
                name = f"Explorer-{uid}"
            lb.append({"name": name, "koin": data.get("koin", 0)})

    if not lb:
        return await msg.edit("📭 Belum ada petualang terdaftar.")

    lb.sort(key=lambda x: x["koin"], reverse=True)
    
    res = "🏆 **TOP 10 PEMBURU HARTA**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `{u['koin']:,} Koin`\n"
    
    await msg.edit(res)