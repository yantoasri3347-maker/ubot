import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴋᴇʙᴜɴ"
__HELP__ = """
<blockquote><b>🚜 Game Farm Tycoon

Perintah:
<code>{0}tanam</code>
- Menanam bibit di ladang kamu.

<code>{0}panen</code>
- Memanen hasil kebun yang sudah matang.

<code>{0}ladang</code>
- Cek status tanaman, koin, dan level tani.

<code>{0}pasar</code>
- Jual hasil panen untuk mendapatkan koin.

<code>{0}top_tani</code>
- Leaderboard petani terkaya.</b></blockquote>
"""

# --- DATABASE KEBUN ---
async def get_farm(user_id):
    data = await get_vars(user_id, "FARM_DATA")
    if not data:
        return {"koin": 1000, "tanaman": None, "status": "Kosong", "hasil": 0}
    return data

async def save_farm(user_id, data, client):
    await set_vars(user_id, "FARM_DATA", data)
    players = await get_vars(client.me.id, "FARM_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "FARM_PLAYERS", players)

# Daftar Bibit
PLANTS = {
    "padi": {"nama": "Padi", "harga_bibit": 500, "jual": 2500},
    "jagung": {"nama": "Jagung", "harga_bibit": 1000, "jual": 5000},
    "semangka": {"nama": "Semangka", "harga_bibit": 5000, "jual": 25000},
}

@PY.UBOT("tanam")
async def tanam_cmd(client, message):
    user_id = message.from_user.id
    data = await get_farm(user_id)
    
    if data["status"] == "Menanam":
        return await message.reply("❌ Ladangmu masih terisi! Tunggu sampai `.panen` dulu.")
    
    if len(message.command) < 2:
        list_bibit = "🌱 **PILIH BIBIT:**\n"
        for k, v in PLANTS.items():
            list_bibit += f"• `{k}` - Rp{v['harga_bibit']:,}\n"
        return await message.reply(list_bibit + "\nKetik: `.tanam padi` (contoh)")

    pilihan = message.command[1].lower()
    if pilihan not in PLANTS:
        return await message.reply("❌ Bibit tidak ada di toko!")
    
    bibit = PLANTS[pilihan]
    if data["koin"] < bibit["harga_bibit"]:
        return await message.reply("❌ Koin tidak cukup buat beli bibit!")

    data["koin"] -= bibit["harga_bibit"]
    data["tanaman"] = bibit["nama"]
    data["status"] = "Menanam"
    
    await save_farm(user_id, data, client)
    await message.reply(f"👨‍🌾 **Berhasil!** Kamu menanam **{bibit['nama']}**. Tunggu sebentar lagi untuk panen!")

@PY.UBOT("panen")
async def panen_cmd(client, message):
    user_id = message.from_user.id
    data = await get_farm(user_id)
    
    if data["status"] != "Menanam":
        return await message.reply("❌ Gak ada yang bisa dipanen. Tanam dulu gih!")

    msg = await message.reply("🚜 **Sedang memanen hasil kebun...**")
    await asyncio.sleep(3)
    
    # Cari harga jualnya
    nama_tanam = data["tanaman"]
    harga_jual = 0
    for k, v in PLANTS.items():
        if v["nama"] == nama_tanam:
            harga_jual = v["jual"]

    data["hasil"] += harga_jual
    data["status"] = "Kosong"
    data["tanaman"] = None
    
    await save_farm(user_id, data, client)
    await msg.edit(f"🧺 **Panen Sukses!** Kamu mendapatkan hasil panen senilai `Rp{harga_jual:,}`. Ketik `.pasar` untuk menjualnya!")

@PY.UBOT("pasar")
async def pasar_cmd(client, message):
    user_id = message.from_user.id
    data = await get_farm(user_id)
    
    if data["hasil"] <= 0:
        return await message.reply("❌ Kamu gak punya hasil panen buat dijual.")
    
    cuan = data["hasil"]
    data["koin"] += cuan
    data["hasil"] = 0
    
    await save_farm(user_id, data, client)
    await message.reply(f"💰 **Terjual!** Kamu mendapatkan `Rp{cuan:,}` dari tengkulak.")

@PY.UBOT("ladang")
async def ladang_cmd(client, message):
    user_id = message.from_user.id
    data = await get_farm(user_id)
    
    res = (
        f"🏡 **MY FARM STATUS**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 **Koin:** `Rp{data['koin']:,}`\n"
        f"🌱 **Ladang:** `{data['tanaman'] or 'Kosong'}`\n"
        f"📦 **Hasil di Gudang:** `Rp{data['hasil']:,}`\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.reply(res)

@PY.UBOT("top_tani")
async def top_tani_cmd(client, message):
    msg = await message.reply("📊 **Mencari Petani Sukses...**")
    user_ids = await get_vars(client.me.id, "FARM_PLAYERS") or []
    
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "FARM_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except: name = f"Farmer-{uid}"
            lb.append({"name": name, "koin": data.get("koin", 0)})

    lb.sort(key=lambda x: x["koin"], reverse=True)
    res = "🏆 **TOP 10 PETANI TERKAYA**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `Rp{u['koin']:,}`\n"
    await msg.edit(res)