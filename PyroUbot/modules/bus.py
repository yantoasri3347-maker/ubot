import random
import asyncio
from PyroUbot import *

__MODULE__ = "ʙᴜs"
__HELP__ = """
<blockquote><b>🚌 BUS SIMULATOR INDONESIA (COMPLETE)

🎮 UTAMA:
<code>{0}ngeline</code> - Tarik penumpang (Aman).
<code>{0}ngeblong</code> - Lawan arus (Resiko Tinggi, Hasil Gede).
<code>{0}cari_sewa</code> - Cari penumpang sampingan di jalan.

🛠️ PERAWATAN:
<code>{0}isi_bensin</code> - Isi solar di SPBU.
<code>{0}istirahat_bus</code> - Supir rehat di Rest Area.
<code>{0}cuci_bus</code> - Bersihkan bus agar Kinclong.

🏪 TOKO & MODIF:
<code>{0}toko_variasi</code> - Beli aksesoris (Strobo/Basuri).
<code>{0}beli_bus</code> - Upgrade armada bus.
<code>{0}garasi_bus</code> - Cek koin, solar, tenaga, & modif.</b></blockquote>
"""

# --- DATABASE SYSTEM ---
async def get_bus_data(user_id):
    data = await get_vars(user_id, "BUS_DATA")
    if not data:
        return {
            "koin": 5000, "bus": "Bus Mini", "penumpang": 0, 
            "tenaga": 100, "bensin": 100, "aksesoris": [], "kebersihan": 100
        }
    # Safety checks for old data
    keys = ["tenaga", "bensin", "aksesoris", "kebersihan"]
    for key in keys:
        if key not in data:
            data[key] = 100 if key != "aksesoris" else []
    return data

async def save_bus_data(user_id, data, client):
    await set_vars(user_id, "BUS_DATA", data)
    players = await get_vars(client.me.id, "BUS_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "BUS_PLAYERS", players)

# --- KONFIGURASI GAME ---
BUS_SHOP = {
    "jetbus": {"nama": "Jetbus 3+", "harga": 30000, "bonus": 8000},
    "sr2": {"nama": "SR2 XHD Prime", "harga": 85000, "bonus": 18000},
    "dd": {"nama": "Double Decker v3", "harga": 300000, "bonus": 60000},
}

VARIASI = {
    "strobo": {"nama": "Lampu Strobo ⚡", "harga": 15000, "bonus": 5000},
    "boneka": {"nama": "Boneka Dashboard 🧸", "harga": 5000, "bonus": 1500},
    "basuri": {"nama": "Klakson Basuri V3 🔊", "harga": 25000, "bonus": 10000},
}

# --- COMMANDS ---

@PY.UBOT("ngeline")
async def ngeline_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    
    if data["tenaga"] < 20 or data["bensin"] < 15:
        return await message.reply("⚠️ **Mogok!** Solar habis atau supir tepar. Cek `.garasi_bus`")

    rute = random.choice(["Jakarta-Solo", "Surabaya-Bali", "Medan-Palembang", "Bandung-Jogja"])
    is_mudik = random.randint(1, 100) <= 20
    multiplier = 3 if is_mudik else 1
    
    msg = await message.reply(f"🚌 **Bus {data['bus']} berangkat ke {rute}...**")
    await asyncio.sleep(3)
    
    # Hitung Bonus
    total_bonus = sum(v["bonus"] for k, v in VARIASI.items() if v["nama"] in data["aksesoris"])
    bonus_kinclong = 5000 if data["kebersihan"] > 80 else 0
    
    ongkos_dasar = random.randint(15000, 35000)
    total_setoran = (ongkos_dasar * multiplier) + total_bonus + bonus_kinclong
    
    # Update Data
    data["koin"] += total_setoran
    data["tenaga"] -= 20
    data["bensin"] -= 15
    data["kebersihan"] -= random.randint(5, 15)
    
    await save_bus_data(user_id, data, client)
    
    res = f"🏁 **Tiba di Terminal {rute.split('-')[1]}!**\n"
    res += f"💰 Setoran: `Rp{total_setoran:,}`\n"
    if is_mudik: res += "🌙 **MUDIK BONUS 3X!**\n"
    if bonus_kinclong: res += "🧼 **Bonus Kinclong Terpakai!**\n"
    res += f"⚡ Tenaga: `{data['tenaga']}%` | ⛽ Solar: `{data['bensin']}%`"
    await msg.edit(res)

@PY.UBOT("ngeblong")
async def ngeblong_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    if data["tenaga"] < 30: return await message.reply("Supir terlalu lelah untuk ngeblong!")
    
    msg = await message.reply("🚀 **AKSI NGEBLONG! Bus membelah kemacetan lawan arus...**")
    await asyncio.sleep(2)
    
    nasib = random.randint(1, 100)
    if nasib <= 25: # Celaka
        rugi = random.randint(15000, 30000)
        data["koin"] = max(0, data["koin"] - rugi)
        data["tenaga"] -= 40
        await save_bus_data(user_id, data, client)
        return await msg.edit(f"💥 **KECELAKAAN!** Bus ringsek menabrak pembatas jalan.\n💸 Rugi: `Rp{rugi:,}`")
    
    cuan = random.randint(50000, 100000)
    data["koin"] += cuan
    data["tenaga"] -= 30
    await save_bus_data(user_id, data, client)
    await msg.edit(f"🔥 **GILA!** Ngeblong sukses sampai tujuan sangat cepat.\n💰 Uang Masuk: `Rp{cuan:,}`")

@PY.UBOT("cuci_bus")
async def cuci_bus_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    if data["koin"] < 1000: return await message.reply("Koin gak cukup buat cuci bus!")
    data["koin"] -= 1000
    data["kebersihan"] = 100
    await save_bus_data(user_id, data, client)
    await message.reply("✨ **Bus Kinclong!** Bonus setoran kembali aktif.")

@PY.UBOT("cari_sewa")
async def cari_sewa_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    msg = await message.reply("🔍 **Mencari penumpang tambahan...**")
    await asyncio.sleep(2)
    tips = random.randint(2000, 6000)
    data["koin"] += tips
    await save_bus_data(user_id, data, client)
    await msg.edit(f"🎒 **Dapet Sewa!** Tambahan koin: `Rp{tips:,}`")

@PY.UBOT("toko_variasi")
async def toko_variasi_cmd(client, message):
    data = await get_bus_data(message.from_user.id)
    txt = "🏪 **TOKO VARIASI BUS**\n\n"
    for k, v in VARIASI.items():
        status = "✅ Dimiliki" if v["nama"] in data["aksesoris"] else f"Rp{v['harga']:,}"
        txt += f"• `{k}` : {v['nama']} ({status})\n"
    await message.reply(txt + "\nKetik: `.beli_variasi [kode]`")

@PY.UBOT("beli_variasi")
async def beli_variasi_cmd(client, message):
    if len(message.command) < 2: return
    kode = message.command[1].lower()
    if kode not in VARIASI: return
    data = await get_bus_data(message.from_user.id)
    item = VARIASI[kode]
    if item["nama"] in data["aksesoris"]: return await message.reply("Sudah punya!")
    if data["koin"] < item["harga"]: return await message.reply("Koin kurang!")
    data["koin"] -= item["harga"]
    data["aksesoris"].append(item["nama"])
    await save_bus_data(message.from_user.id, data, client)
    await message.reply(f"✨ **Terpasang:** {item['nama']}")

@PY.UBOT("garasi_bus")
async def garasi_bus_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    aks = ", ".join(data["aksesoris"]) if data["aksesoris"] else "-"
    await message.reply(
        f"🏢 **GARASI BUS {message.from_user.first_name.upper()}**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `Rp{data['koin']:,}`\n"
        f"🚌 **Bus:** `{data['bus']}`\n"
        f"🧼 **Kebersihan:** `{data['kebersihan']}%`\n"
        f"⚡ **Tenaga:** `{data['tenaga']}%` | ⛽ **Solar:** `{data['bensin']}%` \n"
        f"✨ **Modif:** `{aks}`\n"
        f"━━━━━━━━━━━━━━━"
    )

@PY.UBOT("isi_bensin")
async def isi_bensin_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    if data["koin"] < 2500: return await message.reply("Koin gak cukup!")
    data["koin"] -= 2500
    data["bensin"] = 100
    await save_bus_data(user_id, data, client)
    await message.reply("⛽ **Solar Full!** Bus siap ngeline.")

@PY.UBOT("istirahat_bus")
async def istirahat_cmd(client, message):
    user_id = message.from_user.id
    data = await get_bus_data(user_id)
    data["tenaga"] = 100
    await save_bus_data(user_id, data, client)
    await message.reply("☕ **Rest Area:** Supir sudah fit kembali!")

@PY.UBOT("beli_bus")
async def beli_bus_cmd(client, message):
    if len(message.command) < 2:
        shop = "🛒 **DEALER BUS**\n\n"
        for k, v in BUS_SHOP.items(): shop += f"• `{k}` : {v['nama']} (Rp{v['harga']:,})\n"
        return await message.reply(shop)
    kode = message.command[1].lower()
    if kode not in BUS_SHOP: return
    data = await get_bus_data(message.from_user.id)
    item = BUS_SHOP[kode]
    if data["koin"] < item["harga"]: return await message.reply("Koin kurang!")
    data["koin"] -= item["harga"]
    data["bus"] = item["nama"]
    await save_bus_data(message.from_user.id, data, client)
    await message.reply(f"🎉 **Baru!** Kamu punya {item['nama']}")