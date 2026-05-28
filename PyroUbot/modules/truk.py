import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴛʀᴜᴋ"
__HELP__ = """
<blockquote><b>🚚 Game Truck Simulator (V3 - Fatigue System)

Perintah:
<code>{0}narik_truk</code>
- Kerja antar barang (Butuh tenaga).

<code>{0}istirahat</code>
- Mampir ke Rest Area untuk pulihkan tenaga.

<code>{0}garasi</code>
- Cek koin, truk, dan sisa tenaga.

<code>{0}beli_truk</code>
- Upgrade armada trukmu.

<code>{0}top_truk</code>
- Ranking Bos Ekspedisi terkaya.</b></blockquote>
"""

# --- DATABASE TRUK ---
async def get_truck(user_id):
    data = await get_vars(user_id, "TRUCK_DATA")
    if not data:
        return {"koin": 2000, "truk": "Pickup L300", "rit": 0, "tenaga": 100}
    # Pastikan key tenaga ada untuk pemain lama
    if "tenaga" not in data:
        data["tenaga"] = 100
    return data

async def save_truck(user_id, data, client):
    await set_vars(user_id, "TRUCK_DATA", data)
    players = await get_vars(client.me.id, "TRUCK_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "TRUCK_PLAYERS", players)

# Katalog Truk
TRUCK_SHOP = {
    "canter": {"nama": "Mitsubishi Canter", "harga": 25000, "bonus": 5000},
    "fuso": {"nama": "Hino Fuso", "harga": 75000, "bonus": 15000},
    "scania": {"nama": "Scania R500 V8", "harga": 250000, "bonus": 50000},
}

@PY.UBOT("narik_truk")
async def narik_truk_cmd(client, message):
    user_id = message.from_user.id
    data = await get_truck(user_id)
    
    if data["tenaga"] < 20:
        return await message.reply("💤 **Kamu terlalu lelah!**\nTenaga tersisa cuma `" + str(data["tenaga"]) + "%`. Silakan ketik `.istirahat` dulu di Rest Area.")

    rute = random.choice(["Merak - Lampung", "Palembang - Jambi", "Bali - Lombok", "Jogja - Surabaya"])
    muatan = random.choice(["📦 Paket Express", "⛽ BBM", "🏗️ Beton", "🍎 Buah Segar"])
    
    msg = await message.reply(f"🚛 **Memuat {muatan}...**")
    await asyncio.sleep(2)
    await msg.edit(f"🛣️ **Mengemudi menuju {rute}...**")
    await asyncio.sleep(3)
    
    # RESIKO JALANAN
    nasib = random.randint(1, 100)
    if nasib <= 15: # 15% Tilang/Pungli
        denda = random.randint(2000, 5000)
        data["koin"] = max(0, data["koin"] - denda)
        data["tenaga"] -= 10
        await save_truck(user_id, data, client)
        return await msg.edit(f"👮 **APES!** Kamu kena denda operasi zebra di jalan.\nBayar: `Rp{denda:,}`\nTenaga berkurang: `-10%`")

    # HASIL NARIK
    base_ongkos = random.randint(12000, 28000)
    bonus_truk = 0
    for k, v in TRUCK_SHOP.items():
        if v["nama"] == data["truk"]:
            bonus_truk = v["bonus"]
            
    total_cuan = base_ongkos + bonus_truk
    data["koin"] += total_cuan
    data["rit"] += 1
    data["tenaga"] -= 20 # Berkurang setiap narik
    
    await save_truck(user_id, data, client)
    await msg.edit(
        f"✅ **Tiba di Gudang!**\n"
        f"💰 Ongkos: `Rp{total_cuan:,}`\n"
        f"⚡ Tenaga Sisa: `{data['tenaga']}%`\n"
        f"🏁 Total: `{data['rit']} Rit`"
    )

@PY.UBOT("istirahat")
async def istirahat_cmd(client, message):
    user_id = message.from_user.id
    data = await get_truck(user_id)
    
    if data["tenaga"] >= 100:
        return await message.reply("💪 Tenagamu masih full, gak perlu istirahat!")
    
    biaya_makan = 1500
    if data["koin"] < biaya_makan:
        return await message.reply(f"❌ Koin gak cukup buat beli kopi & makan di Rest Area (Butuh `Rp{biaya_makan}`)!")

    msg = await message.reply("☕ **Masuk ke Rest Area...**\nSedang makan siang dan rebahan sejenak.")
    await asyncio.sleep(4)
    
    data["koin"] -= biaya_makan
    data["tenaga"] = 100
    await save_truck(user_id, data, client)
    await msg.edit("🔋 **Tenaga Pulih!**\nSekarang kamu segar kembali dan siap narik lagi. (Biaya: `Rp1.500`) ")

@PY.UBOT("garasi")
async def garasi_cmd(client, message):
    user_id = message.from_user.id
    data = await get_truck(user_id)
    await message.reply(
        f"🏢 **GARASI TRUK**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `Rp{data['koin']:,}`\n"
        f"⚡ **Tenaga:** `{data['tenaga']}%`\n"
        f"🚛 **Truk:** `{data['truk']}`\n"
        f"📊 **Total Rit:** `{data['rit']}`\n"
        f"━━━━━━━━━━━━━━━"
    )

@PY.UBOT("beli_truk")
async def beli_truk_pro(client, message):
    if len(message.command) < 2:
        shop = "🛒 **DEALER TRUK**\n\n"
        for k, v in TRUCK_SHOP.items():
            shop += f"• `{k}` : {v['nama']} (Rp{v['harga']:,})\n"
        return await message.reply(shop + "\nKetik: `.beli_truk [kode]`")
    
    kode = message.command[1].lower()
    if kode not in TRUCK_SHOP: return
    
    user_id = message.from_user.id
    data = await get_truck(user_id)
    item = TRUCK_SHOP[kode]
    
    if data["koin"] < item["harga"]:
        return await message.reply(f"❌ Koin kurang `Rp{item['harga'] - data['koin']:,}`")
        
    data["koin"] -= item["harga"]
    data["truk"] = item["nama"]
    await save_truck(user_id, data, client)
    await message.reply(f"🎉 **Selamat!** Sekarang armada kamu adalah **{item['nama']}**.")