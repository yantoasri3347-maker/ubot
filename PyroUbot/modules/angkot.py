import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴀɴɢᴋᴏᴛ"
__HELP__ = """
<blockquote><b>🚐 Angkot Simulator: Raja Jalanan

Perintah:
<code>{0}narik_angkot</code>
- Narik penumpang keliling trayek (Butuh bensin & tenaga).

<code>{0}ngetem</code>
- Berhenti di perempatan buat nunggu penumpang (Hemat bensin).

<code>{0}setor</code>
- Setor hasil tarikan ke juragan (Dapet Koin).

<code>{0}modifikasi</code>
- Beli variasi (Stiker, Audio, Velg Racing) buat nambah tarif.

<code>{0}bengkel</code>
- Isi bensin, servis mesin, atau cuci angkot.

<code>{0}pool</code>
- Cek status angkot, koin, dan koleksi modif.</b></blockquote>
"""

# --- DATABASE ANGKOT ---
async def get_angkot(user_id):
    data = await get_vars(user_id, "ANGKOT_DATA")
    if not data:
        return {
            "koin": 1000, "kantong": 0, "bensin": 100, 
            "tenaga": 100, "modif": [], "kondisi": 100
        }
    return data

async def save_angkot(user_id, data, client):
    await set_vars(user_id, "ANGKOT_DATA", data)
    players = await get_vars(client.me.id, "ANGKOT_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "ANGKOT_PLAYERS", players)

# Daftar Modifikasi (Nambah Tarif per Penumpang)
UPGRADES = {
    "audio": {"nama": "Audio Jedag-Jedug 🔊", "harga": 5000, "bonus": 1000},
    "stiker": {"nama": "Stiker Kaca 'Doa Ibu' ✨", "harga": 2000, "bonus": 500},
    "velg": {"nama": "Velg Racing Celong 🏎️", "harga": 8000, "bonus": 2000},
    "ceper": {"nama": "Modif Ceper Kandas 🛠️", "harga": 10000, "bonus": 3000},
}

@PY.UBOT("narik_angkot")
async def narik_angkot(client, message):
    user_id = message.from_user.id
    data = await get_angkot(user_id)
    
    if data["bensin"] < 20: return await message.reply("⛽ Bensin tiris, Bang! Isi dulu di `.bengkel`.")
    if data["tenaga"] < 20: return await message.reply("💤 Supir udah loyo, istirahat dulu.")

    trayek = random.choice(["Pasar Baru - Terminal", "Stasiun - Kampus", "Pinggiran Kota", "Pusat Grosir"])
    msg = await message.reply(f"🚐 **Angkot berangkat ke trayek {trayek}...**")
    await asyncio.sleep(3)
    
    # Hitung Bonus Modif
    bonus_total = sum(v["bonus"] for k, v in UPGRADES.items() if v["nama"] in data["modif"])
    
    duit_dapet = random.randint(3000, 10000) + bonus_total
    data["kantong"] += duit_dapet
    data["bensin"] -= 15
    data["tenaga"] -= 15
    data["kondisi"] -= 5
    
    await save_angkot(user_id, data, client)
    await msg.edit(
        f"✅ **Putaran Selesai!**\n"
        f"📍 Trayek: `{trayek}`\n"
        f"💰 Dapet Duit: `Rp{duit_dapet:,}`\n"
        f"🚐 Sisa Bensin: `{data['bensin']}%`"
    )

@PY.UBOT("ngetem")
async def ngetem_angkot(client, message):
    user_id = message.from_user.id
    data = await get_angkot(user_id)
    
    msg = await message.reply("🚦 **Ngetem di perempatan... 'Ayo neng, kosong bangku depan!'**")
    await asyncio.sleep(4)
    
    duit = random.randint(2000, 5000)
    data["kantong"] += duit
    data["tenaga"] -= 5 # Ngetem cuma ngurangin dikit tenaga
    
    await save_angkot(user_id, data, client)
    await msg.edit(f" penumpang naik! 💰 Dapet tambahan: `Rp{duit:,}`")

@PY.UBOT("setor")
async def setor_angkot(client, message):
    user_id = message.from_user.id
    data = await get_angkot(user_id)
    
    if data["kantong"] <= 0: return await message.reply("Belum ada duit di kantong, narik dulu sana!")
    
    duit = data["kantong"]
    data["koin"] += duit
    data["kantong"] = 0
    
    await save_angkot(user_id, data, client)
    await message.reply(f"💸 **Setor Sukses!** `Rp{duit:,}` masuk ke saldo koin kamu.")

@PY.UBOT("modifikasi")
async def modif_angkot(client, message):
    if len(message.command) < 2:
        txt = "🏪 **TOKO VARIASI ANGKOT**\n\n"
        for k, v in UPGRADES.items():
            txt += f"• `{k}` : {v['nama']} (Rp{v['harga']:,})\n"
        return await message.reply(txt + "\nKetik: `.modifikasi [kode]`")
    
    kode = message.command[1].lower()
    if kode not in UPGRADES: return
    
    data = await get_angkot(message.from_user.id)
    item = UPGRADES[kode]
    
    if item["nama"] in data["modif"]: return await message.reply("Udah kepasang, Bang!")
    if data["koin"] < item["harga"]: return await message.reply("Duit setoran kurang!")
    
    data["koin"] -= item["harga"]
    data["modif"].append(item["nama"])
    await save_angkot(message.from_user.id, data, client)
    await message.reply(f"🔥 **Mbois!** Angkot kamu sekarang pake **{item['nama']}**.")

@PY.UBOT("pool")
async def pool_angkot(client, message):
    user_id = message.from_user.id
    data = await get_angkot(user_id)
    modif_list = ", ".join(data["modif"]) if data["modif"] else "-"
    
    await message.reply(
        f"🚐 **POOL ANGKOT INDO**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `Rp{data['koin']:,}`\n"
        f"💵 **Kantong:** `Rp{data['kantong']:,}`\n"
        f"⛽ **Bensin:** `{data['bensin']}%`\n"
        f"⚡ **Tenaga:** `{data['tenaga']}%`\n"
        f"🛠️ **Kondisi:** `{data['kondisi']}%`\n"
        f"✨ **Modif:** `{modif_list}`\n"
        f"━━━━━━━━━━━━━━━"
    )

@PY.UBOT("bengkel")
async def bengkel_angkot(client, message):
    user_id = message.from_user.id
    data = await get_angkot(user_id)
    
    # Opsi sederhana: Langsung full semua bayar 2000
    if data["koin"] < 2000: return await message.reply("Gak cukup duit buat ke bengkel!")
    
    data["koin"] -= 2000
    data["bensin"] = 100
    data["tenaga"] = 100
    data["kondisi"] = 100
    
    await save_angkot(user_id, data, client)
    await message.reply("🛠️ **Servis Selesai!** Bensin full, mesin seger, supir fit lagi. (Biaya: `Rp2.000`) ")